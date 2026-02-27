"""Azure chained authentication strategy.

Resolves credentials by trying Azure CLI, then Managed Identity,
then a static API key, failing explicitly if none succeed.
Requires ``pip install azure-identity`` for credential steps 1-2.
"""

from __future__ import annotations

from llm_extender.auth.base import AuthStrategy
from llm_extender.exceptions import AuthenticationError

_DEFAULT_SCOPE = "https://cognitiveservices.azure.com/.default"


class AzureChainedAuth(AuthStrategy):
    """Resolve credentials via a predictable 3-step chain.

    Resolution order (stops at first success):
        1. **Azure CLI** — ``AzureCliCredential`` (local dev)
        2. **Managed Identity** — ``ManagedIdentityCredential`` (production)
        3. **API key** — static ``api_key`` string (fallback)
        4. **Fail** — ``AuthenticationError`` listing all attempted methods

    The ``scope`` parameter controls which Azure AD resource the token
    is requested for, making this class reusable for both LLM API auth
    and authenticated URL fetches with different scopes.

    Args:
        scope: The Azure AD token scope.
            Defaults to ``https://cognitiveservices.azure.com/.default``.
        api_key: An optional static API key used as the final fallback.

    Note:
        ``azure-identity`` is lazily imported. If not installed, steps 1-2
        are skipped and the chain falls through to the API key.
    """

    def __init__(
        self,
        scope: str = _DEFAULT_SCOPE,
        api_key: str = "",
    ) -> None:
        self._scope = scope
        self._api_key = api_key
        self._azure_available = True

        # Eagerly check if azure-identity is available (but don't fail)
        try:
            from azure.identity import (  # noqa: F401
                AzureCliCredential,
                ManagedIdentityCredential,
            )
        except ImportError:
            self._azure_available = False

    # ------------------------------------------------------------------
    # Sync
    # ------------------------------------------------------------------

    def resolve(self) -> str:
        """Resolve a credential synchronously.

        Tries Azure CLI → Managed Identity → API key → fail.

        Returns:
            The credential string (token or API key).

        Raises:
            AuthenticationError: If all methods fail.
        """
        errors: list[str] = []

        if self._azure_available:
            # Step 1: Azure CLI
            try:
                from azure.identity import AzureCliCredential

                cred = AzureCliCredential()
                token = cred.get_token(self._scope)
                return token.token
            except Exception as exc:
                errors.append(f"Azure CLI: {exc}")

            # Step 2: Managed Identity
            try:
                from azure.identity import ManagedIdentityCredential

                cred = ManagedIdentityCredential()
                token = cred.get_token(self._scope)
                return token.token
            except Exception as exc:
                errors.append(f"Managed Identity: {exc}")
        else:
            errors.append(
                "Azure CLI: azure-identity not installed"
            )
            errors.append(
                "Managed Identity: azure-identity not installed"
            )

        # Step 3: API key
        if self._api_key:
            return self._api_key

        errors.append("API key: not provided")

        raise AuthenticationError(
            "All authentication methods failed:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    # ------------------------------------------------------------------
    # Async
    # ------------------------------------------------------------------

    async def aresolve(self) -> str:
        """Resolve a credential asynchronously.

        Tries Azure CLI → Managed Identity → API key → fail.
        Async credentials are created and closed per call for lifecycle safety.

        Returns:
            The credential string (token or API key).

        Raises:
            AuthenticationError: If all methods fail.
        """
        errors: list[str] = []

        if self._azure_available:
            # Step 1: Azure CLI (async)
            try:
                from azure.identity.aio import AzureCliCredential

                cred = AzureCliCredential()
                try:
                    token = await cred.get_token(self._scope)
                    return token.token
                finally:
                    await cred.close()
            except ImportError:
                errors.append("Azure CLI: azure-identity[aio] not available")
            except Exception as exc:
                errors.append(f"Azure CLI: {exc}")

            # Step 2: Managed Identity (async)
            try:
                from azure.identity.aio import ManagedIdentityCredential

                cred = ManagedIdentityCredential()
                try:
                    token = await cred.get_token(self._scope)
                    return token.token
                finally:
                    await cred.close()
            except ImportError:
                errors.append(
                    "Managed Identity: azure-identity[aio] not available"
                )
            except Exception as exc:
                errors.append(f"Managed Identity: {exc}")
        else:
            errors.append("Azure CLI: azure-identity not installed")
            errors.append("Managed Identity: azure-identity not installed")

        # Step 3: API key
        if self._api_key:
            return self._api_key

        errors.append("API key: not provided")

        raise AuthenticationError(
            "All authentication methods failed:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    def __repr__(self) -> str:
        return f"AzureChainedAuth(scope='{self._scope}', ***)"
