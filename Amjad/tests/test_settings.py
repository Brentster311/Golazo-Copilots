"""Tests for SettingsManager and FactExtractor kwargs override."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from ees.gui.settings import SettingsManager


# ── SettingsManager ───────────────────────────────────────────


class TestSettingsManagerLoad:
    """TC-1, TC-2: Load from YAML and defaults."""

    def test_load_from_yaml(self, tmp_path: Path) -> None:
        """TC-1: Load settings from existing YAML file."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text(
            "azure_openai:\n"
            '  endpoint: "https://test.openai.azure.com/"\n'
            '  deployment: "gpt-4o"\n'
            '  api_version: "2025-01-01"\n'
        )
        mgr = SettingsManager(tmp_path)
        settings = mgr.load()
        assert settings["endpoint"] == "https://test.openai.azure.com/"
        assert settings["deployment"] == "gpt-4o"
        assert settings["api_version"] == "2025-01-01"

    def test_load_returns_defaults_when_no_file(self, tmp_path: Path) -> None:
        """TC-2: Returns built-in defaults when no settings.yaml."""
        mgr = SettingsManager(tmp_path)
        settings = mgr.load()
        assert settings["endpoint"] == "https://open-ai-poc.openai.azure.com/"
        assert settings["deployment"] == "gpt-5.2"
        assert settings["api_version"] == "2024-12-01-preview"


class TestSettingsManagerSave:
    """TC-3, TC-8: Save and round-trip."""

    def test_save_creates_yaml(self, tmp_path: Path) -> None:
        """TC-3: Save creates settings.yaml with correct structure."""
        mgr = SettingsManager(tmp_path)
        mgr.save({
            "endpoint": "https://x.openai.azure.com/",
            "deployment": "gpt-4o",
            "api_version": "2025-01-01",
        })
        assert (tmp_path / "settings.yaml").exists()
        content = (tmp_path / "settings.yaml").read_text()
        assert "https://x.openai.azure.com/" in content

    def test_save_and_reload_roundtrip(self, tmp_path: Path) -> None:
        """TC-8: Save then load returns same values."""
        mgr = SettingsManager(tmp_path)
        original = {
            "endpoint": "https://roundtrip.openai.azure.com/",
            "deployment": "gpt-5",
            "api_version": "2025-06-01",
        }
        mgr.save(original)
        loaded = mgr.load()
        assert loaded == original


class TestSettingsManagerEffective:
    """TC-4 through TC-7: Resolution order — config → env → default."""

    def test_env_var_overrides_default(self, tmp_path: Path) -> None:
        """TC-4: Env var used when no config."""
        mgr = SettingsManager(tmp_path)
        with patch.dict(os.environ, {"AZURE_OPENAI_ENDPOINT": "https://env.openai.azure.com/"}):
            value, source = mgr.get_effective("endpoint")
        assert value == "https://env.openai.azure.com/"
        assert source == "env"

    def test_config_overrides_env_var(self, tmp_path: Path) -> None:
        """TC-5: Config takes precedence over env var."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text(
            "azure_openai:\n"
            '  endpoint: "https://config.openai.azure.com/"\n'
        )
        mgr = SettingsManager(tmp_path)
        with patch.dict(os.environ, {"AZURE_OPENAI_ENDPOINT": "https://env.openai.azure.com/"}):
            value, source = mgr.get_effective("endpoint")
        assert value == "https://config.openai.azure.com/"
        assert source == "config"

    def test_blank_config_falls_back_to_env(self, tmp_path: Path) -> None:
        """TC-6: Blank config field falls back to env var."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text(
            "azure_openai:\n"
            '  endpoint: ""\n'
        )
        mgr = SettingsManager(tmp_path)
        with patch.dict(os.environ, {"AZURE_OPENAI_ENDPOINT": "https://env.openai.azure.com/"}):
            value, source = mgr.get_effective("endpoint")
        assert value == "https://env.openai.azure.com/"
        assert source == "env"

    def test_default_when_no_config_no_env(self, tmp_path: Path) -> None:
        """TC-7: Falls all the way to built-in default."""
        mgr = SettingsManager(tmp_path)
        env_cleared = {
            "AZURE_OPENAI_ENDPOINT": "",
            "AZURE_OPENAI_DEPLOYMENT": "",
            "AZURE_OPENAI_API_VERSION": "",
        }
        with patch.dict(os.environ, env_cleared, clear=False):
            # Remove the keys entirely
            for k in env_cleared:
                os.environ.pop(k, None)
            value, source = mgr.get_effective("endpoint")
        assert value == "https://open-ai-poc.openai.azure.com/"
        assert source == "default"


class TestFactExtractorKwargs:
    """TC-9, TC-10: FactExtractor with explicit kwargs."""

    def test_accepts_kwargs(self) -> None:
        """TC-9: FactExtractor uses kwargs instead of env vars."""
        from unittest.mock import MagicMock, patch as mock_patch

        with mock_patch("ees.fact_extractor.AzureOpenAI") as mock_client, \
             mock_patch("ees.fact_extractor.ChainedTokenCredential"):
            from ees.fact_extractor import FactExtractor
            extractor = FactExtractor(
                endpoint="https://kwarg.openai.azure.com/",
                deployment="gpt-4o-kwarg",
                api_version="2025-03-01",
            )
            assert extractor.deployment == "gpt-4o-kwarg"
            mock_client.assert_called_once()
            call_kwargs = mock_client.call_args
            assert call_kwargs.kwargs["azure_endpoint"] == "https://kwarg.openai.azure.com/"
            assert call_kwargs.kwargs["api_version"] == "2025-03-01"

    def test_kwargs_none_falls_back_to_env(self) -> None:
        """TC-10: FactExtractor() with no kwargs uses env vars."""
        from unittest.mock import MagicMock, patch as mock_patch

        with mock_patch.dict(os.environ, {
            "AZURE_OPENAI_ENDPOINT": "https://envtest.openai.azure.com/",
            "AZURE_OPENAI_DEPLOYMENT": "gpt-4o-env",
        }):
            with mock_patch("ees.fact_extractor.AzureOpenAI") as mock_client, \
                 mock_patch("ees.fact_extractor.ChainedTokenCredential"):
                from ees.fact_extractor import FactExtractor
                extractor = FactExtractor()
                assert extractor.deployment == "gpt-4o-env"
