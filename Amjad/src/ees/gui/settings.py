"""Settings manager for EES GUI — persists Azure OpenAI and Kusto config to YAML.

Resolution order: settings.yaml → environment variable → built-in default.
No Tkinter dependency — fully testable in isolation.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

_DEFAULTS: dict[str, str] = {
    "endpoint": "https://open-ai-poc.openai.azure.com/",
    "deployment": "gpt5.2",
    "api_version": "2025-12-11",
}

_ENV_MAP: dict[str, str] = {
    "endpoint": "AZURE_OPENAI_ENDPOINT",
    "deployment": "AZURE_OPENAI_DEPLOYMENT",
    "api_version": "AZURE_OPENAI_API_VERSION",
}

_KUSTO_DEFAULTS: dict[str, str] = {
    "cluster": "https://acciafollowercentralus.centralus.kusto.windows.net",
    "database": "IcmDataWarehouse",
}

_KUSTO_ENV_MAP: dict[str, str] = {
    "cluster": "KUSTO_CLUSTER",
    "database": "KUSTO_DATABASE",
}

_SETTINGS_FILE = "settings.yaml"


class SettingsManager:
    """Load, save, and resolve Azure OpenAI settings."""

    def __init__(self, data_dir: Path) -> None:
        self._data_dir = data_dir
        self._yaml = YAML()
        self._yaml.default_flow_style = False

    @property
    def _path(self) -> Path:
        return self._data_dir / _SETTINGS_FILE

    def load(self) -> dict[str, str]:
        """Load settings from YAML; return defaults if file missing."""
        if not self._path.exists():
            return dict(_DEFAULTS)

        raw = self._yaml.load(self._path)
        section = (raw or {}).get("azure_openai", {})
        return {
            key: section.get(key, _DEFAULTS[key]) or _DEFAULTS[key]
            for key in _DEFAULTS
        }

    def save(self, settings: dict[str, str]) -> None:
        """Persist Azure OpenAI settings to settings.yaml (preserves other sections)."""
        existing = self._load_raw()
        existing["azure_openai"] = {
            "endpoint": settings.get("endpoint", ""),
            "deployment": settings.get("deployment", ""),
            "api_version": settings.get("api_version", ""),
        }
        self._write_raw(existing)

    # ── Kusto settings ────────────────────────────────────────

    def load_kusto(self) -> dict[str, str]:
        """Load Kusto settings from YAML; return defaults if missing."""
        if not self._path.exists():
            return dict(_KUSTO_DEFAULTS)

        raw = self._yaml.load(self._path)
        section = (raw or {}).get("kusto", {})
        return {
            key: section.get(key, _KUSTO_DEFAULTS[key]) or _KUSTO_DEFAULTS[key]
            for key in _KUSTO_DEFAULTS
        }

    def save_kusto(self, settings: dict[str, str]) -> None:
        """Persist Kusto settings to settings.yaml (preserves other sections)."""
        existing = self._load_raw()
        existing["kusto"] = {
            "cluster": settings.get("cluster", ""),
            "database": settings.get("database", ""),
        }
        self._write_raw(existing)

    # ── Helpers ───────────────────────────────────────────────

    def _load_raw(self) -> dict[str, Any]:
        """Load the full raw YAML dict, or empty dict if missing."""
        if self._path.exists():
            return dict(self._yaml.load(self._path) or {})
        return {}

    def _write_raw(self, data: dict[str, Any]) -> None:
        """Write full dict back to settings file."""
        self._data_dir.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as f:
            self._yaml.dump(data, f)

    def get_effective(self, key: str) -> tuple[str, str]:
        """Return (value, source) for a setting key.

        Resolution: config → env var → built-in default.
        """
        # 1. Config file
        if self._path.exists():
            raw = self._yaml.load(self._path)
            section = (raw or {}).get("azure_openai", {})
            val = section.get(key, "")
            if val:
                return str(val), "config"

        # 2. Environment variable
        env_key = _ENV_MAP.get(key, "")
        if env_key:
            env_val = os.environ.get(env_key, "")
            if env_val:
                return env_val, "env"

        # 3. Built-in default
        return _DEFAULTS[key], "default"
