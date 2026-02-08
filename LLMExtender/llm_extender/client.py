"""LLM Client — the main public interface for LLM Extender.

Provides the LLMClient class that accepts a config and delegates
completion calls to the appropriate provider implementation.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from llm_extender.config import LLMConfig
from llm_extender.exceptions import UnsupportedProviderError
from llm_extender.providers.base import LLMProvider
from llm_extender.providers.azure_openai import AzureOpenAIProvider
from llm_extender.providers.openai import OpenAIProvider

if TYPE_CHECKING:
    from types import TracebackType

    from llm_extender.auth.base import AuthStrategy

# Provider registry: maps provider name to provider class.
PROVIDER_REGISTRY: dict[str, type[LLMProvider]] = {
    "openai": OpenAIProvider,
    "azure_openai": AzureOpenAIProvider,
}


class LLMClient:
    """Provider-agnostic LLM client with sync and async support.

    Instantiate with an LLMConfig to select the provider and model.
    Use complete() for synchronous calls and acomplete() for async.

    Supports context manager protocol for automatic resource cleanup:

        with LLMClient(config) as client:
            result = client.complete("Hello")

        async with LLMClient(config) as client:
            result = await client.acomplete("Hello")

    Args:
        config: An LLMConfig specifying provider, model, and credentials.

    Raises:
        UnsupportedProviderError: If the provider name is not in the registry.
    """

    def __init__(self, config: LLMConfig, auth: AuthStrategy | None = None) -> None:
        if auth is not None:
            config = replace(config, api_key=auth.resolve())
        self._config = config
        provider_cls = PROVIDER_REGISTRY.get(config.provider)
        if provider_cls is None:
            available = ", ".join(sorted(PROVIDER_REGISTRY.keys()))
            raise UnsupportedProviderError(
                f"Unsupported provider '{config.provider}'. "
                f"Available providers: {available}"
            )
        self._provider: LLMProvider = provider_cls(config)

    def complete(self, prompt: str) -> str:
        """Generate a completion synchronously.

        Args:
            prompt: The user prompt to send to the model.

        Returns:
            The model's response as a string.

        Raises:
            ProviderError: If the provider returns an error.
        """
        return self._provider.complete(prompt)

    async def acomplete(self, prompt: str) -> str:
        """Generate a completion asynchronously.

        Args:
            prompt: The user prompt to send to the model.

        Returns:
            The model's response as a string.

        Raises:
            ProviderError: If the provider returns an error.
        """
        return await self._provider.acomplete(prompt)

    def close(self) -> None:
        """Close the underlying provider and release resources."""
        self._provider.close()

    async def aclose(self) -> None:
        """Close the underlying provider asynchronously and release resources."""
        await self._provider.aclose()

    # Sync context manager

    def __enter__(self) -> LLMClient:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.close()

    # Async context manager

    async def __aenter__(self) -> LLMClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.aclose()
