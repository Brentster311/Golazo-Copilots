"""Tests for LLMClient + AuthStrategy integration — Architect A4."""

import httpx
import pytest
import respx

from llm_extender.auth.env_var import EnvVarAuth
from llm_extender.auth.callback import CallbackAuth
from llm_extender.client import LLMClient
from llm_extender.config import LLMConfig

from conftest import MOCK_OPENAI_RESPONSE


class TestClientAuthIntegration:
    @respx.mock
    def test_client_uses_auth_strategy_key(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """LLMClient should use auth.resolve() instead of config.api_key when auth is provided."""
        monkeypatch.setenv("MY_LLM_KEY", "env-resolved-key")
        config = LLMConfig(provider="openai", model="gpt-4")
        auth = EnvVarAuth("MY_LLM_KEY")

        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(config, auth=auth) as client:
            client.complete("test")

        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer env-resolved-key", (
            "Client should use resolved auth key in request headers"
        )

    @respx.mock
    def test_client_falls_back_to_config_api_key(self) -> None:
        """LLMClient should use config.api_key when no auth is provided."""
        config = LLMConfig(provider="openai", model="gpt-4", api_key="direct-key")

        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(config) as client:
            client.complete("test")

        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer direct-key", (
            "Client should fall back to config.api_key when no auth provided"
        )

    @respx.mock
    def test_client_with_callback_auth(self) -> None:
        """LLMClient should work with CallbackAuth."""
        config = LLMConfig(provider="openai", model="gpt-4")
        auth = CallbackAuth(callback=lambda: "callback-resolved-key")

        route = respx.post("https://api.openai.com/v1/chat/completions").mock(
            return_value=httpx.Response(200, json=MOCK_OPENAI_RESPONSE)
        )
        with LLMClient(config, auth=auth) as client:
            result = client.complete("test")

        assert result == "Hello"
        request = route.calls[0].request
        assert request.headers["authorization"] == "Bearer callback-resolved-key"
