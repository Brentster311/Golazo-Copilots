"""OpenAI-compatible provider implementation.

Supports any API endpoint that follows the OpenAI /v1/chat/completions
format, including OpenAI, Azure OpenAI, Together, Groq, and LM Studio.
"""

from __future__ import annotations

from typing import Any

import httpx

from llm_extender.config import LLMConfig
from llm_extender.exceptions import ProviderError
from llm_extender.providers.base import LLMProvider

_DEFAULT_BASE_URL = "https://api.openai.com"


class OpenAIProvider(LLMProvider):
    """Provider for OpenAI-compatible chat completion APIs.

    Uses httpx for both synchronous and asynchronous HTTP calls.
    Sends requests to the /v1/chat/completions endpoint.

    Args:
        config: The LLM configuration containing model, api_key,
            and optional base_url.
    """

    def __init__(self, config: LLMConfig) -> None:
        self._config = config
        self._base_url = (config.base_url or _DEFAULT_BASE_URL).rstrip("/")
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
        return f"{self._base_url}/v1/chat/completions"

    def _build_payload(self, prompt: str) -> dict[str, Any]:
        return {
            "model": self._config.model,
            "messages": [{"role": "user", "content": prompt}],
        }

    def _extract_content(self, data: dict[str, Any]) -> str:
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as exc:
            raise ProviderError(
                f"Unexpected response format from provider: {exc}"
            ) from exc

    def _check_response(self, response: httpx.Response) -> dict[str, Any]:
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
        """Generate a completion synchronously via the OpenAI-compatible API.

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
        """Generate a completion asynchronously via the OpenAI-compatible API.

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
