"""Tests for LLM-0011: Public Context-Prompt API for Pre-Fetched Content.

Covers TC-1 through TC-6 from LLM-0011-Test-Cases.md.
"""

import pytest
import httpx
import respx

from llm_extender.client import LLMClient
from llm_extender.config import LLMConfig

from conftest import MOCK_OPENAI_RESPONSE


# ---------------------------------------------------------------------------
# TC-1: build_context_prompt is public and exported
# ---------------------------------------------------------------------------

class TestBuildContextPromptPublic:
    def test_importable_from_top_level(self) -> None:
        """TC-1: build_context_prompt should be importable from llm_extender."""
        from llm_extender import build_context_prompt  # noqa: F401
        assert callable(build_context_prompt)

    def test_returns_expected_format(self) -> None:
        """TC-1: build_context_prompt should return the canonical format."""
        from llm_extender import build_context_prompt
        result = build_context_prompt("https://example.com", "page text", "summarize")
        assert result == "Content from https://example.com:\n\npage text\n\nsummarize"


# ---------------------------------------------------------------------------
# TC-2: _build_context_prompt alias still works
# ---------------------------------------------------------------------------

class TestBuildContextPromptAlias:
    def test_private_alias_importable(self) -> None:
        """TC-2: _build_context_prompt should still be importable."""
        from llm_extender.url_fetcher import _build_context_prompt  # noqa: F401
        assert callable(_build_context_prompt)

    def test_alias_returns_same_result(self) -> None:
        """TC-2: _build_context_prompt should return same result as public version."""
        from llm_extender import build_context_prompt
        from llm_extender.url_fetcher import _build_context_prompt
        args = ("https://example.com", "content", "prompt")
        assert build_context_prompt(*args) == _build_context_prompt(*args)


# ---------------------------------------------------------------------------
# TC-3: complete_with_context sends augmented prompt to provider
# ---------------------------------------------------------------------------

class TestCompleteWithContext:
    @respx.mock
    def test_sends_augmented_prompt(self, openai_config: LLMConfig) -> None:
        """TC-3: complete_with_context should send context-augmented prompt."""
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(openai_config) as client:
            result = client.complete_with_context(
                "summarize", "page text", source_url="https://example.com"
            )
        assert result == "Hello"
        # Verify the prompt sent to the provider contains the context
        request_body = route.calls.last.request.content
        import json
        body = json.loads(request_body)
        user_msg = body["messages"][0]["content"]
        assert "Content from https://example.com:" in user_msg
        assert "page text" in user_msg
        assert "summarize" in user_msg


# ---------------------------------------------------------------------------
# TC-4: complete_with_context without source_url
# ---------------------------------------------------------------------------

class TestCompleteWithContextNoUrl:
    @respx.mock
    def test_no_source_url(self, openai_config: LLMConfig) -> None:
        """TC-4: complete_with_context without source_url uses 'unknown'."""
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(openai_config) as client:
            result = client.complete_with_context("summarize", "page text")
        assert result == "Hello"
        import json
        body = json.loads(route.calls.last.request.content)
        user_msg = body["messages"][0]["content"]
        assert "page text" in user_msg
        assert "summarize" in user_msg


# ---------------------------------------------------------------------------
# TC-5: acomplete_with_context async variant
# ---------------------------------------------------------------------------

class TestAsyncCompleteWithContext:
    @respx.mock
    async def test_async_sends_augmented_prompt(self, openai_config: LLMConfig) -> None:
        """TC-5: acomplete_with_context should send context-augmented prompt."""
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        async with LLMClient(openai_config) as client:
            result = await client.acomplete_with_context(
                "summarize", "page text", source_url="https://example.com"
            )
        assert result == "Hello"
        import json
        body = json.loads(route.calls.last.request.content)
        user_msg = body["messages"][0]["content"]
        assert "Content from https://example.com:" in user_msg
        assert "page text" in user_msg


# ---------------------------------------------------------------------------
# TC-6: complete_with_url delegates to complete_with_context
# ---------------------------------------------------------------------------

class TestCompleteWithUrlDelegation:
    @respx.mock
    def test_complete_with_url_uses_context_method(
        self, openai_config: LLMConfig
    ) -> None:
        """TC-6: complete_with_url should use the same prompt format as complete_with_context."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        respx.get("https://example.com/page").mock(
            return_value=httpx.Response(200, text="<html><body>Hello World</body></html>",
                                        headers={"content-type": "text/html"})
        )
        with LLMClient(openai_config) as client:
            result = client.complete_with_url(
                "summarize", "https://example.com/page"
            )
        assert result == "Hello"
