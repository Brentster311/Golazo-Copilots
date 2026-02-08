"""Tests for AzureOpenAIProvider — maps to LLM-0004 acceptance criteria."""

import httpx
import pytest
import respx

from llm_extender.client import LLMClient
from llm_extender.config import LLMConfig
from llm_extender.providers.azure_openai import AzureOpenAIProvider
from llm_extender.providers.base import LLMProvider
from llm_extender.exceptions import ProviderError, UnsupportedProviderError

from conftest import MOCK_OPENAI_RESPONSE

_AZURE_BASE = "https://open-ai-poc.openai.azure.com"
_DEPLOYMENT = "gpt-5.2"
_API_VERSION = "2024-12-01-preview"
_AZURE_URL = f"{_AZURE_BASE}/openai/deployments/{_DEPLOYMENT}/chat/completions?api-version={_API_VERSION}"


@pytest.fixture
def azure_config() -> LLMConfig:
    """A valid Azure OpenAI config for testing."""
    return LLMConfig(
        provider="azure_openai",
        model="gpt-5.2",
        api_key="test-azure-token",
        base_url=_AZURE_BASE,
        deployment=_DEPLOYMENT,
        api_version=_API_VERSION,
    )


@pytest.fixture
def azure_provider(azure_config: LLMConfig) -> AzureOpenAIProvider:
    """An AzureOpenAIProvider for testing."""
    return AzureOpenAIProvider(azure_config)


# --- AC-1: Azure URL format ---

class TestAzureURLFormat:
    @respx.mock
    def test_uses_azure_url_pattern(self, azure_provider: AzureOpenAIProvider) -> None:
        """AC-1: Should use Azure's deployment-based URL format."""
        route = respx.post(_AZURE_URL).mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        azure_provider.complete("test")
        assert route.called, (
            "AzureOpenAIProvider should POST to Azure deployment URL"
        )

    @respx.mock
    def test_custom_api_version_in_url(self) -> None:
        """AC-1: Custom api_version should appear in the URL."""
        config = LLMConfig(
            provider="azure_openai",
            model="gpt-4",
            api_key="token",
            base_url=_AZURE_BASE,
            deployment=_DEPLOYMENT,
            api_version="2025-01-01",
        )
        expected_url = f"{_AZURE_BASE}/openai/deployments/{_DEPLOYMENT}/chat/completions?api-version=2025-01-01"
        route = respx.post(expected_url).mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        provider = AzureOpenAIProvider(config)
        provider.complete("test")
        assert route.called


# --- AC-2: LLMConfig accepts deployment and api_version ---

class TestConfigFields:
    def test_config_has_deployment_field(self) -> None:
        """AC-2: LLMConfig should accept a deployment field."""
        config = LLMConfig(
            provider="azure_openai", model="gpt-4",
            deployment="my-deployment",
        )
        assert config.deployment == "my-deployment"

    def test_config_has_api_version_field(self) -> None:
        """AC-2: LLMConfig should accept an api_version field."""
        config = LLMConfig(
            provider="azure_openai", model="gpt-4",
            api_version="2025-01-01",
        )
        assert config.api_version == "2025-01-01"

    def test_config_defaults_to_none(self) -> None:
        """AC-2: deployment and api_version should default to None."""
        config = LLMConfig(provider="openai", model="gpt-4")
        assert config.deployment is None
        assert config.api_version is None


# --- AC-3: Registered as "azure_openai" ---

class TestProviderRegistration:
    def test_azure_openai_in_registry(self) -> None:
        """AC-3: 'azure_openai' should be in PROVIDER_REGISTRY."""
        from llm_extender.client import PROVIDER_REGISTRY
        assert "azure_openai" in PROVIDER_REGISTRY, (
            "'azure_openai' should be registered in PROVIDER_REGISTRY"
        )
        assert PROVIDER_REGISTRY["azure_openai"] is AzureOpenAIProvider

    def test_client_resolves_azure_provider(self, azure_config: LLMConfig) -> None:
        """AC-3: LLMClient should resolve 'azure_openai' to AzureOpenAIProvider."""
        client = LLMClient(azure_config)
        assert isinstance(client._provider, AzureOpenAIProvider)
        client.close()


