"""LLM Extender — provider-agnostic LLM client library.

A unified interface for calling LLMs through different providers,
with synchronous and asynchronous support.

Usage:
    from llm_extender import LLMClient, LLMConfig

    config = LLMConfig(provider="openai", model="gpt-4", api_key="sk-...")
    with LLMClient(config) as client:
        response = client.complete("Hello, world!")
"""

from llm_extender.auth import AuthStrategy, AzureChainedAuth, CallbackAuth, EnvVarAuth, ManagedIdentityAuth
from llm_extender.client import LLMClient
from llm_extender.config import LLMConfig
from llm_extender.exceptions import (
    AuthenticationError,
    LLMExtenderError,
    ProviderError,
    UnsupportedProviderError,
)
from llm_extender.providers.azure_openai import AzureOpenAIProvider
from llm_extender.providers.base import LLMProvider
from llm_extender.url_fetcher import afetch_url, build_context_prompt, fetch_url
from llm_extender.discovery import discover_azure_configs

__all__ = [
    "AuthStrategy",
    "AuthenticationError",
    "AzureChainedAuth",
    "AzureOpenAIProvider",
    "CallbackAuth",
    "EnvVarAuth",
    "LLMClient",
    "LLMConfig",
    "LLMExtenderError",
    "LLMProvider",
    "ManagedIdentityAuth",
    "ProviderError",
    "UnsupportedProviderError",
    "afetch_url",
    "build_context_prompt",
    "discover_azure_configs",
    "fetch_url",
]
