"""Tests for KustoClient and extended SettingsManager (EES-00007)."""
from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ── KustoClient ───────────────────────────────────────────────


class TestKustoClientFetch:
    """TC-1 through TC-4: KustoClient.fetch_incident."""

    def test_fetch_returns_description(self) -> None:
        """TC-1: Successful fetch returns description text."""
        mock_df = MagicMock()
        mock_df.empty = False
        mock_df.iloc.__getitem__ = MagicMock(return_value="Server is down and not responding.")

        with patch("ees.gui.kusto_client.KustoClient._execute_query", return_value=mock_df):
            from ees.gui.kusto_client import KustoClient

            client = KustoClient(
                cluster="https://test.kusto.windows.net",
                database="TestDB",
            )
            result = client.fetch_incident("INC-12345")
            assert result == "Server is down and not responding."

    def test_fetch_not_found_raises(self) -> None:
        """TC-2: Returns RuntimeError when incident not found."""
        mock_df = MagicMock()
        mock_df.empty = True

        with patch("ees.gui.kusto_client.KustoClient._execute_query", return_value=mock_df):
            from ees.gui.kusto_client import KustoClient

            client = KustoClient(
                cluster="https://test.kusto.windows.net",
                database="TestDB",
            )
            with pytest.raises(RuntimeError, match="not found"):
                client.fetch_incident("INC-99999")

    def test_fetch_connection_error(self) -> None:
        """TC-3: Connection failure raises RuntimeError."""
        with patch(
            "ees.gui.kusto_client.KustoClient._execute_query",
            side_effect=Exception("Connection refused"),
        ):
            from ees.gui.kusto_client import KustoClient

            client = KustoClient(
                cluster="https://test.kusto.windows.net",
                database="TestDB",
            )
            with pytest.raises(RuntimeError, match="Kusto query failed"):
                client.fetch_incident("INC-12345")

    def test_fetch_empty_id_raises(self) -> None:
        """TC-4: Empty incident ID rejected with ValueError."""
        from ees.gui.kusto_client import KustoClient

        client = KustoClient(
            cluster="https://test.kusto.windows.net",
            database="TestDB",
        )
        with pytest.raises(ValueError, match="Incident ID"):
            client.fetch_incident("")

    def test_fetch_whitespace_only_id_raises(self) -> None:
        """TC-4b: Whitespace-only incident ID rejected."""
        from ees.gui.kusto_client import KustoClient

        client = KustoClient(
            cluster="https://test.kusto.windows.net",
            database="TestDB",
        )
        with pytest.raises(ValueError, match="Incident ID"):
            client.fetch_incident("   ")


# ── Settings Extension (Kusto) ────────────────────────────────


class TestSettingsManagerKusto:
    """TC-5 through TC-7: Kusto settings in SettingsManager."""

    def test_load_kusto_from_yaml(self, tmp_path: Path) -> None:
        """TC-5: Load Kusto settings from YAML file."""
        settings_file = tmp_path / "settings.yaml"
        settings_file.write_text(
            "azure_openai:\n"
            '  endpoint: "https://test.openai.azure.com/"\n'
            '  deployment: "gpt-4o"\n'
            '  api_version: "2025-01-01"\n'
            "kusto:\n"
            '  cluster: "https://custom.kusto.windows.net"\n'
            '  database: "CustomDB"\n'
        )
        from ees.gui.settings import SettingsManager

        mgr = SettingsManager(tmp_path)
        kusto = mgr.load_kusto()
        assert kusto["cluster"] == "https://custom.kusto.windows.net"
        assert kusto["database"] == "CustomDB"

    def test_load_kusto_defaults_when_no_config(self, tmp_path: Path) -> None:
        """TC-6: Returns Kusto defaults when no settings.yaml."""
        from ees.gui.settings import SettingsManager

        mgr = SettingsManager(tmp_path)
        kusto = mgr.load_kusto()
        assert kusto["cluster"] == "https://acciafollowercentralus.centralus.kusto.windows.net"
        assert kusto["database"] == "IcmDataWarehouse"

    def test_save_and_reload_kusto_roundtrip(self, tmp_path: Path) -> None:
        """TC-7: Save Kusto settings then load returns same values."""
        from ees.gui.settings import SettingsManager

        mgr = SettingsManager(tmp_path)
        kusto_settings = {
            "cluster": "https://roundtrip.kusto.windows.net",
            "database": "RoundTripDB",
        }
        mgr.save_kusto(kusto_settings)
        loaded = mgr.load_kusto()
        assert loaded == kusto_settings

    def test_save_kusto_preserves_openai_settings(self, tmp_path: Path) -> None:
        """Saving Kusto settings does not clobber Azure OpenAI settings."""
        from ees.gui.settings import SettingsManager

        mgr = SettingsManager(tmp_path)
        mgr.save({
            "endpoint": "https://existing.openai.azure.com/",
            "deployment": "gpt-4o",
            "api_version": "2025-01-01",
        })
        mgr.save_kusto({
            "cluster": "https://new.kusto.windows.net",
            "database": "NewDB",
        })
        # OpenAI settings should survive
        openai = mgr.load()
        assert openai["endpoint"] == "https://existing.openai.azure.com/"
        # Kusto settings should also be there
        kusto = mgr.load_kusto()
        assert kusto["cluster"] == "https://new.kusto.windows.net"
