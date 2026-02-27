"""Tests for cache module."""
import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta


class TestCacheWriteAndRead:
    """Test cache read/write operations."""

    def test_cache_write_and_read(self, tmp_path):
        """TC-006: Verify data can be cached and retrieved."""
        from s360_reporter.cache import write_cache, read_cache
        
        data = {'items': [{'id': 1}], 'timestamp': '2026-02-04T10:00:00'}
        
        write_cache('brentj', data, cache_dir=tmp_path)
        result = read_cache('brentj', cache_dir=tmp_path)
        
        assert result == data

    def test_cache_creates_file(self, tmp_path):
        """Verify cache creates a file."""
        from s360_reporter.cache import write_cache
        
        data = {'items': [], 'timestamp': datetime.now().isoformat()}
        write_cache('testuser', data, cache_dir=tmp_path)
        
        cache_file = tmp_path / 'testuser_cache.json'
        assert cache_file.exists()

    def test_cache_read_nonexistent(self, tmp_path):
        """Verify reading nonexistent cache returns None."""
        from s360_reporter.cache import read_cache
        
        result = read_cache('nonexistent', cache_dir=tmp_path)
        assert result is None


class TestCacheExpiration:
    """Test cache expiration logic."""

    def test_cache_expiration_fresh(self, tmp_path):
        """TC-008: Verify cache is valid within 1 hour."""
        from s360_reporter.cache import is_cache_valid
        
        data = {'timestamp': datetime.now().isoformat()}
        
        result = is_cache_valid(data)
        assert result is True

    def test_cache_expiration_old(self, tmp_path):
        """TC-007: Verify cache is considered expired after 1 hour."""
        from s360_reporter.cache import is_cache_valid
        
        # Create cache from 2 hours ago
        old_time = datetime.now() - timedelta(hours=2)
        data = {'timestamp': old_time.isoformat()}
        
        result = is_cache_valid(data)
        assert result is False

    def test_cache_expiration_boundary(self, tmp_path):
        """Verify cache at exactly 1 hour is expired."""
        from s360_reporter.cache import is_cache_valid
        
        # Create cache from exactly 61 minutes ago
        old_time = datetime.now() - timedelta(minutes=61)
        data = {'timestamp': old_time.isoformat()}
        
        result = is_cache_valid(data)
        assert result is False


class TestCorruptedCache:
    """Test handling of corrupted cache."""

    def test_corrupted_cache(self, tmp_path):
        """TC-009: Verify corrupted cache is handled gracefully."""
        from s360_reporter.cache import read_cache
        
        cache_file = tmp_path / 'brentj_cache.json'
        cache_file.write_text('not valid json {{{')
        
        result = read_cache('brentj', cache_dir=tmp_path)
        assert result is None

    def test_empty_cache_file(self, tmp_path):
        """Verify empty cache file is handled."""
        from s360_reporter.cache import read_cache
        
        cache_file = tmp_path / 'empty_cache.json'
        cache_file.write_text('')
        
        result = read_cache('empty', cache_dir=tmp_path)
        assert result is None


class TestClearCache:
    """Test cache clearing functionality."""

    def test_clear_cache_clears_column_metadata(self, tmp_path, monkeypatch):
        """TC07: Clear Cache button removes both data cache and column metadata cache"""
        from s360_reporter.cache import write_cache, clear_cache
        
        # Create user data cache
        data = {'items': [], 'timestamp': datetime.now().isoformat()}
        write_cache('brentj', data, cache_dir=tmp_path)
        
        # Create column metadata cache
        column_cache_path = tmp_path / 'column_metadata.json'
        column_cache_path.write_text('{"version": 1, "kpis": {}}')
        
        # Monkeypatch to use our tmp_path for column cache
        monkeypatch.setattr("s360_reporter.data.get_column_cache_path", 
                            lambda: str(column_cache_path))
        
        # Clear cache
        result = clear_cache('brentj', cache_dir=tmp_path)
        
        assert result is True
        assert not (tmp_path / 'brentj_cache.json').exists()
        assert not column_cache_path.exists()
