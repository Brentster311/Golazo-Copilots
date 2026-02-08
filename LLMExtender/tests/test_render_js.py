"""Tests for render_js support in URL fetcher — maps to LLM-0007 test cases."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_extender.exceptions import ProviderError


# ===========================================================================
# TC-1: render_js=False is default (no change from LLM-0006)
# ===========================================================================

class TestRenderJsDefault:
    def test_default_is_false(self) -> None:
        """TC-1: fetch_url without render_js uses httpx, not Playwright."""
        import inspect
        from llm_extender.url_fetcher import fetch_url

        sig = inspect.signature(fetch_url)
        assert sig.parameters["render_js"].default is False


# ===========================================================================
# TC-2: render_js=True launches browser and extracts text
# ===========================================================================

class TestRenderJsSync:
    def test_launches_browser_and_returns_text(self) -> None:
        """TC-2: render_js=True launches headless browser and extracts inner text."""
        mock_page = MagicMock()
        mock_page.inner_text.return_value = "Rendered SPA content"

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_pw_cm = MagicMock()
        mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
        mock_pw_cm.__exit__ = MagicMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.sync_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import fetch_url
            result = fetch_url("https://spa.example.com", render_js=True)

        assert result == "Rendered SPA content"
        mock_page.goto.assert_called_once()
        mock_page.inner_text.assert_called_once_with("body")
        mock_browser.close.assert_called_once()


# ===========================================================================
# TC-3: render_js=True async variant
# ===========================================================================

class TestRenderJsAsync:
    @pytest.mark.asyncio
    async def test_async_launches_browser_and_returns_text(self) -> None:
        """TC-3: afetch_url with render_js=True uses async Playwright."""
        mock_page = MagicMock()
        mock_page.inner_text = AsyncMock(return_value="Async SPA content")
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()

        mock_context = MagicMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = MagicMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_cm = MagicMock()
        mock_pw_cm.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_cm.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.async_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import afetch_url
            result = await afetch_url("https://spa.example.com", render_js=True)

        assert result == "Async SPA content"
        mock_browser.close.assert_awaited_once()


# ===========================================================================
# TC-4: Playwright not installed raises clear error (sync)
# ===========================================================================

class TestPlaywrightMissing:
    def test_sync_raises_with_install_instructions(self) -> None:
        """TC-4: Missing playwright gives helpful ProviderError."""
        with patch(
            "llm_extender.url_fetcher._import_sync_playwright",
            side_effect=ImportError("No module named 'playwright'"),
        ):
            from llm_extender.url_fetcher import fetch_url
            with pytest.raises(ProviderError, match="pip install llm-extender\\[browser\\]"):
                fetch_url("https://example.com", render_js=True)


# ===========================================================================
# TC-5: Playwright not installed (async variant)
# ===========================================================================

    @pytest.mark.asyncio
    async def test_async_raises_with_install_instructions(self) -> None:
        """TC-5: Missing playwright (async) gives helpful ProviderError."""
        with patch(
            "llm_extender.url_fetcher._import_async_playwright",
            side_effect=ImportError("No module named 'playwright'"),
        ):
            from llm_extender.url_fetcher import afetch_url
            with pytest.raises(ProviderError, match="pip install llm-extender\\[browser\\]"):
                await afetch_url("https://example.com", render_js=True)


# ===========================================================================
# TC-6: Auth token injected into browser context (sync)
# ===========================================================================

class TestBrowserAuth:
    def test_auth_injected_as_extra_http_header(self) -> None:
        """TC-6: Auth strategy token set as extra_http_headers on browser context."""
        mock_auth = MagicMock()
        mock_auth.resolve.return_value = "browser-token-123"

        mock_page = MagicMock()
        mock_page.inner_text.return_value = "Auth content"

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_pw_cm = MagicMock()
        mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
        mock_pw_cm.__exit__ = MagicMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.sync_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import fetch_url
            fetch_url("https://example.com", render_js=True, auth=mock_auth)

        # Verify extra_http_headers was passed to new_context
        call_kwargs = mock_browser.new_context.call_args
        headers = call_kwargs[1].get("extra_http_headers") or call_kwargs.kwargs.get("extra_http_headers")
        assert headers["Authorization"] == "Bearer browser-token-123"


# ===========================================================================
# TC-7: Auth token injected (async variant)
# ===========================================================================

    @pytest.mark.asyncio
    async def test_async_auth_injected(self) -> None:
        """TC-7: Async auth resolves via aresolve and injects into browser context."""
        mock_auth = MagicMock()
        mock_auth.aresolve = AsyncMock(return_value="async-browser-token")

        mock_page = MagicMock()
        mock_page.inner_text = AsyncMock(return_value="Auth content")
        mock_page.goto = AsyncMock()
        mock_page.wait_for_load_state = AsyncMock()

        mock_context = MagicMock()
        mock_context.new_page = AsyncMock(return_value=mock_page)

        mock_browser = MagicMock()
        mock_browser.new_context = AsyncMock(return_value=mock_context)
        mock_browser.close = AsyncMock()

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch = AsyncMock(return_value=mock_browser)

        mock_pw_cm = MagicMock()
        mock_pw_cm.__aenter__ = AsyncMock(return_value=mock_pw_instance)
        mock_pw_cm.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.async_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import afetch_url
            await afetch_url("https://example.com", render_js=True, auth=mock_auth)

        call_kwargs = mock_browser.new_context.call_args
        headers = call_kwargs[1].get("extra_http_headers") or call_kwargs.kwargs.get("extra_http_headers")
        assert headers["Authorization"] == "Bearer async-browser-token"


# ===========================================================================
# TC-8: Browser closed after fetch (resource cleanup)
# ===========================================================================

class TestBrowserCleanup:
    def test_browser_closed_on_success(self) -> None:
        """TC-8: Browser is closed after successful fetch."""
        mock_page = MagicMock()
        mock_page.inner_text.return_value = "Content"

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_pw_cm = MagicMock()
        mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
        mock_pw_cm.__exit__ = MagicMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.sync_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import fetch_url
            fetch_url("https://example.com", render_js=True)

        mock_browser.close.assert_called_once()

    def test_browser_closed_on_error(self) -> None:
        """TC-8: Browser is closed even if page navigation raises."""
        mock_page = MagicMock()
        mock_page.goto.side_effect = Exception("Navigation failed")

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_pw_cm = MagicMock()
        mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
        mock_pw_cm.__exit__ = MagicMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.sync_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import fetch_url
            with pytest.raises(ProviderError, match="Navigation failed"):
                fetch_url("https://example.com", render_js=True)

        mock_browser.close.assert_called_once()


# ===========================================================================
# TC-9: Content truncated to max_length
# ===========================================================================

class TestBrowserTruncation:
    def test_truncates_long_browser_content(self) -> None:
        """TC-9: Browser-rendered content is truncated to max_length."""
        long_text = "A" * 10000
        mock_page = MagicMock()
        mock_page.inner_text.return_value = long_text

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_pw_cm = MagicMock()
        mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
        mock_pw_cm.__exit__ = MagicMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.sync_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import fetch_url
            result = fetch_url("https://example.com", render_js=True, max_length=50)

        assert len(result) <= 50


# ===========================================================================
# TC-10: complete_with_url passes render_js through
# ===========================================================================

class TestClientRenderJsPassthrough:
    def test_complete_with_url_passes_render_js(self) -> None:
        """TC-10: complete_with_url forwards render_js to fetch_url."""
        from llm_extender import LLMClient, LLMConfig

        config = LLMConfig(provider="openai", model="test", api_key="fake")
        client = LLMClient(config)
        client._provider = MagicMock()
        client._provider.complete.return_value = "Summary"

        with patch("llm_extender.client.fetch_url") as mock_fetch:
            mock_fetch.return_value = "Fetched content"
            client.complete_with_url(
                prompt="Summarize",
                url="https://example.com",
                render_js=True,
            )
            mock_fetch.assert_called_once()
            call_kwargs = mock_fetch.call_args
            assert call_kwargs.kwargs.get("render_js") is True or (
                len(call_kwargs.args) > 1 and call_kwargs.args[1] is True
            )


# ===========================================================================
# TC-11: acomplete_with_url passes render_js through
# ===========================================================================

    @pytest.mark.asyncio
    async def test_acomplete_with_url_passes_render_js(self) -> None:
        """TC-11: acomplete_with_url forwards render_js to afetch_url."""
        from llm_extender import LLMClient, LLMConfig

        config = LLMConfig(provider="openai", model="test", api_key="fake")
        client = LLMClient(config)
        client._provider = MagicMock()
        client._provider.acomplete = AsyncMock(return_value="Summary")

        with patch("llm_extender.client.afetch_url", new_callable=AsyncMock) as mock_afetch:
            mock_afetch.return_value = "Fetched content"
            await client.acomplete_with_url(
                prompt="Summarize",
                url="https://example.com",
                render_js=True,
            )
            mock_afetch.assert_called_once()
            call_kwargs = mock_afetch.call_args
            assert call_kwargs.kwargs.get("render_js") is True


# ===========================================================================
# TC-12: Timeout passed to browser
# ===========================================================================

class TestBrowserTimeout:
    def test_timeout_passed_to_browser_launch(self) -> None:
        """TC-12: Timeout value is forwarded to Playwright browser and page."""
        mock_page = MagicMock()
        mock_page.inner_text.return_value = "Content"

        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page

        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context

        mock_pw_instance = MagicMock()
        mock_pw_instance.chromium.launch.return_value = mock_browser

        mock_pw_cm = MagicMock()
        mock_pw_cm.__enter__ = MagicMock(return_value=mock_pw_instance)
        mock_pw_cm.__exit__ = MagicMock(return_value=False)

        with patch(
            "llm_extender.url_fetcher.sync_playwright",
            return_value=mock_pw_cm,
        ):
            from llm_extender.url_fetcher import fetch_url
            fetch_url("https://example.com", render_js=True, timeout=15.0)

        # page.goto should receive timeout in ms
        goto_kwargs = mock_page.goto.call_args
        assert goto_kwargs.kwargs.get("timeout") == 15000.0


# ===========================================================================
# TC-13: Docstrings mention render_js
# ===========================================================================

class TestRenderJsDocstrings:
    def test_fetch_url_docstring_mentions_render_js(self) -> None:
        """TC-13: fetch_url docstring documents render_js."""
        from llm_extender.url_fetcher import fetch_url
        assert "render_js" in fetch_url.__doc__

    def test_afetch_url_docstring_mentions_render_js(self) -> None:
        """TC-13: afetch_url docstring documents render_js."""
        from llm_extender.url_fetcher import afetch_url
        assert "render_js" in afetch_url.__doc__
