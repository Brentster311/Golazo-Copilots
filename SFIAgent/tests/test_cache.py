"""
Tests for cache module.
"""

import json
import time
import pytest
from pathlib import Path

from s360_client.cache import CacheManager
from s360_client.config import S360Config


class TestCacheManager:
    """Tests for cache operations."""

    def test_cache_miss_returns_none(self, test_config: S360Config):
        """Given empty cache, when requesting data, then return None."""
        # Arrange
        cache = CacheManager(test_config)

        # Act
        result = cache.get("/some/endpoint", {"key": "value"})

        # Assert
        assert result is None

    def test_cache_set_and_get(self, test_config: S360Config):
        """Given cached data, when requesting, then return cached data."""
        # Arrange
        cache = CacheManager(test_config)
        endpoint = "/test/endpoint"
        params = {"id": "123"}
        data = {"result": "test data", "count": 42}

        # Act
        cache.set(endpoint, data, params)
        result = cache.get(endpoint, params)

        # Assert
        assert result == data

    def test_cache_expiry(self, temp_cache_dir: Path):
        """Given expired cache, when requesting, then return None."""
        # Arrange
        config = S360Config(
            cache_directory=temp_cache_dir,
            cache_expiry_minutes=0,  # Immediately expire
        )
        cache = CacheManager(config)
        endpoint = "/test/endpoint"
        data = {"result": "test"}

        # Act
        cache.set(endpoint, data)
        time.sleep(0.1)  # Small delay to ensure expiry
        result = cache.get(endpoint)

        # Assert
        assert result is None

    def test_cache_disabled(self, temp_cache_dir: Path):
        """Given cache disabled, when caching, then don't cache."""
        # Arrange
        config = S360Config(
            cache_directory=temp_cache_dir,
            cache_enabled=False,
        )
        cache = CacheManager(config)
        endpoint = "/test/endpoint"
        data = {"result": "test"}

        # Act
        set_result = cache.set(endpoint, data)
        get_result = cache.get(endpoint)

        # Assert
        assert set_result is False
        assert get_result is None

    def test_cache_different_params_different_keys(self, test_config: S360Config):
        """Given same endpoint different params, then cache separately."""
        # Arrange
        cache = CacheManager(test_config)
        endpoint = "/test/endpoint"
        data1 = {"result": "data1"}
        data2 = {"result": "data2"}

        # Act
        cache.set(endpoint, data1, {"id": "1"})
        cache.set(endpoint, data2, {"id": "2"})

        result1 = cache.get(endpoint, {"id": "1"})
        result2 = cache.get(endpoint, {"id": "2"})

        # Assert
        assert result1 == data1
        assert result2 == data2

    def test_cache_corruption_recovery(self, test_config: S360Config):
        """Given corrupted cache file, when reading, then return None and delete."""
        # Arrange
        cache = CacheManager(test_config)
        endpoint = "/test/endpoint"

        # Create corrupted cache file
        cache_key = cache._get_cache_key(endpoint)
        cache_path = cache._get_cache_path(cache_key)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text("not valid json {{{")

        # Act
        result = cache.get(endpoint)

        # Assert
        assert result is None
        assert not cache_path.exists()  # Corrupted file should be deleted

    def test_cache_invalidate_specific(self, test_config: S360Config):
        """Given cached data, when invalidating specific entry, then only remove that entry."""
        # Arrange
        cache = CacheManager(test_config)
        cache.set("/endpoint1", {"data": 1})
        cache.set("/endpoint2", {"data": 2})

        # Act
        count = cache.invalidate("/endpoint1")

        # Assert
        assert count == 1
        assert cache.get("/endpoint1") is None
        assert cache.get("/endpoint2") == {"data": 2}

    def test_cache_clear_all(self, test_config: S360Config):
        """Given cached data, when clearing, then remove all entries."""
        # Arrange
        cache = CacheManager(test_config)
        cache.set("/endpoint1", {"data": 1})
        cache.set("/endpoint2", {"data": 2})
        cache.set("/endpoint3", {"data": 3})

        # Act
        count = cache.clear()

        # Assert
        assert count == 3
        assert cache.get("/endpoint1") is None
        assert cache.get("/endpoint2") is None
        assert cache.get("/endpoint3") is None
