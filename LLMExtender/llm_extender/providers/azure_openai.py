"""Azure OpenAI provider implementation.

Targets Azure OpenAI endpoints using the deployment-based URL format
and Azure AD token authentication.
"""

from __future__ import annotations

from typing import Any

import httpx

from llm_extender.config import LLMConfig
from llm_extender.exceptions import ProviderError
from llm_extender.providers.base import LLMProvider

_DEFAULT_API_VERSION = "2024-12-01-preview"


class AzureOpenAIProvider(LLMProvider):
    """Provider for Azure OpenAI chat completion APIs.

    Uses the Azure deployment-based URL format and supports
    Azure AD token authentication via Bearer header.

    Args:
        config: The LLM configuration containing base_url, deployment,
            api_version, api_key (token), and model.

    Raises:
        ValueError: If base_url or deployment is not configured.
    """

    def __init__(self, config: LLMConfig) -> None:
        if not config.base_url:
            raise ValueError(
                "AzureOpenAIProvider requires 'base_url' to be set "
                "(e.g., 'https://your-resource.openai.azure.com')"
            )
        if not config.deployment:
            raise ValueError(
                "AzureOpenAIProvider requires 'deployment' to be set "
                "(e.g., 'gpt-4')"
            )
        self._config = config
        self._base_url = config.base_url.rstrip("/")
        self._deployment = config.deployment
        self._api_version = config.api_version or _DEFAULT_API_VERSION
        self._headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        self._timeout = httpx.Timeout(config.timeout)
        self._sync_client = httpx.Client(
            headers=self._headers,
            timeout=self._timeout,
        )
        self._async_client: httpx.AsyncClient | None = None

    def _get_url(self) -> str:
        """Build the Azure OpenAI deployment URL."""
        return (
            f"{self._base_url}/openai/deployments/{self._deployment}"
            f"/chat/completions?api-version={self._api_version}"
        )

    def _build_payload(self, prompt: str) -> dict[str, Any]:
        """Build the chat completion request payload."""
        return {
            "model": self._config.model,
            "messages": [{"role": "user", "content": prompt}],
        }

    def _extract_content(self, data: dict[str, Any]) -> str:
        """Extract the assistant message content from the response."""
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(
                f"Unexpected response format from Azure OpenAI: {exc}"
            ) from exc

    def _check_response(self, response: httpx.Response) -> dict[str, Any]:
        """Check response status and parse JSON."""
        if response.status_code >= 400:
            try:
                error_body = response.json()
                message = error_body.get("error", {}).get("message", response.text)
            except Exception:
                message = response.text
            raise ProviderError(
                f"Provider returned HTTP {response.status_code}: {message}"
            )
        return response.json()

    def complete(self, prompt: str) -> str:
        """Generate a completion synchronously via Azure OpenAI.

        Args:
            prompt: The user prompt to send to the model.

        Returns:
            The model's response content as a string.

        Raises:
            ProviderError: If the API returns a non-success HTTP status
                or an unexpected response format.
        """
        response = self._sync_client.post(
            self._get_url(),
            json=self._build_payload(prompt),
        )
        data = self._check_response(response)
        return self._extract_content(data)

    async def acomplete(self, prompt: str) -> str:
        """Generate a completion asynchronously via Azure OpenAI.

        Args:
            prompt: The user prompt to send to the model.

        Returns:
            The model's response content as a string.

        Raises:
            ProviderError: If the API returns a non-success HTTP status
                or an unexpected response format.
        """
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                headers=self._headers,
                timeout=self._timeout,
            )
        response = await self._async_client.post(
            self._get_url(),
            json=self._build_payload(prompt),
        )
        data = self._check_response(response)
        return self._extract_content(data)

    def close(self) -> None:
        """Close the synchronous HTTP client and release resources."""
        self._sync_client.close()

    async def aclose(self) -> None:
        """Close the asynchronous HTTP client and release resources."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None
