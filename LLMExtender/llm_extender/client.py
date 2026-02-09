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
from llm_extender.url_fetcher import afetch_url, build_context_prompt, fetch_url

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

    def complete_with_context(
        self,
        prompt: str,
        content: str,
        source_url: str | None = None,
    ) -> str:
        """Send pre-fetched content as context along with a prompt.

        Use this when content has been obtained outside the library
        (e.g., via CDP browser, file read, or custom scraper).

        Args:
            prompt: The user question or instruction.
            content: The pre-fetched text content to use as context.
            source_url: Optional source URL for attribution in the
                prompt. If ``None``, the URL is omitted.

        Returns:
            The model's response as a string.

        Raises:
            ProviderError: If the provider returns an error.
        """
        url = source_url or "unknown"
        augmented = build_context_prompt(url, content, prompt)
        return self._provider.complete(augmented)

    async def acomplete_with_context(
        self,
        prompt: str,
        content: str,
        source_url: str | None = None,
    ) -> str:
        """Async version of :meth:`complete_with_context`.

        Args:
            prompt: The user question or instruction.
            content: The pre-fetched text content to use as context.
            source_url: Optional source URL for attribution.

        Returns:
            The model's response as a string.

        Raises:
            ProviderError: If the provider returns an error.
        """
        url = source_url or "unknown"
        augmented = build_context_prompt(url, content, prompt)
        return await self._provider.acomplete(augmented)

    def complete_with_url(
        self,
        prompt: str,
        url: str,
        *,
        url_auth: AuthStrategy | None = None,
        max_length: int = 50_000,
        render_js: bool = False,
        browser_auth: str | None = None,
    ) -> str:
        """Fetch URL content and use it as context for a completion.

        Downloads the content at *url*, converts HTML to plain text,
        truncates to *max_length* characters, then sends the combined
        context + prompt to the provider.

        Args:
            prompt: The user question or instruction.
            url: The URL whose content should be fetched as context.
            url_auth: Optional auth strategy for the HTTP request.
                The resolved token is sent as a Bearer header.
            max_length: Maximum characters to keep from the fetched
                content (default 50 000).
            render_js: If ``True``, use a headless browser to render
                JavaScript before extracting text.
            browser_auth: Optional browser auth mode (``"aad"`` for
                AAD device-code-flow). Requires ``render_js=True``.

        Returns:
            The model's response as a string.

        Raises:
            ProviderError: If the URL cannot be fetched or the provider
                returns an error.
        """
        content = fetch_url(
            url, auth=url_auth, max_length=max_length,
            render_js=render_js, browser_auth=browser_auth,
        )
        return self.complete_with_context(prompt, content, source_url=url)

    async def acomplete_with_url(
        self,
        prompt: str,
        url: str,
        *,
        url_auth: AuthStrategy | None = None,
        max_length: int = 50_000,
        render_js: bool = False,
        browser_auth: str | None = None,
    ) -> str:
        """Async version of :meth:`complete_with_url`.

        Args:
            prompt: The user question or instruction.
            url: The URL whose content should be fetched as context.
            url_auth: Optional auth strategy for the HTTP request.
                The resolved token is sent as a Bearer header.
            max_length: Maximum characters to keep from the fetched
                content (default 50 000).
            render_js: If ``True``, use a headless browser to render
                JavaScript before extracting text.
            browser_auth: Optional browser auth mode (``"aad"`` for
                AAD device-code-flow). Requires ``render_js=True``.

        Returns:
            The model's response as a string.

        Raises:
            ProviderError: If the URL cannot be fetched or the provider
                returns an error.
        """
        content = await afetch_url(
            url, auth=url_auth, max_length=max_length,
            render_js=render_js, browser_auth=browser_auth,
        )
        return await self.acomplete_with_context(prompt, content, source_url=url)

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
