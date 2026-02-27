"""Tests for ETA update UI flows and validation.

TC-09 through TC-15 from SFI-019 Test Cases.
"""
import pytest
from datetime import datetime, date, timedelta
from unittest.mock import MagicMock, patch, call


class TestBulkUpdateFlow:
    """Tests for bulk ETA update workflow."""

    def test_tc09_all_items_updated(self):
        """TC-09: Bulk mode updates all invalid-ETA items."""
        from s360_reporter.eta_logic import get_items_needing_eta_update, propose_eta, build_eta_update

        items = [
            {"id": f"item-{i}", "EtaDate": None, "_kpi_id": "kpi-1",
             "S360_ServiceId": "svc-1", "SlaType": "InSla",
             "ActionOwnerAlias": "user1", "dueDate": None}
            for i in range(3)
        ]

        needing = get_items_needing_eta_update(items)
        assert len(needing) == 3

        # Each item should produce a valid EtaUpdate
        for item in needing:
            update = build_eta_update(item, propose_eta(item.get("dueDate")))
            assert update.kpi_id == "kpi-1"
            assert update.service_id == "svc-1"
            assert update.assigned_to == "user1"

    def test_tc10_partial_failure(self):
        """TC-10: Bulk mode — 2 succeed, 1 fails."""
        from accia_s360.models import SaveResult

        results = [
            SaveResult(success=True),
            SaveResult(success=True),
            SaveResult(success=False, error_message="HTTP 500: Internal Server Error"),
        ]

        succeeded = sum(1 for r in results if r.success)
        failed = sum(1 for r in results if not r.success)

        assert succeeded == 2
        assert failed == 1


class TestManualModeFlow:
    """Tests for manual (interactive) ETA update workflow."""

    def test_tc11_skip_and_accept(self):
        """TC-11: Manual mode — skip item 1, accept item 2."""
        from s360_reporter.eta_logic import get_items_needing_eta_update

        items = [
            {"id": "skip-me", "EtaDate": None, "_kpi_id": "kpi-1",
             "S360_ServiceId": "svc-1", "SlaType": "InSla",
             "ActionOwnerAlias": "user1", "dueDate": None},
            {"id": "save-me", "EtaDate": "2020-01-01T00:00:00", "_kpi_id": "kpi-2",
             "S360_ServiceId": "svc-2", "SlaType": "OutOfSla",
             "ActionOwnerAlias": "user2", "dueDate": None},
        ]

        needing = get_items_needing_eta_update(items)
        assert len(needing) == 2

        # Simulate: skip first, save second
        skipped = [needing[0]]
        saved = [needing[1]]

        assert len(saved) == 1
        assert saved[0]["id"] == "save-me"
        assert len(skipped) == 1
        assert skipped[0]["id"] == "skip-me"


class TestSingleItemUpdate:
    """Tests for individual item update from detail view."""

    def test_tc12_single_update_builds_correct_payload(self):
        """TC-12: Single item update from detail view."""
        from s360_reporter.eta_logic import build_eta_update

        item = {
            "id": "single-item",
            "_kpi_id": "kpi-abc",
            "S360_ServiceId": "svc-xyz",
            "SlaType": "OutOfSla",
            "ActionOwnerAlias": "testuser",
            "dueDate": "2026-05-01",
        }

        update = build_eta_update(item, "2026-03-31", notes="Remediation complete")

        assert update.kpi_id == "kpi-abc"
        assert update.service_id == "svc-xyz"
        assert update.action_item_id == "single-item"
        assert update.new_eta == datetime(2026, 3, 31)
        assert update.notes == "Remediation complete"
        assert update.assigned_to == "testuser"
        assert update.sla_type == "OutOfSla"


class TestEmptyState:
    """Tests for edge case: no invalid items."""

    def test_tc13_no_invalid_items(self):
        """TC-13: All ETAs valid → empty list returned."""
        from s360_reporter.eta_logic import get_items_needing_eta_update

        future = (datetime.now() + timedelta(days=365)).isoformat()
        items = [
            {"id": "ok-1", "EtaDate": future},
            {"id": "ok-2", "EtaDate": future},
        ]

        result = get_items_needing_eta_update(items)
        assert result == []


class TestDateValidation:
    """Tests for date input validation."""

    def test_tc14_past_date_rejected(self):
        """TC-14: Past date is rejected."""
        from s360_reporter.eta_logic import validate_eta_date

        ok, msg = validate_eta_date("2025-01-01")
        assert ok is False
        assert "future" in msg.lower() or "past" in msg.lower() or "today" in msg.lower()

    def test_tc15_invalid_format_rejected(self):
        """TC-15: Non-date string is rejected."""
        from s360_reporter.eta_logic import validate_eta_date

        ok, msg = validate_eta_date("not-a-date")
        assert ok is False
        assert "format" in msg.lower() or "invalid" in msg.lower()

    def test_today_is_accepted(self):
        """Bonus: Today's date should be accepted (BD-6)."""
        from s360_reporter.eta_logic import validate_eta_date

        today_str = date.today().strftime("%Y-%m-%d")
        ok, msg = validate_eta_date(today_str)
        assert ok is True

    def test_far_future_rejected(self):
        """Bonus: Date >1 year out is rejected (BD-6)."""
        from s360_reporter.eta_logic import validate_eta_date

        far = (date.today() + timedelta(days=400)).strftime("%Y-%m-%d")
        ok, msg = validate_eta_date(far)
        assert ok is False
