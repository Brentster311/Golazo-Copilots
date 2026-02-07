"""Azure Managed Identity authentication strategy.

Acquires a token via Azure MSI using the azure-identity library.
Requires ``pip install azure-identity``.
"""

from __future__ import annotations

from llm_extender.auth.base import AuthStrategy
from llm_extender.exceptions import AuthenticationError

_DEFAULT_SCOPE = "https://cognitiveservices.azure.com/.default"


class ManagedIdentityAuth(AuthStrategy):
    """Acquire an access token via Azure Managed Identity.

    Args:
        scope: The token scope. Defaults to Azure Cognitive Services.

    Raises:
        ImportError: If ``azure-identity`` is not installed.
    """

    def __init__(self, scope: str = _DEFAULT_SCOPE) -> None:
        try:
            from azure.identity import ManagedIdentityCredential
        except ImportError:
            raise ImportError(
                "ManagedIdentityAuth requires 'azure-identity'. "
                "Install with: pip install azure-identity"
            ) from None
        self._scope = scope
        self._credential = ManagedIdentityCredential()

    def resolve(self) -> str:
        """Acquire a token synchronously.

        Returns:
            The access token string.

        Raises:
            AuthenticationError: If token acquisition fails.
        """
        try:
            token = self._credential.get_token(self._scope)
            return token.token
        except Exception as exc:
            raise AuthenticationError(
                f"Failed to acquire MSI token: {exc}"
            ) from exc

    async def aresolve(self) -> str:
        """Acquire a token asynchronously.

        Creates a new async credential per call for lifecycle safety.

        Returns:
            The access token string.

        Raises:
            AuthenticationError: If token acquisition fails.
        """
        try:
            from azure.identity.aio import (
                ManagedIdentityCredential as AsyncManagedIdentityCredential,
            )
            async_cred = AsyncManagedIdentityCredential()
            try:
                token = await async_cred.get_token(self._scope)
                return token.token
            finally:
                await async_cred.close()
        except ImportError:
            raise ImportError(
                "Async ManagedIdentityAuth requires 'azure-identity'. "
                "Install with: pip install azure-identity"
            ) from None
        except Exception as exc:
            raise AuthenticationError(
                f"Failed to acquire async MSI token: {exc}"
            ) from exc

    def __repr__(self) -> str:
        return f"ManagedIdentityAuth(scope='{self._scope}')"
