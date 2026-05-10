from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from finance_planner.connectors import FixtureConnector, TransactionRecord
from finance_planner.planner import FinancialPlannerService, PlannerValidationError


def _record(txn_id: str, merchant: str, amount: float, days_ago: int, direction: str = "debit") -> TransactionRecord:
    posted_at = datetime.now(tz=UTC) - timedelta(days=days_ago)
    return TransactionRecord(
        provider_transaction_id=txn_id,
        posted_at=posted_at,
        amount=amount,
        merchant=merchant,
        direction=direction,
    )


@pytest.fixture
def service(tmp_path):
    db_path = tmp_path / "planner.db"
    key_path = tmp_path / "planner.key"

    first_tech = FixtureConnector("First Tech Federal Credit Union")
    fidelity = FixtureConnector("Fidelity")

    first_tech.set_transactions(
        "ft-ok",
        [
            _record("ft-001", "Coffee Hut", 12.25, 5),
            _record("ft-002", "Grocery Mart", 95.00, 2),
        ],
    )
    fidelity.set_transactions(
        "fid-ok",
        [
            _record("fid-001", "Payroll Deposit", 3000.00, 7, direction="credit"),
            _record("fid-002", "Rent Payment", 1200.00, 3),
        ],
    )
    fidelity.set_transactions(
        "fid-overspend",
        [
            _record("fid-101", "Grocery Mart", 80.00, 3),
            _record("fid-102", "Fuel Station", 45.00, 2),
            _record("fid-103", "Utility Power", 120.00, 4),
            _record("fid-104", "Streaming Plus", 30.00, 1),
            _record("fid-105", "Rent Payment", 1200.00, 6),
        ],
    )

    planner = FinancialPlannerService(
        db_path=db_path,
        key_path=key_path,
        connectors={
            "First Tech Federal Credit Union": first_tech,
            "Fidelity": fidelity,
        },
    )
    return planner, first_tech, fidelity


def test_links_and_syncs_90_day_window_for_both_institutions(service):
    planner, _, _ = service

    planner.link_account("First Tech Federal Credit Union", "First Tech Checking", "ft-ok")
    planner.link_account("Fidelity", "Fidelity Brokerage", "fid-ok")

    report = planner.run_sync(days=90)

    assert report["overall_status"] == "success", "Expected both institution syncs to succeed in 90-day window."
    statuses = {item["institution"]: item["status"] for item in report["account_results"]}
    assert statuses["First Tech Federal Credit Union"] == "success", "Expected First Tech sync success."
    assert statuses["Fidelity"] == "success", "Expected Fidelity sync success."

    transactions = planner.list_transactions()
    assert len(transactions) >= 4, "Expected transactions from both linked institutions to be imported."


def test_transactions_are_normalized_and_encrypted_at_rest(service):
    planner, _, _ = service
    planner.link_account("First Tech Federal Credit Union", "First Tech Checking", "ft-ok")

    planner.run_sync(days=90)
    transactions = planner.list_transactions()
    assert transactions, "Expected imported transactions after successful sync."

    first = transactions[0]
    required_fields = {"posted_on", "amount", "merchant", "account", "direction"}
    assert required_fields.issubset(first.keys()), "Transaction schema normalization failed: required field missing."

    encrypted_payload = planner.get_raw_encrypted_payload(first["id"])
    assert b"Coffee Hut" not in encrypted_payload, "Encryption-at-rest check failed: sensitive merchant text found in raw payload."


def test_user_categorization_is_reused_for_future_matching_transactions(service):
    planner, first_tech, _ = service
    planner.link_account("First Tech Federal Credit Union", "First Tech Checking", "ft-ok")

    planner.run_sync(days=90)
    existing = next(item for item in planner.list_transactions() if item["provider_transaction_id"] == "ft-001")
    planner.confirm_category(existing["id"], "Dining")

    first_tech.append_transaction("ft-ok", _record("ft-003", "Coffee Hut", 14.10, 1))
    planner.run_sync(days=90)

    latest = next(item for item in planner.list_transactions() if item["provider_transaction_id"] == "ft-003")
    assert latest["category"] == "Dining", "Categorization learning failed: expected confirmed category to be reused."
    assert latest["category_source"] == "rule", "Expected learned category source to be recorded as rule."


def test_budget_caps_raise_overspend_warning_for_monthly_categories(service):
    planner, _, _ = service
    planner.link_account("Fidelity", "Fidelity Brokerage", "fid-overspend")

    planner.set_budget("Groceries", 50.0)
    planner.set_budget("Housing", 1500.0)
    planner.set_budget("Transportation", 100.0)
    planner.set_budget("Utilities", 100.0)
    planner.set_budget("Entertainment", 20.0)

    planner.run_sync(days=90)

    today = date.today()
    alerts = planner.get_budget_alerts(today.year, today.month)
    groceries = next((alert for alert in alerts if alert["category"] == "Groceries"), None)
    assert groceries is not None, "Budget alert generation failed: expected Groceries overspend alert."
    assert groceries["spent"] > groceries["cap"], "Expected Groceries spent amount to exceed cap for alert generation." 


def test_sync_failure_returns_actionable_error_and_retry_is_duplicate_safe(service):
    planner, _, _ = service
    failed_account_id = planner.link_account("First Tech Federal Credit Union", "First Tech Checking", "fail:connectivity")
    planner.link_account("Fidelity", "Fidelity Brokerage", "fid-ok")

    first_report = planner.run_sync(days=90)
    failed = next(item for item in first_report["account_results"] if item["status"] == "failed")
    assert failed["error_category"] == "connectivity_error", "Expected actionable connectivity error category."
    assert "retry" in failed["actionable_message"].lower(), "Expected actionable retry guidance in sync failure response."

    before_retry_count = len(planner.list_transactions())
    planner.update_account_access_token(failed_account_id, "ft-ok")

    second_report = planner.run_sync(days=90)
    assert second_report["overall_status"] == "success", "Expected successful sync after clearing failure condition and retrying."

    after_retry_count = len(planner.list_transactions())
    third_report = planner.run_sync(days=90)
    assert third_report["duplicates_skipped"] > 0, "Expected duplicate detection on repeated sync runs."
    assert len(planner.list_transactions()) == after_retry_count, "Retry safety failed: duplicate transaction records were introduced."
    assert after_retry_count >= before_retry_count, "Retry should not lose previously imported transactions."


def test_validation_errors_for_invalid_budget_and_unknown_transaction(service):
    planner, _, _ = service

    with pytest.raises(PlannerValidationError):
        planner.set_budget("Groceries", -1.0)

    with pytest.raises(PlannerValidationError):
        planner.confirm_category(99999, "Dining")
