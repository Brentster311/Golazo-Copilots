"""
Local caching for S360 Client.
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from s360_client.config import S360Config
from s360_client.exceptions import S360CacheError

logger = logging.getLogger(__name__)

__all__ = ["CacheManager"]


class CacheManager:
    """Handles local caching of API responses."""

    def __init__(self, config: S360Config | None = None) -> None:
        self.config = config or S360Config()
        self._cache_dir: Path | None = None

    def _get_cache_dir(self) -> Path:
        """Get the cache directory, creating if needed."""
        if self._cache_dir is None:
            self._cache_dir = self.config.get_cache_dir()
        return self._cache_dir

    def _get_cache_key(self, endpoint: str, params: dict[str, Any] | None = None) -> str:
        """Generate a unique cache key for an endpoint and parameters."""
        key_data = f"{endpoint}"
        if params:
            # Sort params for consistent hashing
            sorted_params = json.dumps(params, sort_keys=True)
            key_data = f"{endpoint}:{sorted_params}"
        
        # Create a short hash for the filename
        hash_str = hashlib.sha256(key_data.encode()).hexdigest()[:16]
        # Make endpoint safe for filename
        safe_endpoint = endpoint.replace("/", "_").replace("?", "_").strip("_")
        return f"{safe_endpoint}_{hash_str}"

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the full path for a cache file."""
        return self._get_cache_dir() / f"{cache_key}.json"

    def _is_expired(self, cache_path: Path) -> bool:
        """Check if a cache file has expired."""
        if not cache_path.exists():
            return True
        
        try:
            stat = cache_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
            now = datetime.now(timezone.utc)
            age_minutes = (now - modified_time).total_seconds() / 60
            return age_minutes > self.config.cache_expiry_minutes
        except OSError:
            return True

    def get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> Any | None:
        """
        Get cached data for an endpoint.

        Args:
            endpoint: The API endpoint path.
            params: Optional parameters used in the request.

        Returns:
            The cached data, or None if not found/expired.
        """
        if not self.config.cache_enabled:
            return None

        cache_key = self._get_cache_key(endpoint, params)
        cache_path = self._get_cache_path(cache_key)

        if not cache_path.exists():
            logger.debug("Cache miss: %s", cache_key)
            return None

        if self._is_expired(cache_path):
            logger.debug("Cache expired: %s", cache_key)
            self._delete_cache_file(cache_path)
            return None

        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug("Cache hit: %s", cache_key)
            return data
        except json.JSONDecodeError as e:
            logger.warning("Corrupted cache file, deleting: %s", cache_path)
            self._delete_cache_file(cache_path)
            return None
        except OSError as e:
            logger.warning("Error reading cache: %s", str(e))
            return None

    def set(
        self,
        endpoint: str,
        data: Any,
        params: dict[str, Any] | None = None,
    ) -> bool:
        """
        Cache data for an endpoint.

        Args:
            endpoint: The API endpoint path.
            data: The data to cache.
            params: Optional parameters used in the request.

        Returns:
            True if caching succeeded, False otherwise.
        """
        if not self.config.cache_enabled:
            return False

        cache_key = self._get_cache_key(endpoint, params)
        cache_path = self._get_cache_path(cache_key)

        try:
            # Ensure cache directory exists
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            logger.debug("Cached: %s", cache_key)
            return True
        except OSError as e:
            logger.warning("Failed to write cache: %s", str(e))
            return False

    def _delete_cache_file(self, cache_path: Path) -> None:
        """Delete a cache file safely."""
        try:
            cache_path.unlink(missing_ok=True)
        except OSError as e:
            logger.warning("Failed to delete cache file: %s", str(e))

    def invalidate(
        self,
        endpoint: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> int:
        """
        Invalidate cached data.

        Args:
            endpoint: Specific endpoint to invalidate, or None for all.
            params: Specific params to invalidate.

        Returns:
            Number of cache entries invalidated.
        """
        count = 0
        cache_dir = self._get_cache_dir()

        if not cache_dir.exists():
            return 0

        if endpoint is not None:
            # Invalidate specific cache entry
            cache_key = self._get_cache_key(endpoint, params)
            cache_path = self._get_cache_path(cache_key)
            if cache_path.exists():
                self._delete_cache_file(cache_path)
                count = 1
        else:
            # Invalidate all cache entries
            for cache_file in cache_dir.glob("*.json"):
                self._delete_cache_file(cache_file)
                count += 1

        logger.info("Invalidated %d cache entries", count)
        return count

    def clear(self) -> int:
        """
        Clear all cached data.

        Returns:
            Number of cache entries cleared.
        """
        return self.invalidate()
