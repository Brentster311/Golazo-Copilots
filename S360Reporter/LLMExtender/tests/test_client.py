"""Tests for LLMClient — maps to LLM-0001 test cases TC-1 through TC-7, TC-10, TC-11."""

import pytest
import httpx
import respx

from llm_extender.client import LLMClient
from llm_extender.config import LLMConfig
from llm_extender.providers.base import LLMProvider
from llm_extender.providers.openai import OpenAIProvider
from llm_extender.exceptions import UnsupportedProviderError, ProviderError, LLMExtenderError

from conftest import MOCK_OPENAI_RESPONSE


# --- TC-1: LLMClient accepts config and resolves provider ---

class TestClientCreation:
    def test_client_resolves_openai_provider(self, openai_config: LLMConfig) -> None:
        """TC-1: LLMClient should resolve 'openai' to OpenAIProvider."""
        client = LLMClient(openai_config)
        assert isinstance(client._provider, OpenAIProvider), (
            f"LLMClient should resolve 'openai' to OpenAIProvider, got {type(client._provider)}"
        )
        client.close()


# --- TC-2: LLMClient.complete() returns completion string ---

class TestSyncComplete:
    @respx.mock
    def test_complete_returns_content_string(self, openai_config: LLMConfig) -> None:
        """TC-2: complete() should return the completion content string."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(openai_config) as client:
            result = client.complete("Say hello")
        assert result == "Hello", f"complete() should return 'Hello', got '{result}'"


# --- TC-3: LLMClient.acomplete() returns completion string ---

class TestAsyncComplete:
    @respx.mock
    async def test_acomplete_returns_content_string(self, openai_config: LLMConfig) -> None:
        """TC-3: acomplete() should return the completion content string."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        async with LLMClient(openai_config) as client:
            result = await client.acomplete("Say hello")
        assert result == "Hello", f"acomplete() should return 'Hello', got '{result}'"


# --- TC-4: LLMProvider is an abstract base class ---

class TestProviderABC:
    def test_provider_cannot_be_instantiated(self) -> None:
        """TC-4: LLMProvider should not be directly instantiable."""
        with pytest.raises(TypeError):
            LLMProvider()  # type: ignore[abstract]


# --- TC-5: OpenAIProvider exists and implements LLMProvider ---

class TestOpenAIProviderStructure:
    def test_openai_is_subclass_of_provider(self) -> None:
        """TC-5: OpenAIProvider should be a subclass of LLMProvider."""
        assert issubclass(OpenAIProvider, LLMProvider), (
            "OpenAIProvider should be a subclass of LLMProvider"
        )


# --- TC-6: Unsupported provider raises UnsupportedProviderError ---

class TestUnsupportedProvider:
    def test_unknown_provider_raises_error(self) -> None:
        """TC-6: Should raise UnsupportedProviderError for unknown provider."""
        config = LLMConfig(provider="nonexistent", model="test", api_key="key")
        with pytest.raises(UnsupportedProviderError, match="nonexistent"):
            LLMClient(config)

    def test_unsupported_provider_error_is_llm_extender_error(self) -> None:
        """UnsupportedProviderError should inherit from LLMExtenderError."""
        assert issubclass(UnsupportedProviderError, LLMExtenderError)

    def test_provider_error_is_llm_extender_error(self) -> None:
        """ProviderError should inherit from LLMExtenderError."""
        assert issubclass(ProviderError, LLMExtenderError)


# --- TC-7: All public classes have docstrings ---

class TestDocstrings:
    @pytest.mark.parametrize("cls", [LLMClient, LLMProvider, OpenAIProvider, LLMConfig])
    def test_public_classes_have_docstrings(self, cls: type) -> None:
        """TC-7: All public classes should have docstrings."""
        assert cls.__doc__, f"{cls.__name__} is missing a docstring"

    @pytest.mark.parametrize("method_name", ["complete", "acomplete", "close", "aclose"])
    def test_client_methods_have_docstrings(self, method_name: str) -> None:
        """TC-7: LLMClient public methods should have docstrings."""
        method = getattr(LLMClient, method_name, None)
        assert method is not None, f"LLMClient.{method_name} does not exist"
        assert method.__doc__, f"LLMClient.{method_name} is missing a docstring"


# --- TC-10: Provider HTTP error is raised, not swallowed ---

class TestHTTPErrorPropagation:
    @respx.mock
    def test_http_500_raises_provider_error(self, openai_config: LLMConfig) -> None:
        """TC-10: HTTP errors from provider should be raised as ProviderError."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(500, json={"error": {"message": "Internal Server Error"}})
        )
        with LLMClient(openai_config) as client:
            with pytest.raises(ProviderError):
                client.complete("test")

    @respx.mock
    async def test_http_500_raises_provider_error_async(self, openai_config: LLMConfig) -> None:
        """TC-10: Async HTTP errors from provider should be raised as ProviderError."""
        respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(500, json={"error": {"message": "Internal Server Error"}})
        )
        async with LLMClient(openai_config) as client:
            with pytest.raises(ProviderError):
                await client.acomplete("test")


# --- TC-11: Config with custom base_url is passed to provider ---

class TestCustomBaseURL:
    @respx.mock
    def test_custom_base_url_used(self, openai_config_custom_url: LLMConfig) -> None:
        """TC-11: Custom base_url should be used for API requests."""
        respx.post("https://custom.api.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(openai_config_custom_url) as client:
            result = client.complete("test")
        assert result == "Hello", f"Custom base_url should be used for API requests"


# --- Context manager support (Architect A2) ---

class TestContextManager:
    def test_sync_context_manager(self, openai_config: LLMConfig) -> None:
        """LLMClient should support sync context manager."""
        with LLMClient(openai_config) as client:
            assert isinstance(client, LLMClient)

    async def test_async_context_manager(self, openai_config: LLMConfig) -> None:
        """LLMClient should support async context manager."""
        async with LLMClient(openai_config) as client:
            assert isinstance(client, LLMClient)


# --- api_key hidden from repr (Architect A4) ---

class TestConfigRepr:
    def test_api_key_not_in_repr(self, openai_config: LLMConfig) -> None:
        """Architect A4: api_key should not appear in repr."""
        r = repr(openai_config)
        assert "test-key-abc123" not in r, "api_key value should not appear in repr"
