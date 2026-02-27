"""Tests for ETA logic — propose_eta and get_items_needing_eta_update.

TC-01 through TC-05 from SFI-019 Test Cases.
"""
import pytest
from datetime import date, datetime
from unittest.mock import patch


class TestProposeEta:
    """Tests for propose_eta() date calculation."""

    def test_tc01_basic_no_due_date(self):
        """TC-01: No due date, today=2026-02-06 → end of Feb."""
        from s360_reporter.eta_logic import propose_eta

        with patch("s360_reporter.eta_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 2, 6)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = propose_eta(None)

        assert result == "2026-02-28"

    def test_tc02_due_date_in_future(self):
        """TC-02: Due date 2026-04-15 → end of April."""
        from s360_reporter.eta_logic import propose_eta

        with patch("s360_reporter.eta_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 2, 6)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = propose_eta("2026-04-15")

        assert result == "2026-04-30"

    def test_tc03_due_date_in_past(self):
        """TC-03: Due date in past → ignores it, uses 2 weeks from now."""
        from s360_reporter.eta_logic import propose_eta

        with patch("s360_reporter.eta_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 2, 6)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = propose_eta("2025-12-01")

        assert result == "2026-02-28"

    def test_tc04_december_edge_case(self):
        """TC-04: Dec 20 → 2 weeks = Jan 3 → end of Jan 2027."""
        from s360_reporter.eta_logic import propose_eta

        with patch("s360_reporter.eta_logic.date") as mock_date:
            mock_date.today.return_value = date(2026, 12, 20)
            mock_date.side_effect = lambda *a, **kw: date(*a, **kw)
            result = propose_eta(None)

        assert result == "2027-01-31"


class TestGetItemsNeedingEtaUpdate:
    """Tests for get_items_needing_eta_update()."""

    def test_tc05_filters_correctly(self):
        """TC-05: Filters to only invalid-ETA items."""
        from s360_reporter.eta_logic import get_items_needing_eta_update

        future = (datetime.now().replace(year=datetime.now().year + 1)).isoformat()
        items = [
            {"id": "good", "EtaDate": future},
            {"id": "past", "EtaDate": "2020-01-01T00:00:00"},
            {"id": "none", "EtaDate": None},
        ]

        result = get_items_needing_eta_update(items)

        result_ids = [r["id"] for r in result]
        assert "good" not in result_ids
        assert "past" in result_ids
        assert "none" in result_ids
        assert len(result) == 2
