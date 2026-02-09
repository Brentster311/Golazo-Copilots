"""Tests for wait_for_aad_login / await_for_aad_login — LLM-0010 test cases."""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from llm_extender.auth.aad_browser import (
    _AAD_HOSTS,
    await_for_aad_login,
    wait_for_aad_login,
)
from llm_extender.exceptions import AuthenticationError


# ===========================================================================
# TC-1: wait_for_aad_login returns when URL leaves AAD
# ===========================================================================

class TestWaitForAADLoginSync:
    def test_returns_when_url_leaves_aad(self) -> None:
        """TC-1: Sync wait returns once page.url no longer points to AAD."""
        page = MagicMock()
        # First call → AAD host, second call → target site
        type(page).url = PropertyMock(
            side_effect=[
                "https://login.microsoftonline.com/tenant/oauth2/authorize",
                "https://login.microsoftonline.com/tenant/oauth2/authorize",
                "https://myapp.example.com/dashboard",
            ]
        )

        # Should return without raising (poll_interval kept tiny for speed)
        wait_for_aad_login(page, timeout=5.0, poll_interval=0.01)

    def test_returns_immediately_if_not_on_aad(self) -> None:
        """Edge case: page already off AAD — returns immediately."""
        page = MagicMock()
        type(page).url = PropertyMock(
            return_value="https://myapp.example.com/dashboard"
        )

        wait_for_aad_login(page, timeout=5.0, poll_interval=0.01)

    def test_recognises_all_aad_hosts(self) -> None:
        """Ensure all known AAD hosts are treated as 'still logging in'."""
        for host in _AAD_HOSTS:
            page = MagicMock()
            type(page).url = PropertyMock(
                side_effect=[
                    f"https://{host}/tenant/authorize",
                    "https://target.example.com/ok",
                ]
            )
            wait_for_aad_login(page, timeout=5.0, poll_interval=0.01)


# ===========================================================================
# TC-2: wait_for_aad_login raises AuthenticationError on timeout
# ===========================================================================

class TestWaitForAADLoginTimeout:
    def test_raises_on_timeout(self) -> None:
        """TC-2: AuthenticationError raised when page stays on AAD past timeout."""
        page = MagicMock()
        type(page).url = PropertyMock(
            return_value="https://login.microsoftonline.com/tenant/oauth2/authorize"
        )

        with pytest.raises(AuthenticationError, match="timed out"):
            wait_for_aad_login(page, timeout=0.05, poll_interval=0.01)

    def test_error_message_includes_timeout_seconds(self) -> None:
        """The error message should mention the timeout value."""
        page = MagicMock()
        type(page).url = PropertyMock(
            return_value="https://login.microsoftonline.com/tenant/oauth2/authorize"
        )

        with pytest.raises(AuthenticationError, match="0.05"):
            wait_for_aad_login(page, timeout=0.05, poll_interval=0.01)


# ===========================================================================
# TC-3: await_for_aad_login async variant
# ===========================================================================

class TestAwaitForAADLoginAsync:
    @pytest.mark.asyncio
    async def test_returns_when_url_leaves_aad(self) -> None:
        """TC-3: Async wait returns once page.url no longer points to AAD."""
        page = AsyncMock()
        type(page).url = PropertyMock(
            side_effect=[
                "https://login.microsoftonline.com/tenant/oauth2/authorize",
                "https://login.microsoftonline.com/tenant/oauth2/authorize",
                "https://myapp.example.com/dashboard",
            ]
        )

        await await_for_aad_login(page, timeout=5.0, poll_interval=0.01)

    @pytest.mark.asyncio
    async def test_raises_on_timeout(self) -> None:
        """Async wait raises AuthenticationError when page stays on AAD."""
        page = AsyncMock()
        type(page).url = PropertyMock(
            return_value="https://login.microsoftonline.com/tenant/oauth2/authorize"
        )

        with pytest.raises(AuthenticationError, match="timed out"):
            await await_for_aad_login(page, timeout=0.05, poll_interval=0.01)

    @pytest.mark.asyncio
    async def test_returns_immediately_if_not_on_aad(self) -> None:
        """Async: page already off AAD — returns immediately."""
        page = AsyncMock()
        type(page).url = PropertyMock(
            return_value="https://myapp.example.com/dashboard"
        )

        await await_for_aad_login(page, timeout=5.0, poll_interval=0.01)


# ===========================================================================
# TC-4: Regression — existing _fetch_with_browser still works
# ===========================================================================

class TestFetchWithBrowserRegression:
    """Ensure the refactored _fetch_with_browser still calls wait_for_aad_login."""

    def test_sync_fetch_calls_wait_for_aad_login(self) -> None:
        """After device-code flow, _fetch_with_browser should call wait_for_aad_login."""
        # Build mock Playwright chain
        mock_page = MagicMock()
        mock_page.inner_text.return_value = "Hello, World!"
        type(mock_page).url = PropertyMock(
            side_effect=[
                # First goto → AAD redirect detected
                "https://login.microsoftonline.com/tenant/oauth2/authorize?client_id=abc&scope=openid",
                # After device code + re-navigate → the wait_for_aad_login will see this
                "https://myapp.example.com/dashboard",
            ]
        )

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context

        mock_pw = MagicMock()
        mock_pw.chromium.launch.return_value = mock_browser

        mock_launcher = MagicMock()
        mock_launcher.return_value.__enter__ = MagicMock(return_value=mock_pw)
        mock_launcher.return_value.__exit__ = MagicMock(return_value=False)

        mock_auth = MagicMock()
        mock_auth.resolve.return_value = "fake-token"

        with (
            patch("llm_extender.url_fetcher._get_sync_playwright", return_value=mock_launcher),
            patch("llm_extender.auth.aad_browser.is_user_credential", return_value=True),
            patch("llm_extender.auth.aad_browser.run_device_code_flow", return_value={"access_token": "new-token"}),
            patch("llm_extender.auth.aad_browser.wait_for_aad_login") as mock_wait,
        ):
            from llm_extender.url_fetcher import _fetch_with_browser

            result = _fetch_with_browser(
                "https://myapp.example.com/dashboard",
                auth=mock_auth,
                browser_auth="aad",
                timeout=10.0,
            )

        assert result == "Hello, World!"
        mock_wait.assert_called_once()
