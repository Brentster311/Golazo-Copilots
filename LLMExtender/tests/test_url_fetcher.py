"""Tests for URL content fetcher — maps to LLM-0006 test cases."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
import respx

from llm_extender.exceptions import ProviderError


# ===========================================================================
# TC-1: fetch_url returns text content from HTML
# ===========================================================================

class TestFetchURLBasic:
    def test_returns_text_from_html(self) -> None:
        """TC-1: fetch_url strips HTML tags and returns text."""
        from llm_extender.url_fetcher import fetch_url

        html = "<html><body><p>Hello world</p></body></html>"
        with respx.mock:
            respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text=html)
            )
            result = fetch_url("https://example.com")
        assert "Hello world" in result


# ===========================================================================
# TC-2: fetch_url strips script and style tags
# ===========================================================================

class TestStripScriptStyle:
    def test_strips_script_tags(self) -> None:
        """TC-2: Script content should be removed."""
        from llm_extender.url_fetcher import fetch_url

        html = "<html><body><script>var x=1;</script><p>Visible</p></body></html>"
        with respx.mock:
            respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text=html)
            )
            result = fetch_url("https://example.com")
        assert "var x=1" not in result
        assert "Visible" in result

    def test_strips_style_tags(self) -> None:
        """TC-2: Style content should be removed."""
        from llm_extender.url_fetcher import fetch_url

        html = "<html><body><style>body{color:red}</style><p>Visible</p></body></html>"
        with respx.mock:
            respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text=html)
            )
            result = fetch_url("https://example.com")
        assert "color:red" not in result
        assert "Visible" in result


# ===========================================================================
# TC-3: fetch_url sends Bearer token when auth provided
# ===========================================================================

class TestAuthHeader:
    def test_sends_bearer_token(self) -> None:
        """TC-3: When auth is provided, Bearer token is sent."""
        from llm_extender.url_fetcher import fetch_url

        mock_auth = MagicMock()
        mock_auth.resolve.return_value = "my-secret-token"

        with respx.mock:
            route = respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text="<p>OK</p>")
            )
            fetch_url("https://example.com", auth=mock_auth)

            request = route.calls[0].request
            assert request.headers["authorization"] == "Bearer my-secret-token"


# ===========================================================================
# TC-4: fetch_url with no auth sends no Authorization header
# ===========================================================================

class TestNoAuth:
    def test_no_auth_header(self) -> None:
        """TC-4: Without auth, no Authorization header is sent."""
        from llm_extender.url_fetcher import fetch_url

        with respx.mock:
            route = respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text="<p>OK</p>")
            )
            fetch_url("https://example.com")

            request = route.calls[0].request
            assert "authorization" not in request.headers


# ===========================================================================
# TC-5: fetch_url raises on HTTP error (404)
# ===========================================================================

class TestHTTPError:
    def test_raises_on_404(self) -> None:
        """TC-5: ProviderError on 404."""
        from llm_extender.url_fetcher import fetch_url

        with respx.mock:
            respx.get("https://example.com/missing").mock(
                return_value=httpx.Response(404, text="Not Found")
            )
            with pytest.raises(ProviderError, match="404"):
                fetch_url("https://example.com/missing")


# ===========================================================================
# TC-6: fetch_url raises on 401/403
# ===========================================================================

class TestAuthError:
    def test_raises_on_401(self) -> None:
        """TC-6: ProviderError on 401."""
        from llm_extender.url_fetcher import fetch_url

        with respx.mock:
            respx.get("https://example.com/secret").mock(
                return_value=httpx.Response(401, text="Unauthorized")
            )
            with pytest.raises(ProviderError, match="401"):
                fetch_url("https://example.com/secret")

    def test_raises_on_403(self) -> None:
        """TC-6: ProviderError on 403."""
        from llm_extender.url_fetcher import fetch_url

        with respx.mock:
            respx.get("https://example.com/forbidden").mock(
                return_value=httpx.Response(403, text="Forbidden")
            )
            with pytest.raises(ProviderError, match="403"):
                fetch_url("https://example.com/forbidden")


# ===========================================================================
# TC-7: fetch_url truncates to max_length
# ===========================================================================

class TestTruncation:
    def test_truncates_long_content(self) -> None:
        """TC-7: Content is truncated to max_length."""
        from llm_extender.url_fetcher import fetch_url

        long_text = "A" * 10000
        html = f"<html><body><p>{long_text}</p></body></html>"
        with respx.mock:
            respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text=html)
            )
            result = fetch_url("https://example.com", max_length=100)
        assert len(result) <= 100


# ===========================================================================
# TC-8: fetch_url uses httpx
# ===========================================================================

class TestUsesHttpx:
    def test_uses_httpx(self) -> None:
        """TC-8: Verify httpx is used (respx only intercepts httpx)."""
        from llm_extender.url_fetcher import fetch_url

        with respx.mock:
            respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text="<p>OK</p>")
            )
            # If this works with respx, it's using httpx
            result = fetch_url("https://example.com")
        assert "OK" in result


# ===========================================================================
# TC-9: complete_with_url builds correct prompt
# ===========================================================================

class TestCompleteWithURL:
    def test_prompt_includes_url_content_and_user_prompt(self) -> None:
        """TC-9: complete_with_url injects URL content into prompt."""
        from llm_extender.url_fetcher import fetch_url

        html = "<html><body><p>Page content here</p></body></html>"
        with respx.mock:
            respx.get("https://example.com/page").mock(
                return_value=httpx.Response(200, text=html)
            )

            # Mock the provider's complete method
            from llm_extender import LLMClient, LLMConfig
            config = LLMConfig(provider="openai", model="test", api_key="fake")
            client = LLMClient(config)
            client._provider = MagicMock()
            client._provider.complete.return_value = "Summary result"

            result = client.complete_with_url(
                prompt="Summarize this",
                url="https://example.com/page",
            )

            # Verify the assembled prompt
            call_args = client._provider.complete.call_args[0][0]
            assert "Page content here" in call_args
            assert "Summarize this" in call_args
            assert "https://example.com/page" in call_args
            assert result == "Summary result"


# ===========================================================================
# TC-10: complete_with_url passes url_auth to fetch
# ===========================================================================

class TestURLAuthSeparation:
    def test_url_auth_used_for_fetch_not_llm(self) -> None:
        """TC-10: url_auth is used for the URL fetch, not the LLM call."""
        mock_url_auth = MagicMock()
        mock_url_auth.resolve.return_value = "url-token"

        html = "<html><body><p>Content</p></body></html>"
        with respx.mock:
            route = respx.get("https://example.com/page").mock(
                return_value=httpx.Response(200, text=html)
            )

            from llm_extender import LLMClient, LLMConfig
            config = LLMConfig(provider="openai", model="test", api_key="llm-key")
            client = LLMClient(config)
            client._provider = MagicMock()
            client._provider.complete.return_value = "OK"

            client.complete_with_url(
                prompt="Test",
                url="https://example.com/page",
                url_auth=mock_url_auth,
            )

            # URL fetch should have Bearer token from url_auth
            request = route.calls[0].request
            assert request.headers["authorization"] == "Bearer url-token"


# ===========================================================================
# TC-11: acomplete_with_url async variant
# ===========================================================================

class TestAsyncCompleteWithURL:
    @pytest.mark.asyncio
    async def test_acomplete_with_url(self) -> None:
        """TC-11: acomplete_with_url works asynchronously."""
        html = "<html><body><p>Async content</p></body></html>"
        with respx.mock:
            respx.get("https://example.com/async").mock(
                return_value=httpx.Response(200, text=html)
            )

            from llm_extender import LLMClient, LLMConfig
            config = LLMConfig(provider="openai", model="test", api_key="fake")
            client = LLMClient(config)
            client._provider = MagicMock()
            client._provider.acomplete = AsyncMock(return_value="Async result")

            result = await client.acomplete_with_url(
                prompt="Summarize",
                url="https://example.com/async",
            )

            assert result == "Async result"
            call_args = client._provider.acomplete.call_args[0][0]
            assert "Async content" in call_args


# ===========================================================================
# TC-12: fetch_url sets User-Agent header
# ===========================================================================

class TestUserAgent:
    def test_user_agent_set(self) -> None:
        """TC-12: User-Agent header contains LLMExtender."""
        from llm_extender.url_fetcher import fetch_url

        with respx.mock:
            route = respx.get("https://example.com").mock(
                return_value=httpx.Response(200, text="<p>OK</p>")
            )
            fetch_url("https://example.com")
            request = route.calls[0].request
            assert "LLMExtender" in request.headers.get("user-agent", "")


# ===========================================================================
# TC-13: fetch_url handles plain text content
# ===========================================================================

class TestPlainText:
    def test_plain_text_returned_as_is(self) -> None:
        """TC-13: Plain text response returned without HTML processing errors."""
        from llm_extender.url_fetcher import fetch_url

        with respx.mock:
            respx.get("https://example.com/data.txt").mock(
                return_value=httpx.Response(
                    200,
                    text="Just plain text, no HTML.",
                    headers={"content-type": "text/plain"},
                )
            )
            result = fetch_url("https://example.com/data.txt")
        assert "Just plain text, no HTML." in result


# ===========================================================================
# TC-14: Docstrings present
# ===========================================================================

class TestDocstrings:
    def test_fetch_url_has_docstring(self) -> None:
        """TC-14: fetch_url has a docstring."""
        from llm_extender.url_fetcher import fetch_url
        assert fetch_url.__doc__ is not None

    def test_afetch_url_has_docstring(self) -> None:
        """TC-14: afetch_url has a docstring."""
        from llm_extender.url_fetcher import afetch_url
        assert afetch_url.__doc__ is not None

    def test_complete_with_url_has_docstring(self) -> None:
        """TC-14: complete_with_url has a docstring."""
        from llm_extender import LLMClient
        assert LLMClient.complete_with_url.__doc__ is not None

    def test_acomplete_with_url_has_docstring(self) -> None:
        """TC-14: acomplete_with_url has a docstring."""
        from llm_extender import LLMClient
        assert LLMClient.acomplete_with_url.__doc__ is not None
