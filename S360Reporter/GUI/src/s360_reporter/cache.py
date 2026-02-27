"""Cache module for S360Reporter.

Provides JSON file-based caching with 1-hour expiration.
"""
import json
import logging
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


CACHE_EXPIRATION_HOURS = 1


def get_cache_dir() -> Path:
    """Get the default cache directory.
    
    Returns:
        Path to cache directory (creates if needed).
    """
    cache_dir = Path(tempfile.gettempdir()) / 'S360Reporter'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def get_cache_path(user_alias: str, cache_dir: Optional[Path] = None) -> Path:
    """Get the cache file path for a user.
    
    Args:
        user_alias: The user alias.
        cache_dir: Optional custom cache directory.
        
    Returns:
        Path to cache file.
    """
    if cache_dir is None:
        cache_dir = get_cache_dir() / 'kpis'
        cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f'{user_alias}_cache.json'


def write_cache(user_alias: str, data: dict, cache_dir: Optional[Path] = None) -> None:
    """Write data to cache file.
    
    Args:
        user_alias: The user alias.
        data: Data to cache (must be JSON-serializable).
        cache_dir: Optional custom cache directory.
    """
    cache_path = get_cache_path(user_alias, cache_dir)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    
    with cache_path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def read_cache(user_alias: str, cache_dir: Optional[Path] = None) -> Optional[dict]:
    """Read data from cache file.
    
    Args:
        user_alias: The user alias.
        cache_dir: Optional custom cache directory.
        
    Returns:
        Cached data or None if not found/invalid.
    """
    cache_path = get_cache_path(user_alias, cache_dir)
    
    if not cache_path.exists():
        return None
    
    try:
        with cache_path.open('r', encoding='utf-8') as f:
            content = f.read()
            if not content.strip():
                return None
            return json.loads(content)
    except (json.JSONDecodeError, IOError):
        return None


def is_cache_valid(data: dict, max_age_hours: float = CACHE_EXPIRATION_HOURS) -> bool:
    """Check if cached data is still valid (not expired).
    
    Args:
        data: Cached data with 'timestamp' key.
        max_age_hours: Maximum age in hours (default 1).
        
    Returns:
        True if cache is valid, False if expired.
    """
    if not data or 'timestamp' not in data:
        return False
    
    try:
        timestamp = datetime.fromisoformat(data['timestamp'])
        age = datetime.now() - timestamp
        return age < timedelta(hours=max_age_hours)
    except (ValueError, KeyError):
        return False


def get_cache_age_minutes(data: dict) -> Optional[int]:
    """Get the age of cached data in minutes.
    
    Args:
        data: Cached data with 'timestamp' key.
        
    Returns:
        Age in minutes or None if no timestamp.
    """
    if not data or 'timestamp' not in data:
        return None
    
    try:
        timestamp = datetime.fromisoformat(data['timestamp'])
        age = datetime.now() - timestamp
        return int(age.total_seconds() / 60)
    except (ValueError, KeyError):
        return None


def clear_cache(user_alias: str, cache_dir: Optional[Path] = None) -> bool:
    """Clear cache for a user.
    
    Also clears the column metadata cache.
    
    Args:
        user_alias: The user alias.
        cache_dir: Optional custom cache directory.
        
    Returns:
        True if cache was cleared, False if no cache existed.
    """
    cache_path = get_cache_path(user_alias, cache_dir)
    
    cleared = False
    if cache_path.exists():
        cache_path.unlink()
        cleared = True
    
    # Also clear column metadata cache
    try:
        from s360_reporter.data import get_column_cache_path
        column_cache_path = Path(get_column_cache_path())
        if column_cache_path.exists():
            column_cache_path.unlink()
            cleared = True
            logger.info("Cleared column metadata cache")
    except (ImportError, OSError) as e:
        logger.warning("Could not clear column cache: %s", e)
    
    return cleared
