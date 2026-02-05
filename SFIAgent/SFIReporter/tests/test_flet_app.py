"""Tests for Flet app components."""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta


class TestCacheAgeDisplay:
    """Test cache age indicator logic."""

    def test_cache_age_fresh_color(self):
        """TC-008: Cache < 30 min should show normal color."""
        from sfi_reporter.flet_app import get_cache_age_color
        
        age_minutes = 15
        color = get_cache_age_color(age_minutes)
        
        assert color == "green" or color is None  # Normal/default

    def test_cache_age_stale_color(self):
        """TC-009: Cache > 30 min should show warning color."""
        from sfi_reporter.flet_app import get_cache_age_color
        
        age_minutes = 45
        color = get_cache_age_color(age_minutes)
        
        assert color == "orange" or color == "yellow"


class TestDataFetching:
    """Test data fetching with mocks."""

    def test_refresh_success(self, mocker):
        """TC-004: Verify refresh fetches and caches data."""
        mock_services = mocker.patch('sfi_reporter.data.get_user_services')
        mock_action_items = mocker.patch('sfi_reporter.data.get_action_items_summary')
        mock_write = mocker.patch('sfi_reporter.flet_app.write_cache')
        
        mock_services.return_value = [{'Name': 'Svc1', 'Id': '123'}]
        mock_action_items.return_value = {'ActionItemSummaryList': []}
        
        from sfi_reporter.flet_app import do_refresh
        
        result = do_refresh('testuser')
        
        mock_services.assert_called_once_with('testuser')
        mock_action_items.assert_called_once_with(['123'])
        mock_write.assert_called_once()
        assert result is not None
        assert 'services' in result

    def test_refresh_error(self, mocker):
        """TC-005: Verify error handling during refresh."""
        mock_services = mocker.patch('sfi_reporter.data.get_user_services')
        mock_services.side_effect = Exception("API Error")
        
        from sfi_reporter.flet_app import do_refresh
        
        result = do_refresh('testuser')
        
        assert result is None


class TestClearCache:
    """Test clear cache functionality."""

    def test_clear_cache_calls_module(self, mocker):
        """TC-010: Verify clear cache button works."""
        mock_clear = mocker.patch('sfi_reporter.flet_app.clear_cache')
        mock_clear.return_value = True
        
        from sfi_reporter.flet_app import do_clear_cache
        
        result = do_clear_cache('testuser')
        
        mock_clear.assert_called_once_with('testuser')
        assert result is True
