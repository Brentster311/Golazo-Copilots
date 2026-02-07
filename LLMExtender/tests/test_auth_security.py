"""Tests for auth security — maps to LLM-0003 TC-12, TC-13, TC-14."""

import logging
from unittest.mock import MagicMock, patch

import pytest

from llm_extender.auth.env_var import EnvVarAuth
from llm_extender.auth.callback import CallbackAuth


# --- TC-12: repr() never contains credential values (AC-5, AC-6) ---

class TestReprSafety:
    def test_env_var_repr_no_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-12: repr() must never expose credential values."""
        monkeypatch.setenv("SECRET_KEY", "super-secret-value-999")
        auth = EnvVarAuth("SECRET_KEY")
        auth.resolve()  # resolve first to ensure value is not cached in repr
        r = repr(auth)
        assert "super-secret-value-999" not in r, (
            "repr() must never expose credential values"
        )

    def test_callback_repr_no_credentials(self) -> None:
        """TC-12: CallbackAuth repr must not expose credential values."""
        auth = CallbackAuth(callback=lambda: "my-secret-key")
        r = repr(auth)
        assert "my-secret-key" not in r, (
            "repr() must never expose credential values"
        )

    def test_msi_repr_no_credentials(self) -> None:
        """TC-12: ManagedIdentityAuth repr must not expose credential values."""
        mock_credential_cls = MagicMock()
        mock_credential_cls.return_value = MagicMock()

        with patch.dict("sys.modules", {
            "azure": MagicMock(),
            "azure.identity": MagicMock(ManagedIdentityCredential=mock_credential_cls),
        }):
            from llm_extender.auth.msi import ManagedIdentityAuth
            auth = ManagedIdentityAuth(scope="https://test.scope/.default")

        r = repr(auth)
        assert "token" not in r.lower() or "scope" in r, (
            "repr() must never expose credential values"
        )


# --- TC-13: str() never contains credential values (AC-5, AC-6) ---

class TestStrSafety:
    def test_env_var_str_no_credentials(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """TC-13: str() must never expose credential values."""
        monkeypatch.setenv("SECRET_KEY", "super-secret-value-999")
        auth = EnvVarAuth("SECRET_KEY")
        auth.resolve()
        s = str(auth)
        assert "super-secret-value-999" not in s, (
            "str() must never expose credential values"
        )

    def test_callback_str_no_credentials(self) -> None:
        """TC-13: CallbackAuth str must not expose credential values."""
        auth = CallbackAuth(callback=lambda: "my-secret-key")
        s = str(auth)
        assert "my-secret-key" not in s, (
            "str() must never expose credential values"
        )


# --- TC-14: Credentials are not logged at any level (AC-5) ---

class TestNoLogging:
    def test_env_var_resolve_does_not_log_credential(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """TC-14: Credentials must never appear in log output."""
        monkeypatch.setenv("LLM_KEY", "logged-secret-abc")
        auth = EnvVarAuth("LLM_KEY")
        with caplog.at_level(logging.DEBUG, logger="llm_extender"):
            auth.resolve()
        for record in caplog.records:
            assert "logged-secret-abc" not in record.getMessage(), (
                "Credentials must never appear in log output"
            )

    def test_callback_resolve_does_not_log_credential(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """TC-14: Callback credentials must never appear in log output."""
        auth = CallbackAuth(callback=lambda: "callback-secret-xyz")
        with caplog.at_level(logging.DEBUG, logger="llm_extender"):
            auth.resolve()
        for record in caplog.records:
            assert "callback-secret-xyz" not in record.getMessage(), (
                "Credentials must never appear in log output"
            )
