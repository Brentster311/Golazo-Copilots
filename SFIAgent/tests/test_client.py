"""
Tests for main S360Client facade.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import responses

from s360_client import S360Client, S360Config
from s360_client.exceptions import S360AuthError, S360ApiError
from s360_client.models import UserInfo, EtaUpdate


class TestS360Client:
    """Tests for main client facade."""

    def test_client_initializes_with_default_config(self):
        """Given no config, when creating client, then use defaults."""
        # Act
        with patch("s360_client.auth.AzureCliCredential"):
            client = S360Client()

        # Assert
        assert client.config is not None
        assert client.config.base_url == "https://api.vnext.s360.msftcloudes.com/v1"

    def test_client_accepts_custom_config(self, temp_cache_dir):
        """Given custom config, when creating client, then use custom values."""
        # Arrange
        config = S360Config(
            base_url="https://custom.api.com/v2",
            timeout_seconds=60,
            cache_directory=temp_cache_dir,
        )

        # Act
        with patch("s360_client.auth.AzureCliCredential"):
            client = S360Client(config)

        # Assert
        assert client.config.base_url == "https://custom.api.com/v2"
        assert client.config.timeout_seconds == 60


class TestClientGetCurrentUser:
    """Tests for get_current_user method."""

    @responses.activate
    def test_get_current_user_success(self, test_config, sample_user_info):
        """Given valid auth, when getting user, then return UserInfo."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred:
            # Arrange
            mock_instance = MagicMock()
            mock_cred.return_value = mock_instance
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_instance.get_token.return_value = mock_token

            responses.add(
                responses.GET,
                "https://graph.microsoft.com/v1.0/me",
                json=sample_user_info,
                status=200,
            )

            client = S360Client(test_config)

            # Act
            user = client.get_current_user()

            # Assert
            assert isinstance(user, UserInfo)
            assert user.alias == "testuser"


class TestClientGetEtaHistory:
    """Tests for get_eta_history method."""

    @responses.activate
    def test_get_eta_history_with_cache(self, test_config, sample_eta_history):
        """Given cacheable request, when called twice, then use cache on second call."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred:
            # Arrange
            mock_instance = MagicMock()
            mock_cred.return_value = mock_instance
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_instance.get_token.return_value = mock_token

            responses.add(
                responses.GET,
                f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
                json=sample_eta_history,
                status=200,
            )

            client = S360Client(test_config)

            # Act
            result1 = client.get_eta_history("kpi-123", "action-456")
            result2 = client.get_eta_history("kpi-123", "action-456")

            # Assert
            assert len(result1) == 2
            assert result1 == result2
            assert len(responses.calls) == 1  # Only one API call

    @responses.activate
    def test_get_eta_history_bypass_cache(self, test_config, sample_eta_history):
        """Given use_cache=False, when called, then always hit API."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred:
            # Arrange
            mock_instance = MagicMock()
            mock_cred.return_value = mock_instance
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_instance.get_token.return_value = mock_token

            responses.add(
                responses.GET,
                f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
                json=sample_eta_history,
                status=200,
            )
            responses.add(
                responses.GET,
                f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
                json=sample_eta_history,
                status=200,
            )

            client = S360Client(test_config)

            # Act
            client.get_eta_history("kpi-123", "action-456", use_cache=False)
            client.get_eta_history("kpi-123", "action-456", use_cache=False)

            # Assert
            assert len(responses.calls) == 2  # Two API calls


class TestClientSaveEta:
    """Tests for save_eta convenience method."""

    @responses.activate
    def test_save_single_eta(self, test_config):
        """Given valid data, when saving single ETA, then succeed."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred:
            # Arrange
            mock_instance = MagicMock()
            mock_cred.return_value = mock_instance
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_instance.get_token.return_value = mock_token

            responses.add(
                responses.POST,
                f"{test_config.base_url}/ActionItems/SaveETAsByIds",
                json={"success": True},
                status=200,
            )

            client = S360Client(test_config)

            # Act
            result = client.save_eta(
                kpi_id="kpi-123",
                service_id="svc-456",
                action_item_id="action-789",
                new_eta=datetime(2026, 3, 1, tzinfo=timezone.utc),
                notes="Updated via test",
            )

            # Assert
            assert result.success is True


class TestClientTestConnection:
    """Tests for test_connection method."""

    @responses.activate
    def test_connection_all_pass(self, test_config, sample_user_info):
        """Given all services available, when testing, then all pass."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred:
            # Arrange
            mock_instance = MagicMock()
            mock_cred.return_value = mock_instance
            mock_token = MagicMock()
            mock_token.token = "mock_token"
            mock_instance.get_token.return_value = mock_token

            responses.add(
                responses.GET,
                "https://graph.microsoft.com/v1.0/me",
                json=sample_user_info,
                status=200,
            )

            client = S360Client(test_config)

            # Act
            result = client.test_connection()

            # Assert
            assert result["s360_auth"] is True
            assert result["graph_auth"] is True
            assert result["user_info"] is True
            assert result["user_alias"] == "testuser"

    def test_connection_auth_fails(self, test_config):
        """Given auth failure, when testing, then report failure."""
        with patch("s360_client.auth.AzureCliCredential") as mock_cred:
            # Arrange
            mock_instance = MagicMock()
            mock_cred.return_value = mock_instance
            from azure.core.exceptions import ClientAuthenticationError
            mock_instance.get_token.side_effect = ClientAuthenticationError("Not logged in")

            client = S360Client(test_config)

            # Act
            result = client.test_connection()

            # Assert
            assert result["s360_auth"] is False
            assert "s360_auth_error" in result
