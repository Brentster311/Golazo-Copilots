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


def test_unusual_settings_persist_and_unusual_alerts_are_deterministic(service):
    planner, _, fidelity = service
    planner.link_account("Fidelity", "Fidelity Brokerage", "fid-unusual")

    fidelity.set_transactions(
        "fid-unusual",
        [
            _record("u-001", "Electronics Hub", 100.0, 30),
            _record("u-002", "Electronics Hub", 110.0, 25),
            _record("u-003", "Electronics Hub", 90.0, 20),
            _record("u-004", "Electronics Hub", 120.0, 15),
            _record("u-005", "Electronics Hub", 550.0, 1),
        ],
    )

    planner.update_unusual_settings(minimum_amount=80.0, sensitivity_factor=1.0, min_samples=3)
    settings = planner.get_unusual_settings()

    assert settings["minimum_amount"] == 80.0, "Expected persisted minimum_amount to match latest configured value."
    assert settings["sensitivity_factor"] == 1.0, "Expected persisted sensitivity_factor to match latest configured value."
    assert settings["min_samples"] == 3, "Expected persisted min_samples to match latest configured value."

    planner.run_sync(days=90)
    first = planner.get_unusual_transaction_alerts(days=90)
    second = planner.get_unusual_transaction_alerts(days=90)

    assert first == second, "Expected deterministic unusual alert payload/order across repeated reads."
    assert first, "Expected at least one unusual alert for clear outlier transaction."
    alert = first[0]
    assert alert["provider_transaction_id"] == "u-005", "Expected outlier transaction id to be flagged as unusual."
    assert alert["severity"] in {"medium", "high"}, "Expected unusual alert to include severity classification."
    assert "next_step" in alert, "Expected unusual alert to include actionable next_step field."


def test_goal_creation_contributions_and_drift_alerts(service):
    planner, _, _ = service

    target_date = date.today() + timedelta(days=120)
    goal_id = planner.create_savings_goal(
        name="Emergency Fund",
        target_amount=3000.0,
        target_date=target_date,
        monthly_contribution=150.0,
    )

    planner.add_goal_contribution(goal_id=goal_id, amount=50.0, contributed_on=date.today() - timedelta(days=40))

    alerts = planner.get_goal_drift_alerts(as_of=date.today() + timedelta(days=45))
    assert alerts, "Expected goal drift alert with deficit details for behind-schedule goal."

    drift = alerts[0]
    assert drift["goal_id"] == goal_id, "Expected drift alert to reference the created goal id."
    assert drift["expected_to_date"] > drift["actual_to_date"], "Expected goal drift to show expected progress ahead of actual."
    assert drift["deficit"] > 0, "Expected positive deficit for behind-schedule goal."
    assert "next_step" in drift, "Expected goal drift alert to include actionable next_step field."


def test_invalid_unusual_settings_and_goal_definitions_raise_validation_error(service):
    planner, _, _ = service

    with pytest.raises(PlannerValidationError):
        planner.update_unusual_settings(minimum_amount=-1.0, sensitivity_factor=1.2, min_samples=3)

    with pytest.raises(PlannerValidationError):
        planner.update_unusual_settings(minimum_amount=50.0, sensitivity_factor=0.0, min_samples=3)

    with pytest.raises(PlannerValidationError):
        planner.create_savings_goal(
            name="",
            target_amount=500.0,
            target_date=date.today() + timedelta(days=30),
            monthly_contribution=50.0,
        )

    with pytest.raises(PlannerValidationError):
        planner.create_savings_goal(
            name="Vacation",
            target_amount=500.0,
            target_date=date.today() - timedelta(days=1),
            monthly_contribution=50.0,
        )
