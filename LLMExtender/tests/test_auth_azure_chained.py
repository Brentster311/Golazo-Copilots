"""Tests for AzureChainedAuth — maps to LLM-0005 test cases."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llm_extender.auth.base import AuthStrategy
from llm_extender.exceptions import AuthenticationError


# ---------------------------------------------------------------------------
# Helpers — build mock azure-identity modules
# ---------------------------------------------------------------------------

def _make_azure_modules(
    *,
    cli_token: str | None = None,
    cli_error: Exception | None = None,
    msi_token: str | None = None,
    msi_error: Exception | None = None,
) -> dict[str, MagicMock]:
    """Build mock ``azure.identity`` modules for patching ``sys.modules``."""
    # Sync CLI credential
    mock_cli_cls = MagicMock()
    mock_cli_inst = MagicMock()
    if cli_error:
        mock_cli_inst.get_token.side_effect = cli_error
    else:
        tok = MagicMock()
        tok.token = cli_token or ""
        mock_cli_inst.get_token.return_value = tok
    mock_cli_cls.return_value = mock_cli_inst

    # Sync MSI credential
    mock_msi_cls = MagicMock()
    mock_msi_inst = MagicMock()
    if msi_error:
        mock_msi_inst.get_token.side_effect = msi_error
    else:
        tok = MagicMock()
        tok.token = msi_token or ""
        mock_msi_inst.get_token.return_value = tok
    mock_msi_cls.return_value = mock_msi_inst

    identity_mod = MagicMock(
        AzureCliCredential=mock_cli_cls,
        ManagedIdentityCredential=mock_msi_cls,
    )
    azure_mod = MagicMock()

    return {
        "azure": azure_mod,
        "azure.identity": identity_mod,
    }


def _make_async_azure_modules(
    *,
    cli_token: str | None = None,
    cli_error: Exception | None = None,
    msi_token: str | None = None,
    msi_error: Exception | None = None,
) -> dict[str, MagicMock]:
    """Build mock ``azure.identity.aio`` modules for async tests."""
    # Start with sync modules (needed for __init__ to not fail)
    modules = _make_azure_modules(
        cli_token=cli_token,
        cli_error=cli_error,
        msi_token=msi_token,
        msi_error=msi_error,
    )

    # Async CLI credential
    mock_async_cli_cls = MagicMock()
    mock_async_cli_inst = MagicMock()
    if cli_error:
        mock_async_cli_inst.get_token = AsyncMock(side_effect=cli_error)
    else:
        tok = MagicMock()
        tok.token = cli_token or ""
        mock_async_cli_inst.get_token = AsyncMock(return_value=tok)
    mock_async_cli_inst.close = AsyncMock()
    mock_async_cli_cls.return_value = mock_async_cli_inst

    # Async MSI credential
    mock_async_msi_cls = MagicMock()
    mock_async_msi_inst = MagicMock()
    if msi_error:
        mock_async_msi_inst.get_token = AsyncMock(side_effect=msi_error)
    else:
        tok = MagicMock()
        tok.token = msi_token or ""
        mock_async_msi_inst.get_token = AsyncMock(return_value=tok)
    mock_async_msi_inst.close = AsyncMock()
    mock_async_msi_cls.return_value = mock_async_msi_inst

    aio_mod = MagicMock(
        AzureCliCredential=mock_async_cli_cls,
        ManagedIdentityCredential=mock_async_msi_cls,
    )
    modules["azure.identity.aio"] = aio_mod

    return modules


# ===========================================================================
# TC-1: Azure CLI credential succeeds
# ===========================================================================

class TestCLISucceeds:
    def test_resolve_returns_cli_token(self) -> None:
        """TC-1: When CLI credential succeeds, resolve() returns CLI token."""
        modules = _make_azure_modules(cli_token="cli-token-123")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            result = auth.resolve()
        assert result == "cli-token-123"

    def test_msi_not_called_when_cli_succeeds(self) -> None:
        """TC-1: MSI should not be called when CLI succeeds."""
        modules = _make_azure_modules(cli_token="cli-token")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            auth.resolve()
            # MSI credential should not have get_token called
            msi_cls = modules["azure.identity"].ManagedIdentityCredential
            msi_inst = msi_cls.return_value
            msi_inst.get_token.assert_not_called()


# ===========================================================================
# TC-2: CLI fails, MSI succeeds
# ===========================================================================

class TestMSIFallback:
    def test_resolve_returns_msi_token(self) -> None:
        """TC-2: When CLI fails, resolve() falls back to MSI token."""
        modules = _make_azure_modules(
            cli_error=Exception("CLI not logged in"),
            msi_token="msi-token-456",
        )
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            result = auth.resolve()
        assert result == "msi-token-456"


# ===========================================================================
# TC-3: CLI fails, MSI fails, API key succeeds
# ===========================================================================

class TestAPIKeyFallback:
    def test_resolve_returns_api_key(self) -> None:
        """TC-3: When CLI and MSI fail, resolve() falls back to api_key."""
        modules = _make_azure_modules(
            cli_error=Exception("CLI fail"),
            msi_error=Exception("MSI fail"),
        )
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth(api_key="my-api-key")
            result = auth.resolve()
        assert result == "my-api-key"


# ===========================================================================
# TC-4: All three fail → AuthenticationError
# ===========================================================================

class TestAllFail:
    def test_raises_auth_error_listing_methods(self) -> None:
        """TC-4: When all methods fail, AuthenticationError lists them all."""
        modules = _make_azure_modules(
            cli_error=Exception("CLI fail"),
            msi_error=Exception("MSI fail"),
        )
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()  # no api_key
            with pytest.raises(AuthenticationError, match="Azure CLI"):
                auth.resolve()

    def test_error_mentions_msi(self) -> None:
        """TC-4: Error message mentions Managed Identity."""
        modules = _make_azure_modules(
            cli_error=Exception("CLI fail"),
            msi_error=Exception("MSI fail"),
        )
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            with pytest.raises(AuthenticationError, match="Managed Identity"):
                auth.resolve()

    def test_error_mentions_api_key(self) -> None:
        """TC-4: Error message mentions API key."""
        modules = _make_azure_modules(
            cli_error=Exception("CLI fail"),
            msi_error=Exception("MSI fail"),
        )
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            with pytest.raises(AuthenticationError, match="API key"):
                auth.resolve()


# ===========================================================================
# TC-5: Custom scope passed to credentials
# ===========================================================================

class TestCustomScope:
    def test_custom_scope_used(self) -> None:
        """TC-5: Custom scope is passed to get_token()."""
        modules = _make_azure_modules(cli_token="tok")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth(scope="https://graph.microsoft.com/.default")
            auth.resolve()
            cli_inst = modules["azure.identity"].AzureCliCredential.return_value
            cli_inst.get_token.assert_called_once_with(
                "https://graph.microsoft.com/.default"
            )


# ===========================================================================
# TC-6: Default scope is cognitiveservices
# ===========================================================================

class TestDefaultScope:
    def test_default_scope(self) -> None:
        """TC-6: Default scope is cognitiveservices."""
        modules = _make_azure_modules(cli_token="tok")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            auth.resolve()
            cli_inst = modules["azure.identity"].AzureCliCredential.return_value
            cli_inst.get_token.assert_called_once_with(
                "https://cognitiveservices.azure.com/.default"
            )


# ===========================================================================
# TC-7: azure-identity not installed → falls to API key
# ===========================================================================

class TestNoAzureIdentityWithKey:
    def test_falls_to_api_key(self) -> None:
        """TC-7: Without azure-identity, falls back to API key."""
        with patch.dict("sys.modules", {
            "azure": None,
            "azure.identity": None,
        }):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth(api_key="fallback-key")
            result = auth.resolve()
        assert result == "fallback-key"


# ===========================================================================
# TC-8: azure-identity not installed, no API key → fail
# ===========================================================================

class TestNoAzureIdentityNoKey:
    def test_raises_auth_error(self) -> None:
        """TC-8: Without azure-identity and no API key, raises AuthenticationError."""
        with patch.dict("sys.modules", {
            "azure": None,
            "azure.identity": None,
        }):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            with pytest.raises(AuthenticationError):
                auth.resolve()


# ===========================================================================
# TC-9: Async resolve — CLI succeeds
# ===========================================================================

class TestAsyncCLI:
    @pytest.mark.asyncio
    async def test_aresolve_returns_cli_token(self) -> None:
        """TC-9: aresolve() returns CLI token when it succeeds."""
        modules = _make_async_azure_modules(cli_token="async-cli-tok")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
            result = await auth.aresolve()
        assert result == "async-cli-tok"


# ===========================================================================
# TC-10: Async resolve — full chain fallback to API key
# ===========================================================================

class TestAsyncFallback:
    @pytest.mark.asyncio
    async def test_aresolve_falls_to_api_key(self) -> None:
        """TC-10: aresolve() falls back to API key when CLI and MSI fail."""
        modules = _make_async_azure_modules(
            cli_error=Exception("CLI fail"),
            msi_error=Exception("MSI fail"),
        )
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth(api_key="async-key")
            result = await auth.aresolve()
        assert result == "async-key"


# ===========================================================================
# TC-11: repr does not leak credentials
# ===========================================================================

class TestRepr:
    def test_repr_hides_credentials(self) -> None:
        """TC-11: repr shows class name with *** (no credential leaks)."""
        modules = _make_azure_modules(cli_token="secret")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth(api_key="secret-key")
            r = repr(auth)
        assert "***" in r
        assert "secret" not in r


# ===========================================================================
# TC-12: Subclass of AuthStrategy
# ===========================================================================

class TestSubclass:
    def test_is_auth_strategy(self) -> None:
        """TC-12: AzureChainedAuth is a subclass of AuthStrategy."""
        modules = _make_azure_modules(cli_token="tok")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
            auth = AzureChainedAuth()
        assert isinstance(auth, AuthStrategy)


# ===========================================================================
# TC-13: Docstrings present
# ===========================================================================

class TestDocstrings:
    def test_class_has_docstring(self) -> None:
        """TC-13: AzureChainedAuth has a class docstring."""
        modules = _make_azure_modules(cli_token="tok")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
        assert AzureChainedAuth.__doc__ is not None

    def test_resolve_has_docstring(self) -> None:
        """TC-13: resolve() has a docstring."""
        modules = _make_azure_modules(cli_token="tok")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
        assert AzureChainedAuth.resolve.__doc__ is not None

    def test_aresolve_has_docstring(self) -> None:
        """TC-13: aresolve() has a docstring."""
        modules = _make_azure_modules(cli_token="tok")
        with patch.dict("sys.modules", modules):
            from llm_extender.auth.azure_chained import AzureChainedAuth
        assert AzureChainedAuth.aresolve.__doc__ is not None
