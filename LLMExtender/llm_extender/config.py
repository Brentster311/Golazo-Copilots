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
        provider: The provider name (e.g., 'openai', 'azure_openai'). Used to
            look up the provider implementation in the registry.
        model: The model identifier (e.g., 'gpt-4').
        api_key: The API key or token for authentication. Excluded from repr
            for security. Will be replaced by auth strategies when provided.
        base_url: Optional override for the provider's base URL.
            Required for Azure OpenAI (e.g., 'https://your-resource.openai.azure.com').
        timeout: HTTP request timeout in seconds. Defaults to 30.0.
        deployment: Azure OpenAI deployment name. Required for azure_openai provider.
        api_version: Azure OpenAI API version. Defaults to None (provider uses its own default).
    """

    provider: str
    model: str
    api_key: str = field(default="", repr=False)
    base_url: str | None = None
    timeout: float = 30.0
    deployment: str | None = None
    api_version: str | None = None
