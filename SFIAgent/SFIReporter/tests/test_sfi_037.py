"""Tests for SFI-037: KPI Cost Column feature.

Covers: cost data fetching, row cost computation, formatting, and edge cases.
"""
import pytest
import sfi_reporter.data as data_module


@pytest.fixture(autouse=True)
def _reset_client_singleton():
    """Reset the S360Client singleton before each test."""
    data_module._client_instance = None
    yield
    data_module._client_instance = None


# ---------------------------------------------------------------------------
# AC-1: Cost data fetched during refresh
# ---------------------------------------------------------------------------

class TestFetchKpiCosts:
    """Tests for the fetch_kpi_costs() function."""

    def test_successful_cost_fetch(self, mocker):
        """TC-037-01: Successful cost fetch returns correct map."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        mock_client.query_kpi_costs.return_value = [
            {"KpiId": "kpi-1", "AverageCostInMin": 180.0, "AverageCost": "HalfDay"},
            {"KpiId": "kpi-2", "AverageCostInMin": 1054.0, "AverageCost": "OneDay"},
            {"KpiId": "kpi-3", "AverageCostInMin": 1962.0, "AverageCost": "HalfWeek"},
        ]
        from sfi_reporter.data import fetch_kpi_costs

        result = fetch_kpi_costs(["kpi-1", "kpi-2", "kpi-3"])

        assert result == {"kpi-1": 180.0, "kpi-2": 1054.0, "kpi-3": 1962.0}, \
            "Cost map should contain all 3 KPI IDs with correct minute values"

    def test_partial_cost_data(self, mocker):
        """TC-037-02: Cost API returns partial data — only found KPIs in map."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        mock_client.query_kpi_costs.return_value = [
            {"KpiId": "kpi-1", "AverageCostInMin": 180.0, "AverageCost": "HalfDay"},
        ]
        from sfi_reporter.data import fetch_kpi_costs

        result = fetch_kpi_costs(["kpi-1", "kpi-2", "kpi-3"])

        assert result == {"kpi-1": 180.0}, \
            "Cost map should contain only KPIs with data, missing KPIs absent"
        assert "kpi-2" not in result
        assert "kpi-3" not in result

    def test_cost_api_failure(self, mocker):
        """TC-037-03: Cost API fails entirely — returns empty dict, no exception."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        mock_client.query_kpi_costs.side_effect = Exception("API timeout")
        from sfi_reporter.data import fetch_kpi_costs

        result = fetch_kpi_costs(["kpi-1", "kpi-2"])

        assert result == {}, \
            "Cost fetch failure should return empty dict, not raise"

    def test_empty_kpi_list(self, mocker):
        """TC-037-04: Empty KPI list short-circuits without API call."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        from sfi_reporter.data import fetch_kpi_costs

        result = fetch_kpi_costs([])

        assert result == {}, \
            "Empty KPI list should short-circuit and return empty dict"
        mock_client.query_kpi_costs.assert_not_called()


# ---------------------------------------------------------------------------
# AC-2 through AC-5: Row cost computation
# ---------------------------------------------------------------------------

class TestComputeRowCost:
    """Tests for compute_row_cost() used across all table views."""

    def test_service_row_cost(self):
        """TC-037-05: Service cost = sum(kpi_cost × item_count)."""
        from sfi_reporter.data import compute_row_cost

        items = [
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-2"},
            {"_kpi_id": "kpi-2"},
        ]
        kpi_cost_map = {"kpi-1": 180.0, "kpi-2": 1054.0}

        result = compute_row_cost(items, kpi_cost_map)

        assert result == 180 * 3 + 1054 * 2, \
            "Service cost should be sum of (kpi_cost × item_count) across all KPIs"

    def test_service_no_cost_data(self):
        """TC-037-06: Service with no cost data returns None."""
        from sfi_reporter.data import compute_row_cost

        items = [{"_kpi_id": "kpi-unknown"}]
        kpi_cost_map = {}

        result = compute_row_cost(items, kpi_cost_map)

        assert result is None, \
            "Service with no cost data should return None"

    def test_kpi_row_cost(self):
        """TC-037-07: KPI row cost = kpi_cost × item_count."""
        from sfi_reporter.data import compute_row_cost

        items = [
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
        ]
        kpi_cost_map = {"kpi-1": 180.0}

        result = compute_row_cost(items, kpi_cost_map)

        assert result == 900.0, \
            "KPI row cost should be kpi_cost × item_count"

    def test_program_row_cost(self):
        """TC-037-08: Program row sums costs across KPIs."""
        from sfi_reporter.data import compute_row_cost

        items = [
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-2"},
        ]
        kpi_cost_map = {"kpi-1": 180.0, "kpi-2": 1054.0}

        result = compute_row_cost(items, kpi_cost_map)

        assert result == 180 * 2 + 1054 * 1, \
            "Program cost should sum across all KPI items in the program"

    def test_owner_row_cost(self):
        """TC-037-09: Owner row sums costs for all owned items."""
        from sfi_reporter.data import compute_row_cost

        items = [
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-1"},
        ]
        kpi_cost_map = {"kpi-1": 180.0}

        result = compute_row_cost(items, kpi_cost_map)

        assert result == 540.0, \
            "Owner cost should sum costs for all items under that owner"

    def test_item_cost(self):
        """TC-037-10: Individual item shows its KPI's AverageCostInMin."""
        from sfi_reporter.data import compute_row_cost

        items = [{"_kpi_id": "kpi-1"}]
        kpi_cost_map = {"kpi-1": 180.0}

        result = compute_row_cost(items, kpi_cost_map)

        assert result == 180.0, \
            "Individual item cost should equal its KPI's AverageCostInMin"


# ---------------------------------------------------------------------------
# AC-7: Graceful degradation & formatting
# ---------------------------------------------------------------------------

class TestCostFormatting:
    """Tests for cost display formatting."""

    def test_missing_kpi_contributes_zero(self):
        """TC-037-11: Items with missing cost contribute 0 to sums."""
        from sfi_reporter.data import compute_row_cost

        items = [
            {"_kpi_id": "kpi-1"},
            {"_kpi_id": "kpi-missing"},
            {"_kpi_id": "kpi-3"},
        ]
        kpi_cost_map = {"kpi-1": 180.0, "kpi-3": 1054.0}

        result = compute_row_cost(items, kpi_cost_map)

        assert result == 1234.0, \
            "Items with missing cost should contribute 0 to sums"

    def test_format_with_thousands_separator(self):
        """TC-037-12: Cost formatted with thousands separator."""
        from sfi_reporter.data import format_cost

        assert format_cost(12500) == "12,500", \
            "Cost should be formatted with thousands separator"

    def test_format_none_shows_dash(self):
        """TC-037-12b: None cost shows dash."""
        from sfi_reporter.data import format_cost

        assert format_cost(None) == "\u2014", \
            "None cost should display em-dash"

    def test_format_zero_shows_zero(self):
        """TC-037-13: Zero cost shows '0', not dash."""
        from sfi_reporter.data import format_cost

        assert format_cost(0) == "0", \
            "Zero cost should display '0', not dash"

    def test_format_fractional_rounds(self):
        """Fractional cost rounds to integer for display."""
        from sfi_reporter.data import format_cost

        assert format_cost(1054.7) == "1,055", \
            "Fractional cost should round to nearest integer"
