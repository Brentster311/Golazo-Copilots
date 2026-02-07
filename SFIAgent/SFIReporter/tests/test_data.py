"""Tests for data module."""
import pytest
import sfi_reporter.data as data_module


@pytest.fixture(autouse=True)
def _reset_client_singleton():
    """Reset the S360Client singleton before each test."""
    data_module._client_instance = None
    yield
    data_module._client_instance = None


class TestUserDetection:
    """Test user detection functionality."""

    def test_auto_detect_user(self, mocker):
        """TC-001: Verify user alias is auto-detected from Azure CLI credentials."""
        # Mock S360Client
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        
        # Mock user info
        mock_user = mocker.MagicMock()
        mock_user.alias = 'brentj'
        mock_client.get_current_user.return_value = mock_user
        
        from sfi_reporter.data import get_current_user_alias
        
        alias = get_current_user_alias()
        assert alias == 'brentj'

    def test_handle_missing_azure_cli(self, mocker):
        """TC-002: Verify clear error when Azure CLI is not available."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client_class.side_effect = Exception("Azure CLI not found")
        
        from sfi_reporter.data import get_current_user_alias
        
        result = get_current_user_alias()
        assert result is None


class TestServiceFetching:
    """Test service fetching functionality."""

    def test_fetch_user_services(self, mocker):
        """TC-003: Verify services are fetched for given user."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        mock_client.get_default_landing_view.return_value = {
            'SearchDataList': [
                {'Id': 'svc1', 'Name': 'Service A', 'Group': 'Service'},
                {'Id': 'svc2', 'Name': 'Service B', 'Group': 'Service'},
            ]
        }
        
        from sfi_reporter.data import get_user_services
        
        services = get_user_services('brentj')
        assert len(services) == 2
        assert services[0]['Name'] == 'Service A'


class TestActionItemFetching:
    """Test action item fetching functionality."""

    def test_fetch_action_items(self, mocker):
        """TC-004: Verify action items are fetched for given services."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        mock_client.get_action_items_summary.return_value = {
            'SummaryList': [
                {
                    'ActionItemId': 'kpi1',
                    'ActionItemName': 'KPI 1',
                    'TotalCount': 5,
                    'OutOfSlaCount': 2,
                },
            ]
        }
        
        from sfi_reporter.data import get_action_items_summary
        
        items = get_action_items_summary(['svc1', 'svc2'])
        assert items is not None
        assert 'SummaryList' in items

    def test_handle_api_timeout(self, mocker):
        """TC-005: Verify timeout is handled gracefully."""
        mock_client_class = mocker.patch('sfi_reporter.data.S360Client')
        mock_client = mock_client_class.return_value
        mock_client.get_action_items_summary.side_effect = TimeoutError()
        
        from sfi_reporter.data import get_action_items_summary
        
        items = get_action_items_summary(['svc1'])
        assert items is None or items == {}


class TestColumnMetadataCache:
    """Test column metadata caching functionality."""

    def test_column_cache_path(self):
        """TC01: Column metadata cache is at $TEMP/sfireporter/column_metadata.json"""
        from sfi_reporter.data import get_column_cache_path
        import os
        path = get_column_cache_path()
        assert "sfireporter" in path
        assert path.endswith("column_metadata.json")

    def test_load_column_cache_when_missing(self, tmp_path, monkeypatch):
        """TC02: Returns empty cache when cache file doesn't exist"""
        monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", 
                            lambda: str(tmp_path / "nonexistent.json"))
        from sfi_reporter.data import load_column_cache
        cache = load_column_cache()
        assert cache == {"version": 1, "kpis": {}}

    def test_save_and_load_column_cache(self, tmp_path, monkeypatch):
        """TC03: Cache roundtrip preserves data"""
        cache_path = str(tmp_path / "column_metadata.json")
        monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", lambda: cache_path)
        
        from sfi_reporter.data import save_column_cache, load_column_cache
        
        test_data = {
            "version": 1,
            "kpis": {
                "kpi-123": {
                    "columns": ["id", "title", "dueDate"],
                    "discovered_at": "2026-02-04T18:00:00Z"
                }
            }
        }
        save_column_cache(test_data)
        loaded = load_column_cache()
        assert loaded == test_data

    def test_load_column_cache_corrupt_json(self, tmp_path, monkeypatch):
        """TC04: Returns empty cache when file is corrupt"""
        cache_path = tmp_path / "column_metadata.json"
        cache_path.write_text("not valid json {{{")
        monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", 
                            lambda: str(cache_path))
        
        from sfi_reporter.data import load_column_cache
        cache = load_column_cache()
        assert cache == {"version": 1, "kpis": {}}

    def test_get_cached_columns_hit(self, tmp_path, monkeypatch):
        """TC05: Returns cached columns for known KPI"""
        cache_path = str(tmp_path / "column_metadata.json")
        monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", lambda: cache_path)
        
        from sfi_reporter.data import save_column_cache, get_cached_columns
        
        save_column_cache({
            "version": 1,
            "kpis": {
                "kpi-123": {"columns": ["id", "title"], "discovered_at": "2026-02-04"}
            }
        })
        
        columns = get_cached_columns("kpi-123")
        assert columns == ["id", "title"]

    def test_get_cached_columns_miss(self, tmp_path, monkeypatch):
        """Returns None for unknown KPI"""
        cache_path = str(tmp_path / "column_metadata.json")
        monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", lambda: cache_path)
        
        from sfi_reporter.data import save_column_cache, get_cached_columns
        
        save_column_cache({"version": 1, "kpis": {}})
        
        columns = get_cached_columns("unknown-kpi")
        assert columns is None

    def test_essential_columns_always_included(self):
        """TC06: S360_ProgramIds, url, and id are always in column requests"""
        from sfi_reporter.data import ESSENTIAL_COLUMNS, merge_columns_with_essentials
        
        discovered = ["title", "dueDate"]
        result = merge_columns_with_essentials(discovered)
        
        assert "S360_ProgramIds" in result
        assert "url" in result
        assert "id" in result
        # Original columns preserved
        assert "title" in result
        assert "dueDate" in result

    def test_cache_kpi_columns(self, tmp_path, monkeypatch):
        """Cache KPI columns stores columns with timestamp"""
        cache_path = str(tmp_path / "column_metadata.json")
        monkeypatch.setattr("sfi_reporter.data.get_column_cache_path", lambda: cache_path)
        
        from sfi_reporter.data import cache_kpi_columns, get_cached_columns
        
        cache_kpi_columns("kpi-456", ["col1", "col2", "col3"])
        
        columns = get_cached_columns("kpi-456")
        assert columns == ["col1", "col2", "col3"]
