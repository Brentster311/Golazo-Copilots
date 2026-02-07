"""Tests for SFI-018: In-App Azure Login with chained credentials.

Tests the credential chain: AzureCliCredential -> InteractiveBrowserCredential.
"""

import logging
from unittest.mock import MagicMock, patch

import pytest
from azure.core.credentials import AccessToken
from azure.core.exceptions import ClientAuthenticationError


# ---------------------------------------------------------------------------
# TC-01: CLI credential succeeds — no fallback
# ---------------------------------------------------------------------------
class TestCliCredentialSucceeds:
    """When AzureCliCredential works, InteractiveBrowserCredential is never used."""

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_s360_token_uses_cli_only(self, mock_cli_cls, mock_browser_cls):
        """TC-01a: get_s360_token uses CLI credential when available."""
        from accia_s360.auth import AuthManager

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.return_value = AccessToken("cli-s360-token", 9999999999)

        mgr = AuthManager()
        token = mgr.get_s360_token()

        assert token == "cli-s360-token"
        mock_cli.get_token.assert_called_once()
        mock_browser_cls.return_value.get_token.assert_not_called()

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_graph_token_uses_cli_only(self, mock_cli_cls, mock_browser_cls):
        """TC-01b: get_graph_token uses CLI credential when available."""
        from accia_s360.auth import AuthManager

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.return_value = AccessToken("cli-graph-token", 9999999999)

        mgr = AuthManager()
        token = mgr.get_graph_token()

        assert token == "cli-graph-token"
        mock_cli.get_token.assert_called_once()
        mock_browser_cls.return_value.get_token.assert_not_called()

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_logs_cli_success(self, mock_cli_cls, mock_browser_cls, caplog):
        """TC-01c: Logs that AzureCliCredential succeeded."""
        from accia_s360.auth import AuthManager

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.return_value = AccessToken("tok", 9999999999)

        mgr = AuthManager()
        with caplog.at_level(logging.DEBUG, logger="accia_s360.auth"):
            mgr.get_s360_token()

        assert any("AzureCliCredential" in m and "succeeded" in m.lower()
                    for m in caplog.messages), (
            f"Expected log about CLI success, got: {caplog.messages}"
        )


# ---------------------------------------------------------------------------
# TC-02: CLI fails — falls back to interactive browser
# ---------------------------------------------------------------------------
class TestFallbackToBrowser:
    """When CLI credential fails, browser credential is used."""

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_falls_back_to_browser(self, mock_cli_cls, mock_browser_cls):
        """TC-02a: Falls back to InteractiveBrowserCredential on CLI failure."""
        from accia_s360.auth import AuthManager

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.side_effect = ClientAuthenticationError(
            "Azure CLI not found"
        )

        mock_browser = mock_browser_cls.return_value
        mock_browser.get_token.return_value = AccessToken("browser-token", 9999999999)

        mgr = AuthManager()
        token = mgr.get_s360_token()

        assert token == "browser-token"
        mock_browser.get_token.assert_called_once()

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_logs_fallback(self, mock_cli_cls, mock_browser_cls, caplog):
        """TC-02b: Logs fallback to browser credential."""
        from accia_s360.auth import AuthManager

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.side_effect = ClientAuthenticationError("no az")

        mock_browser = mock_browser_cls.return_value
        mock_browser.get_token.return_value = AccessToken("tok", 9999999999)

        mgr = AuthManager()
        with caplog.at_level(logging.DEBUG, logger="accia_s360.auth"):
            mgr.get_s360_token()

        log_text = " ".join(caplog.messages).lower()
        assert "interactive" in log_text or "browser" in log_text or "fallback" in log_text, (
            f"Expected fallback log, got: {caplog.messages}"
        )


# ---------------------------------------------------------------------------
# TC-03: Both credentials fail — error surfaces
# ---------------------------------------------------------------------------
class TestBothCredentialsFail:
    """When both credentials fail, a clear error is raised."""

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_raises_auth_error(self, mock_cli_cls, mock_browser_cls):
        """TC-03: S360AuthError is raised when all credentials fail."""
        from accia_s360.auth import AuthManager
        from accia_s360.exceptions import S360AuthError

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.side_effect = ClientAuthenticationError("no az")

        mock_browser = mock_browser_cls.return_value
        mock_browser.get_token.side_effect = ClientAuthenticationError(
            "user cancelled"
        )

        mgr = AuthManager()
        with pytest.raises(S360AuthError):
            mgr.get_s360_token()

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_logs_failure(self, mock_cli_cls, mock_browser_cls, caplog):
        """TC-03b: Logs auth failure."""
        from accia_s360.auth import AuthManager
        from accia_s360.exceptions import S360AuthError

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.side_effect = ClientAuthenticationError("no az")

        mock_browser = mock_browser_cls.return_value
        mock_browser.get_token.side_effect = ClientAuthenticationError("cancelled")

        mgr = AuthManager()
        with caplog.at_level(logging.DEBUG, logger="accia_s360.auth"):
            with pytest.raises(S360AuthError):
                mgr.get_s360_token()

        log_text = " ".join(caplog.messages).lower()
        assert "failed" in log_text or "error" in log_text, (
            f"Expected failure log, got: {caplog.messages}"
        )


# ---------------------------------------------------------------------------
# TC-05: LAUNCHME.ps1 removed
# ---------------------------------------------------------------------------
class TestLaunchMeRemoved:
    """LAUNCHME.ps1 no longer exists and is not referenced in build manifest."""

    def test_launchme_does_not_exist(self):
        """TC-05a: LAUNCHME.ps1 file does not exist."""
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent  # SFIAgent/
        launchme = repo_root / "SFIReporter" / "LAUNCHME.ps1"
        assert not launchme.exists(), f"LAUNCHME.ps1 should be deleted: {launchme}"

    def test_build_manifest_no_launchme(self):
        """TC-05b: BUILD_MANIFEST.md does not reference LAUNCHME.ps1."""
        from pathlib import Path

        repo_root = Path(__file__).parent.parent.parent
        manifest = repo_root / "SFIReporter" / "BUILD_MANIFEST.md"
        if manifest.exists():
            content = manifest.read_text()
            assert "LAUNCHME" not in content, (
                "BUILD_MANIFEST.md still references LAUNCHME.ps1"
            )


# ---------------------------------------------------------------------------
# TC-09: Both scopes use the same credential chain
# ---------------------------------------------------------------------------
class TestBothScopesWork:
    """S360 and Graph tokens both go through the credential chain."""

    @patch("accia_s360.auth.InteractiveBrowserCredential")
    @patch("accia_s360.auth.AzureCliCredential")
    def test_both_scopes_through_chain(self, mock_cli_cls, mock_browser_cls):
        """TC-09: get_s360_token and get_graph_token use the same credential."""
        from accia_s360.auth import AuthManager

        mock_cli = mock_cli_cls.return_value
        mock_cli.get_token.return_value = AccessToken("tok", 9999999999)

        mgr = AuthManager()
        s360_tok = mgr.get_s360_token()
        graph_tok = mgr.get_graph_token()

        assert s360_tok == "tok"
        assert graph_tok == "tok"
        assert mock_cli.get_token.call_count == 2

        # Verify different scopes were requested
        calls = mock_cli.get_token.call_args_list
        scopes = [c[0][0] for c in calls]
        assert any("Service360" in s for s in scopes)
        assert any("graph.microsoft.com" in s for s in scopes)
