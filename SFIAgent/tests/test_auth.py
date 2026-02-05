"""
Tests for authentication module.
"""

import pytest
from unittest.mock import MagicMock, patch
import responses

from azure.core.exceptions import ClientAuthenticationError

from s360_client.auth import AuthManager
from s360_client.config import S360Config
from s360_client.exceptions import S360AuthError
from s360_client.models import UserInfo


class TestAuthManagerGetS360Token:
    """Tests for S360 token acquisition."""

    def test_auth_success(self, test_config: S360Config):
        """Given valid Azure CLI credentials, when getting token, then return valid bearer token."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred_class:
            # Arrange
            mock_credential = MagicMock()
            mock_cred_class.return_value = mock_credential
            mock_token = MagicMock()
            mock_token.token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.test"
            mock_credential.get_token.return_value = mock_token

            auth = AuthManager(test_config)

            # Act
            token = auth.get_s360_token()

            # Assert
            assert token is not None
            assert isinstance(token, str)
            assert token.startswith("eyJ")
            mock_credential.get_token.assert_called_once_with(test_config.s360_scope)

    def test_auth_failure_not_logged_in(self, test_config: S360Config):
        """Given no Azure CLI login, when getting token, then raise S360AuthError."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred_class:
            # Arrange
            mock_credential = MagicMock()
            mock_cred_class.return_value = mock_credential
            mock_credential.get_token.side_effect = ClientAuthenticationError(
                "Azure CLI not logged in"
            )

            auth = AuthManager(test_config)

            # Act & Assert
            with pytest.raises(S360AuthError) as exc_info:
                auth.get_s360_token()

            assert "az login" in str(exc_info.value).lower()

    def test_auth_failure_wrong_scope(self, test_config: S360Config):
        """Given invalid scope, when getting token, then raise S360AuthError with scope info."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred_class:
            # Arrange
            mock_credential = MagicMock()
            mock_cred_class.return_value = mock_credential
            mock_credential.get_token.side_effect = ClientAuthenticationError(
                "Invalid scope"
            )

            auth = AuthManager(test_config)

            # Act & Assert
            with pytest.raises(S360AuthError) as exc_info:
                auth.get_s360_token()

            assert exc_info.value.scope == test_config.s360_scope


class TestAuthManagerGetUserInfo:
    """Tests for user info retrieval."""

    @responses.activate
    def test_get_user_info_success(
        self, test_config: S360Config, sample_user_info: dict
    ):
        """Given valid auth, when getting user info, then return user dict with alias."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred_class:
            # Arrange
            mock_credential = MagicMock()
            mock_cred_class.return_value = mock_credential
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_credential.get_token.return_value = mock_token

            responses.add(
                responses.GET,
                "https://graph.microsoft.com/v1.0/me",
                json=sample_user_info,
                status=200,
            )

            auth = AuthManager(test_config)

            # Act
            user = auth.get_current_user()

            # Assert
            assert isinstance(user, UserInfo)
            assert user.display_name == "Test User"
            assert user.alias == "testuser"
            assert user.mail == "testuser@microsoft.com"

    @responses.activate
    def test_get_user_info_failure_forbidden(self, test_config: S360Config):
        """Given Graph API error, when getting user info, then raise S360AuthError."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred_class:
            # Arrange
            mock_credential = MagicMock()
            mock_cred_class.return_value = mock_credential
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_credential.get_token.return_value = mock_token

            responses.add(
                responses.GET,
                "https://graph.microsoft.com/v1.0/me",
                json={"error": "forbidden"},
                status=403,
            )

            auth = AuthManager(test_config)

            # Act & Assert
            with pytest.raises(S360AuthError) as exc_info:
                auth.get_current_user()

            assert "403" in str(exc_info.value)

    @responses.activate
    def test_get_user_info_caches_result(
        self, test_config: S360Config, sample_user_info: dict
    ):
        """Given successful fetch, when called again, then return cached result."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred_class:
            # Arrange
            mock_credential = MagicMock()
            mock_cred_class.return_value = mock_credential
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_credential.get_token.return_value = mock_token

            responses.add(
                responses.GET,
                "https://graph.microsoft.com/v1.0/me",
                json=sample_user_info,
                status=200,
            )

            auth = AuthManager(test_config)

            # Act
            user1 = auth.get_current_user()
            user2 = auth.get_current_user()

            # Assert - should only call API once
            assert user1 == user2
            assert len(responses.calls) == 1