# --- AC-4: Works with CallbackAuth ---

class TestCallbackAuthIntegration:
    @respx.mock
    def test_works_with_callback_auth(self) -> None:
        """AC-4: Should work with CallbackAuth + token-based auth."""
        from llm_extender.auth.callback import CallbackAuth

        config = LLMConfig(
            provider="azure_openai",
            model="gpt-5.2",
            base_url=_AZURE_BASE,
            deployment=_DEPLOYMENT,
            api_version=_API_VERSION,
        )
        auth = CallbackAuth(callback=lambda: "azure-ad-token-123")

        route = respx.post(_AZURE_URL).mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(config, auth=auth) as client:
            result = client.complete("test")

        assert result == "Hello"
        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer azure-ad-token-123"


# --- AC-5: Bearer token header ---

class TestAuthHeader:
    @respx.mock
    def test_sends_bearer_token(self, azure_provider: AzureOpenAIProvider) -> None:
        """AC-5: Should send Authorization: Bearer <token> header."""
        route = respx.post(_AZURE_URL).mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        azure_provider.complete("test")
        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer test-azure-token", (
            "Azure provider should send Bearer token header"
        )


# --- AC-6: Sync and async support ---

class TestSyncAsync:
    @respx.mock
    def test_complete_returns_string(self, azure_provider: AzureOpenAIProvider) -> None:
        """AC-6: complete() should return completion string."""
        respx.post(_AZURE_URL).mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        result = azure_provider.complete("test")
        assert result == "Hello"

    @respx.mock
    async def test_acomplete_returns_string(self, azure_provider: AzureOpenAIProvider) -> None:
        """AC-6: acomplete() should return completion string."""
        respx.post(_AZURE_URL).mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        result = await azure_provider.acomplete("test")
        assert result == "Hello"


# --- AC-7: Inherits LLMProvider ---

class TestProviderContract:
    def test_is_subclass_of_llm_provider(self) -> None:
        """AzureOpenAIProvider should be a subclass of LLMProvider."""
        assert issubclass(AzureOpenAIProvider, LLMProvider)


# --- Error handling ---

class TestValidation:
    def test_missing_deployment_raises_error(self) -> None:
        """Should raise ValueError if deployment is not set."""
        config = LLMConfig(
            provider="azure_openai",
            model="gpt-4",
            api_key="token",
            base_url=_AZURE_BASE,
        )
        with pytest.raises(ValueError, match="deployment"):
            AzureOpenAIProvider(config)

    def test_missing_base_url_raises_error(self) -> None:
        """Should raise ValueError if base_url is not set."""
        config = LLMConfig(
            provider="azure_openai",
            model="gpt-4",
            api_key="token",
            deployment=_DEPLOYMENT,
        )
        with pytest.raises(ValueError, match="base_url"):
            AzureOpenAIProvider(config)


class TestHTTPErrors:
    @respx.mock
    def test_401_raises_provider_error(self, azure_provider: AzureOpenAIProvider) -> None:
        """HTTP 401 should raise ProviderError."""
        respx.post(_AZURE_URL).mock(
            return_value=httpx.Response(401, json={"error": {"message": "Unauthorized"}})
        )
        with pytest.raises(ProviderError, match="401"):
            azure_provider.complete("test")

    @respx.mock
    async def test_async_500_raises_provider_error(self, azure_provider: AzureOpenAIProvider) -> None:
        """Async HTTP 500 should raise ProviderError."""
        respx.post(_AZURE_URL).mock(
            return_value=httpx.Response(500, json={"error": {"message": "Server error"}})
        )
        with pytest.raises(ProviderError):
            await azure_provider.acomplete("test")


# --- Docstrings ---

class TestDocstrings:
    def test_class_has_docstring(self) -> None:
        """AzureOpenAIProvider should have a docstring."""
        assert AzureOpenAIProvider.__doc__

    @pytest.mark.parametrize("method_name", ["complete", "acomplete", "close", "aclose"])
    def test_methods_have_docstrings(self, method_name: str) -> None:
        """Public methods should have docstrings."""
        method = getattr(AzureOpenAIProvider, method_name, None)
        assert method is not None
        assert method.__doc__
