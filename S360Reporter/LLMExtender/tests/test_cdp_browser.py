"""Tests for CDP browser auth (browser_auth='cdp') — LLM-0009 test cases."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from llm_extender.exceptions import ProviderError


# ===========================================================================
# TC-1: _find_edge_executable returns path on Windows
# ===========================================================================

class TestFindEdgeExecutable:
    def test_returns_path_from_which(self) -> None:
        """TC-1: When shutil.which finds msedge, return it."""
        from llm_extender.cdp_browser import _find_edge_executable

        with patch("shutil.which", return_value=r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"):
            result = _find_edge_executable()
        assert isinstance(result, Path)
        assert "msedge" in str(result).lower()

    def test_returns_path_from_program_files_fallback(self) -> None:
        """When shutil.which returns None, fall back to known paths."""
        from llm_extender.cdp_browser import _find_edge_executable

        with (
            patch("shutil.which", return_value=None),
            patch("pathlib.Path.exists", return_value=True),
        ):
            result = _find_edge_executable()
        assert isinstance(result, Path)

    # TC-2: raises when Edge not found
    def test_raises_when_not_found(self) -> None:
        """TC-2: ProviderError raised when Edge is not installed."""
        from llm_extender.cdp_browser import _find_edge_executable

        with (
            patch("shutil.which", return_value=None),
            patch("pathlib.Path.exists", return_value=False),
        ):
            with pytest.raises(ProviderError, match="[Ee]dge"):
                _find_edge_executable()


# ===========================================================================
# TC-3: _find_edge_user_data_dir
# ===========================================================================

class TestFindEdgeUserDataDir:
    def test_returns_correct_path(self) -> None:
        """TC-3: Returns LOCALAPPDATA-based Edge profile path."""
        from llm_extender.cdp_browser import _find_edge_user_data_dir

        with patch.dict(os.environ, {"LOCALAPPDATA": r"C:\Users\Test\AppData\Local"}):
            result = _find_edge_user_data_dir()
        assert isinstance(result, Path)
        assert "Edge" in str(result)
        assert "User Data" in str(result)


# ===========================================================================
# TC-6: "cdp" is in _VALID_BROWSER_AUTH
# ===========================================================================

class TestCdpInValidAuth:
    def test_cdp_in_valid_browser_auth(self) -> None:
        """TC-6: 'cdp' is a recognized browser_auth value."""
        from llm_extender.url_fetcher import _VALID_BROWSER_AUTH

        assert "cdp" in _VALID_BROWSER_AUTH


# ===========================================================================
# TC-4: fetch_url routes browser_auth="cdp" to CDP fetcher
# ===========================================================================

class TestFetchUrlRouting:
    def test_sync_routes_to_cdp_fetcher(self) -> None:
        """TC-4: fetch_url with browser_auth='cdp' calls _fetch_with_cdp_browser."""
        with patch("llm_extender.cdp_browser._fetch_with_cdp_browser", return_value="cdp content") as mock_cdp:
            from llm_extender.url_fetcher import fetch_url

            result = fetch_url(
                "https://example.com",
                render_js=True,
                browser_auth="cdp",
            )
        mock_cdp.assert_called_once()
        assert result == "cdp content"

    @pytest.mark.asyncio
    async def test_async_routes_to_cdp_fetcher(self) -> None:
        """TC-5: afetch_url with browser_auth='cdp' calls _afetch_with_cdp_browser."""
        with patch("llm_extender.cdp_browser._afetch_with_cdp_browser", new_callable=AsyncMock, return_value="cdp async") as mock_cdp:
            from llm_extender.url_fetcher import afetch_url

            result = await afetch_url(
                "https://example.com",
                render_js=True,
                browser_auth="cdp",
            )
        mock_cdp.assert_called_once()
        assert result == "cdp async"


# ===========================================================================
# TC-7: CDP fetch calls wait_for_aad_login when AAD redirect detected
# ===========================================================================

class TestCdpAADLoginWait:
    def test_calls_wait_for_aad_login_on_redirect(self) -> None:
        """TC-7: When page lands on AAD, wait_for_aad_login is called."""
        from llm_extender.cdp_browser import _fetch_with_cdp_browser

        # Build mock Playwright CDP chain
        mock_page = MagicMock()
        mock_page.inner_text.return_value = "Dashboard content"
        type(mock_page).url = PropertyMock(
            side_effect=[
                "https://login.microsoftonline.com/tenant/oauth2/authorize",
                "https://login.microsoftonline.com/tenant/oauth2/authorize",
                "https://myapp.example.com/dashboard",
            ]
        )

        mock_context = MagicMock()
        mock_context.pages = [mock_page]

        mock_browser = MagicMock()
        mock_browser.contexts = [mock_context]

        mock_pw = MagicMock()
        mock_pw.chromium.connect_over_cdp.return_value = mock_browser

        mock_launcher = MagicMock()
        mock_launcher.return_value.__enter__ = MagicMock(return_value=mock_pw)
        mock_launcher.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("llm_extender.cdp_browser._get_sync_playwright", return_value=mock_launcher),
            patch("llm_extender.cdp_browser._launch_edge_with_cdp"),
            patch("llm_extender.cdp_browser._wait_for_cdp_ready"),
            patch("llm_extender.cdp_browser.detect_aad_redirect", side_effect=[True, False]),
            patch("llm_extender.cdp_browser.wait_for_aad_login") as mock_wait,
        ):
            result = _fetch_with_cdp_browser(
                "https://myapp.example.com/dashboard",
                timeout=10.0,
            )

        assert result == "Dashboard content"
        mock_wait.assert_called_once()


# ===========================================================================
# TC-8: CDP fetch raises ProviderError when CDP connection fails
# ===========================================================================

class TestCdpConnectionFailure:
    def test_raises_on_cdp_connect_failure(self) -> None:
        """TC-8: ProviderError raised when CDP connection fails."""
        from llm_extender.cdp_browser import _fetch_with_cdp_browser

        mock_pw = MagicMock()
        mock_pw.chromium.connect_over_cdp.side_effect = Exception("Connection refused")

        mock_launcher = MagicMock()
        mock_launcher.return_value.__enter__ = MagicMock(return_value=mock_pw)
        mock_launcher.return_value.__exit__ = MagicMock(return_value=False)

        with (
            patch("llm_extender.cdp_browser._get_sync_playwright", return_value=mock_launcher),
            patch("llm_extender.cdp_browser._launch_edge_with_cdp"),
            patch("llm_extender.cdp_browser._wait_for_cdp_ready"),
        ):
            with pytest.raises(ProviderError, match="CDP|Edge|browser"):
                _fetch_with_cdp_browser(
                    "https://example.com",
                    timeout=10.0,
                )


# ===========================================================================
# TC-10: browser_auth="cdp" does not require auth parameter
# ===========================================================================

class TestCdpNoAuthRequired:
    def test_works_without_auth(self) -> None:
        """TC-10: browser_auth='cdp' works with auth=None."""
        # If we can call fetch_url with browser_auth="cdp" and auth=None
        # without an auth-related error, this passes.
        with patch("llm_extender.cdp_browser._fetch_with_cdp_browser", return_value="content"):
            from llm_extender.url_fetcher import fetch_url

            result = fetch_url(
                "https://example.com",
                render_js=True,
                browser_auth="cdp",
                auth=None,
            )
        assert result == "content"


# ===========================================================================
# TC-9: Existing browser_auth="aad" unchanged (regression)
# ===========================================================================

class TestExistingAADUnchanged:
    def test_aad_still_valid(self) -> None:
        """TC-9: 'aad' is still a valid browser_auth value."""
        from llm_extender.url_fetcher import _VALID_BROWSER_AUTH

        assert "aad" in _VALID_BROWSER_AUTH

    def test_invalid_still_rejected(self) -> None:
        """Regression: invalid browser_auth values still raise."""
        from llm_extender.url_fetcher import fetch_url

        with pytest.raises(ProviderError, match="Unsupported"):
            fetch_url("https://example.com", render_js=True, browser_auth="invalid")
