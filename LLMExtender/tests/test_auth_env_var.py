"""Tests for EnvVarAuth — maps to LLM-0003 TC-2, TC-3, TC-4, TC-5."""

import pytest

from llm_extender.auth.env_var import EnvVarAuth
from llm_extender.exceptions import AuthenticationError


# --- TC-2: EnvVarAuth resolves API key from env var (AC-2) ---

class TestEnvVarResolve:
    def test_resolve_returns_env_var_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-2: EnvVarAuth should return the value of the named env var."""
        monkeypatch.setenv("LLM_API_KEY", "test-key-123")
        auth = EnvVarAuth("LLM_API_KEY")
        assert auth.resolve() == "test-key-123", (
            "EnvVarAuth should return the value of the named env var"
        )


# --- TC-3: EnvVarAuth raises on missing env var (AC-7) ---

class TestEnvVarMissing:
    def test_resolve_raises_on_missing_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-3: EnvVarAuth should raise AuthenticationError for missing env var."""
        monkeypatch.delenv("MISSING_VAR", raising=False)
        auth = EnvVarAuth("MISSING_VAR")
        with pytest.raises(AuthenticationError, match="MISSING_VAR"):
            auth.resolve()


# --- TC-4: EnvVarAuth raises on empty env var (AC-7) ---

class TestEnvVarEmpty:
    def test_resolve_raises_on_empty_var(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-4: EnvVarAuth should raise AuthenticationError for empty env var."""
        monkeypatch.setenv("EMPTY_VAR", "")
        auth = EnvVarAuth("EMPTY_VAR")
        with pytest.raises(AuthenticationError):
            auth.resolve()


# --- TC-5: EnvVarAuth.aresolve() works async (AC-2) ---

class TestEnvVarAsync:
    async def test_aresolve_returns_env_var_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-5: EnvVarAuth.aresolve() should return the value of the named env var."""
        monkeypatch.setenv("LLM_API_KEY", "test-key-123")
        auth = EnvVarAuth("LLM_API_KEY")
        result = await auth.aresolve()
        assert result == "test-key-123", (
            "EnvVarAuth.aresolve() should return the value of the named env var"
        )
