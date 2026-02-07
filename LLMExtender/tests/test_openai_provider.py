"""Tests for OpenAIProvider — maps to LLM-0001 test cases TC-8, TC-9."""

import httpx
import pytest
import respx

from llm_extender.config import LLMConfig
from llm_extender.providers.openai import OpenAIProvider
from llm_extender.exceptions import ProviderError

from conftest import MOCK_OPENAI_RESPONSE


@pytest.fixture
def provider() -> OpenAIProvider:
    """An OpenAIProvider for testing."""
    config = LLMConfig(provider="openai", model="gpt-4", api_key="test-key", base_url=None)
    return OpenAIProvider(config)


@pytest.fixture
def provider_custom_url() -> OpenAIProvider:
    """An OpenAIProvider with custom base_url."""
    config = LLMConfig(provider="openai", model="gpt-4", api_key="test-key", base_url="https://custom.api.com")
    return OpenAIProvider(config)


# --- TC-8: OpenAIProvider.complete() sends correct HTTP request ---

class TestSyncHTTPRequest:
    @respx.mock
    def test_complete_posts_to_correct_endpoint(self, provider: OpenAIProvider) -> None:
        """TC-8: POST sent to /v1/chat/completions with correct payload."""
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        provider.complete("test prompt")
        assert route.called, "OpenAIProvider should POST to /v1/chat/completions"

        request = route.calls[0].request
        import json
        body = json.loads(request.content)
        assert body["model"] == "gpt-4", "Request should include the model name"
        assert body["messages"] == [{"role": "user", "content": "test prompt"}], (
            "Request should wrap prompt as a user message"
        )

    @respx.mock
    def test_complete_sends_auth_header(self, provider: OpenAIProvider) -> None:
        """TC-8: Authorization header should be sent."""
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        provider.complete("test")
        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer test-key", (
            "Authorization header should contain the API key"
        )

    @respx.mock
    def test_complete_uses_custom_base_url(self, provider_custom_url: OpenAIProvider) -> None:
        """TC-8: Custom base_url should be used."""
        route = respx.post("https://custom.api.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        provider_custom_url.complete("test")
        assert route.called, "Should use custom base_url"


# --- TC-9: OpenAIProvider.acomplete() sends correct async HTTP request ---

class TestAsyncHTTPRequest:
    @respx.mock
    async def test_acomplete_posts_to_correct_endpoint(self, provider: OpenAIProvider) -> None:
        """TC-9: Async POST sent to /v1/chat/completions with correct payload."""
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        result = await provider.acomplete("test prompt")
        assert route.called, "OpenAIProvider async should POST to /v1/chat/completions"
        assert result == "Hello", f"acomplete() should return 'Hello', got '{result}'"

    @respx.mock
    async def test_acomplete_sends_auth_header(self, provider: OpenAIProvider) -> None:
        """TC-9: Async authorization header should be sent."""
        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        await provider.acomplete("test")
        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer test-key"


# --- Error handling ---

class TestProviderErrors:
    @respx.mock
    def test_401_raises_provider_error(self, provider: OpenAIProvider) -> None:
        """401 response should raise ProviderError."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(401, json={"error": {"message": "Unauthorized"}})
        )
        with pytest.raises(ProviderError, match="401"):
            provider.complete("test")

    @respx.mock
    def test_429_raises_provider_error(self, provider: OpenAIProvider) -> None:
        """429 rate limit should raise ProviderError."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(429, json={"error": {"message": "Rate limited"}})
        )
        with pytest.raises(ProviderError, match="429"):
            provider.complete("test")

    @respx.mock
    async def test_async_500_raises_provider_error(self, provider: OpenAIProvider) -> None:
        """Async 500 should raise ProviderError."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(500, json={"error": {"message": "Server error"}})
        )
        with pytest.raises(ProviderError):
            await provider.acomplete("test")
