"""
Configuration for S360 Client.
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import ClassVar


def _get_default_cache_dir() -> Path:
    """Get the default cache directory based on OS."""
    if os.name == "nt":  # Windows
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    else:
        base = Path.home() / ".cache"
    return base / "accia_s360" / "cache"


@dataclass
class S360Config:
    """Configuration settings for S360 Client."""

    # API Settings
    base_url: str = "https://api.vnext.s360.msftcloudes.com/v1"
    timeout_seconds: int = 30
    retry_count: int = 1
    retry_delay_seconds: float = 2.0

    # Authentication scopes
    s360_scope: str = "https://microsoft.onmicrosoft.com/Service360/.default"
    graph_scope: str = "https://graph.microsoft.com/.default"

    # Cache Settings
    cache_enabled: bool = True
    cache_expiry_minutes: int = 60
    cache_directory: Path | None = None

    # Logging
    log_level: str = "INFO"
    mask_tokens: bool = True  # Never log full tokens

    # Known endpoints (from reference project)
    KNOWN_ENDPOINTS: ClassVar[list[tuple[str, str, str]]] = [
        ("GET", "/ActionItems/GetEtaHistoryById", "Get ETA history for an action item"),
        ("POST", "/ActionItems/SaveETAsByIds", "Save ETA updates"),
    ]

    def __post_init__(self) -> None:
        """Set defaults after initialization."""
        if self.cache_directory is None:
            self.cache_directory = _get_default_cache_dir()

    def get_cache_dir(self) -> Path:
        """Get the cache directory, creating it if needed."""
        cache_dir = self.cache_directory or _get_default_cache_dir()
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
