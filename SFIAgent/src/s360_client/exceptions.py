"""
Custom exceptions for S360 Client.

Exception hierarchy:
    S360Error (base)
    ├── S360AuthError (authentication/authorization failures)
    ├── S360ApiError (API call failures)
    └── S360CacheError (cache operations failures)
"""

from typing import Any


class S360Error(Exception):
    """Base exception for all S360 client errors."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class S360AuthError(S360Error):
    """Raised when authentication or authorization fails."""

    def __init__(
        self,
        message: str,
        *,
        scope: str | None = None,
        suggestion: str | None = None,
    ) -> None:
        self.scope = scope
        self.suggestion = suggestion or "Try running 'az login' to authenticate."
        full_message = message
        if suggestion:
            full_message = f"{message}. {suggestion}"
        super().__init__(full_message)


class S360ApiError(S360Error):
    """Raised when an S360 API call fails."""

    def __init__(
        self,
        message: str,
        *,
        endpoint: str | None = None,
        status_code: int | None = None,
        response_body: Any | None = None,
    ) -> None:
        self.endpoint = endpoint
        self.status_code = status_code
        self.response_body = response_body
        full_message = message
        if status_code:
            full_message = f"{message} (HTTP {status_code})"
        if endpoint:
            full_message = f"{full_message} - Endpoint: {endpoint}"
        super().__init__(full_message)


class S360CacheError(S360Error):
    """Raised when cache operations fail."""

    def __init__(
        self,
        message: str,
        *,
        cache_path: str | None = None,
        recoverable: bool = True,
    ) -> None:
        self.cache_path = cache_path
        self.recoverable = recoverable
        super().__init__(message)
