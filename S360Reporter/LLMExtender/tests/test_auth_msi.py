"""Tests for ManagedIdentityAuth — maps to LLM-0003 TC-6, TC-7."""

from unittest.mock import MagicMock, patch

import pytest

from llm_extender.auth.msi import ManagedIdentityAuth
from llm_extender.exceptions import AuthenticationError


# --- TC-6: ManagedIdentityAuth calls azure-identity (AC-3) ---

class TestMSIResolve:
    def test_resolve_returns_token(self) -> None:
        """TC-6: ManagedIdentityAuth should return token from azure-identity."""
        mock_token = MagicMock()
        mock_token.token = "msi-token-456"

        mock_credential_cls = MagicMock()
        mock_credential_instance = MagicMock()
        mock_credential_instance.get_token.return_value = mock_token
        mock_credential_cls.return_value = mock_credential_instance

        with patch.dict("sys.modules", {
            "azure": MagicMock(),
            "azure.identity": MagicMock(ManagedIdentityCredential=mock_credential_cls),
        }):
            auth = ManagedIdentityAuth()
            result = auth.resolve()

        assert result == "msi-token-456", (
            "ManagedIdentityAuth should return token from azure-identity"
        )


# --- TC-7: ManagedIdentityAuth raises ImportError without azure-identity (AC-3) ---

class TestMSIImportError:
    def test_raises_import_error_without_azure(self) -> None:
        """TC-7: ManagedIdentityAuth should raise ImportError with install instructions."""
        with patch.dict("sys.modules", {
            "azure": None,
            "azure.identity": None,
        }):
            with pytest.raises(ImportError, match="azure-identity"):
                ManagedIdentityAuth()
