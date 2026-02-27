"""Shared test fixtures for llm_extender tests."""

import pytest

from llm_extender.config import LLMConfig


@pytest.fixture
def openai_config() -> LLMConfig:
    """A valid OpenAI provider config for testing."""
    return LLMConfig(
        provider="openai",
        model="gpt-4",
        api_key="test-key-abc123",
    )


@pytest.fixture
def openai_config_custom_url() -> LLMConfig:
    """A valid OpenAI config with custom base_url."""
    return LLMConfig(
        provider="openai",
        model="gpt-4",
        api_key="test-key-abc123",
        base_url="https://custom.api.com",
    )


MOCK_OPENAI_RESPONSE = {
    "id": "chatcmpl-test",
    "object": "chat.completion",
    "choices": [
        {
            "index": 0,
            "message": {"role": "assistant", "content": "Hello"},
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6},
}
