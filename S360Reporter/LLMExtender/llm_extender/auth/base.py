"""Abstract base class for authentication strategies.

All auth implementations must inherit from AuthStrategy and
implement resolve() and aresolve() methods.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class AuthStrategy(ABC):
    """Abstract base class defining the auth strategy contract.

    Every concrete strategy must implement both synchronous and
    asynchronous credential resolution. Credentials must never be
    persisted, logged, or exposed via repr/str.
    """

    @abstractmethod
    def resolve(self) -> str:
        """Resolve and return the credential synchronously.

        Returns:
            The credential string (API key, token, etc.).

        Raises:
            AuthenticationError: If the credential cannot be resolved.
        """

    @abstractmethod
    async def aresolve(self) -> str:
        """Resolve and return the credential asynchronously.

        Returns:
            The credential string (API key, token, etc.).

        Raises:
            AuthenticationError: If the credential cannot be resolved.
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(***)"

    def __str__(self) -> str:
        return self.__repr__()
