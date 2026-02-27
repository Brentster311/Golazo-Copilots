"""Tests for AuthStrategy ABC — maps to LLM-0003 TC-1."""

import pytest

from llm_extender.auth.base import AuthStrategy


class TestAuthStrategyABC:
    def test_auth_strategy_cannot_be_instantiated(self) -> None:
        """TC-1: AuthStrategy should not be directly instantiable."""
        with pytest.raises(TypeError):
            AuthStrategy()  # type: ignore[abstract]
