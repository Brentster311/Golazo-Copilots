"""Callback-based authentication strategy.

Resolves credentials by calling a user-supplied function.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from llm_extender.auth.base import AuthStrategy
from llm_extender.exceptions import AuthenticationError


class CallbackAuth(AuthStrategy):
    """Resolve credentials via a user-supplied callable.

    Args:
        callback: A sync callable ``() -> str`` that returns a credential.
        async_callback: An optional async callable ``() -> str``.
            Used by aresolve() when provided; otherwise falls back to
            the sync callback.
    """

    def __init__(
        self,
        callback: Callable[[], str],
        async_callback: Callable[[], Awaitable[str]] | None = None,
    ) -> None:
        self._callback = callback
        self._async_callback = async_callback

    @staticmethod
    def _validate(result: str) -> str:
        """Validate that the resolved credential is non-empty."""
        if not result:
            raise AuthenticationError("Callback returned empty credential")
        return result

    def resolve(self) -> str:
        """Call the sync callback to get the credential.

        Returns:
            The credential string.

        Raises:
            AuthenticationError: If the callback returns empty or raises.
        """
        try:
            result = self._callback()
        except Exception as exc:
            raise AuthenticationError(
                f"Auth callback failed: {exc}"
            ) from exc
        return self._validate(result)

    async def aresolve(self) -> str:
        """Call the async callback (or fall back to sync) to get the credential.

        Returns:
            The credential string.

        Raises:
            AuthenticationError: If the callback returns empty or raises.
        """
        try:
            if self._async_callback is not None:
                result = await self._async_callback()
            else:
                result = self._callback()
        except Exception as exc:
            raise AuthenticationError(
                f"Auth callback failed: {exc}"
            ) from exc
        return self._validate(result)

    def __repr__(self) -> str:
        return "CallbackAuth(callback=<function>)"
