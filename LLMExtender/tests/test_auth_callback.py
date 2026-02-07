"""Tests for CallbackAuth — maps to LLM-0003 TC-8, TC-9, TC-10, TC-11."""

import pytest

from llm_extender.auth.callback import CallbackAuth
from llm_extender.exceptions import AuthenticationError


# --- TC-8: CallbackAuth calls user function (AC-4) ---

class TestCallbackResolve:
    def test_resolve_returns_callback_value(self) -> None:
        """TC-8: CallbackAuth should return value from user-supplied callback."""
        auth = CallbackAuth(callback=lambda: "callback-key-789")
        assert auth.resolve() == "callback-key-789", (
            "CallbackAuth should return value from user-supplied callback"
        )


# --- TC-9: CallbackAuth.aresolve() uses async callback when provided (AC-4) ---

class TestCallbackAsync:
    async def test_aresolve_uses_async_callback(self) -> None:
        """TC-9: CallbackAuth.aresolve() should use async_callback when provided."""
        async def async_fn() -> str:
            return "async-key"

        auth = CallbackAuth(callback=lambda: "sync-key", async_callback=async_fn)
        result = await auth.aresolve()
        assert result == "async-key", (
            "CallbackAuth.aresolve() should use async_callback when provided"
        )


# --- TC-10: CallbackAuth.aresolve() falls back to sync callback (AC-4) ---

class TestCallbackAsyncFallback:
    async def test_aresolve_falls_back_to_sync(self) -> None:
        """TC-10: CallbackAuth.aresolve() should fall back to sync callback when no async_callback."""
        auth = CallbackAuth(callback=lambda: "sync-key")
        result = await auth.aresolve()
        assert result == "sync-key", (
            "CallbackAuth.aresolve() should fall back to sync callback when no async_callback"
        )


# --- TC-11: CallbackAuth raises on empty result (AC-7) ---

class TestCallbackEmpty:
    def test_resolve_raises_on_empty(self) -> None:
        """TC-11: CallbackAuth should raise AuthenticationError on empty credential."""
        auth = CallbackAuth(callback=lambda: "")
        with pytest.raises(AuthenticationError):
            auth.resolve()


# --- Architect A1: Callback exceptions wrapped in AuthenticationError ---

class TestCallbackExceptionWrapping:
    def test_resolve_wraps_callback_exception(self) -> None:
        """A1: Callback exception should be wrapped in AuthenticationError."""
        def bad_callback() -> str:
            raise ValueError("something broke")

        auth = CallbackAuth(callback=bad_callback)
        with pytest.raises(AuthenticationError, match="something broke") as exc_info:
            auth.resolve()
        assert exc_info.value.__cause__ is not None, (
            "Original exception should be preserved as __cause__"
        )

    async def test_aresolve_wraps_async_callback_exception(self) -> None:
        """A1: Async callback exception should be wrapped in AuthenticationError."""
        async def bad_async() -> str:
            raise RuntimeError("async broke")

        auth = CallbackAuth(callback=lambda: "x", async_callback=bad_async)
        with pytest.raises(AuthenticationError, match="async broke") as exc_info:
            await auth.aresolve()
        assert exc_info.value.__cause__ is not None
