"""Configuration for LLM Extender.

Provides the LLMConfig dataclass that holds provider, model, and
connection settings. Security artifacts (api_key) are excluded from
repr output.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LLMConfig:
    """Configuration for the LLM client.

    Attributes:
        provider: The provider name (e.g., 'openai'). Used to look up
            the provider implementation in the registry.
        model: The model identifier (e.g., 'gpt-4').
        api_key: The API key for authentication. Excluded from repr
            for security. Will be replaced by auth strategies in LLM-0003.
        base_url: Optional override for the provider's base URL.
            Useful for proxies, local models, or compatible endpoints.
        timeout: HTTP request timeout in seconds. Defaults to 30.0.
    """

    provider: str
    model: str
    api_key: str = field(default="", repr=False)
    base_url: str | None = None
    timeout: float = 30.0
