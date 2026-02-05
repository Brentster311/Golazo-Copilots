"""
Tests for action items endpoint.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
import requests
import responses

from s360_client.config import S360Config
from s360_client.endpoints.action_items import ActionItemsEndpoint
from s360_client.exceptions import S360ApiError, S360AuthError
from s360_client.models import EtaUpdate


class TestGetEtaHistory:
    """Tests for GetEtaHistoryById endpoint."""

    @responses.activate
    def test_get_eta_history_success(
        self, test_config: S360Config, sample_eta_history: list[dict]
    ):
        """Given valid IDs, when calling get_eta_history, then return history list."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
            json=sample_eta_history,
            status=200,
        )

        # Act
        result = endpoint.get_eta_history("kpi-123", "action-456")

        # Assert
        assert len(result) == 2
        assert result[0].id == "item-1"
        assert result[0].status == "InProgress"
        assert result[1].notes == "Done"

    @responses.activate
    def test_get_eta_history_not_found(self, test_config: S360Config):
        """Given invalid IDs, when calling get_eta_history, then raise S360ApiError."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
            json={"error": "Not found"},
            status=404,
        )

        # Act & Assert
        with pytest.raises(S360ApiError) as exc_info:
            endpoint.get_eta_history("invalid-kpi", "invalid-action")

        assert exc_info.value.status_code == 404

    @responses.activate
    def test_get_eta_history_empty_response(self, test_config: S360Config):
        """Given valid IDs with no history, when calling get_eta_history, then return empty list."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
            json=[],
            status=200,
        )

        # Act
        result = endpoint.get_eta_history("kpi-123", "action-456")

        # Assert
        assert result == []

    @responses.activate
    def test_get_eta_history_unauthorized(self, test_config: S360Config):
        """Given expired token, when calling get_eta_history, then raise S360AuthError."""
        # Arrange
        get_token = MagicMock(return_value="expired_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
            json={"error": "Unauthorized"},
            status=401,
        )

        # Act & Assert
        with pytest.raises(S360AuthError):
            endpoint.get_eta_history("kpi-123", "action-456")


class TestSaveEtas:
    """Tests for SaveETAsByIds endpoint."""

    @responses.activate
    def test_save_etas_success(self, test_config: S360Config):
        """Given valid ETA data, when calling save_etas, then return success."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.POST,
            f"{test_config.base_url}/ActionItems/SaveETAsByIds",
            json={"success": True},
            status=200,
        )

        updates = [
            EtaUpdate(
                kpi_id="kpi-123",
                service_id="svc-456",
                action_item_id="action-789",
                new_eta=datetime(2026, 3, 1, tzinfo=timezone.utc),
                notes="Updated ETA",
            )
        ]

        # Act
        result = endpoint.save_etas(updates)

        # Assert
        assert result.success is True
        assert len(result.failed_items) == 0

    @responses.activate
    def test_save_etas_validation_error(self, test_config: S360Config):
        """Given invalid ETA data, when calling save_etas, then return failure result."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.POST,
            f"{test_config.base_url}/ActionItems/SaveETAsByIds",
            json={"failedItems": ["action-789"], "message": "Validation failed"},
            status=200,  # S360 returns 200 with failedItems for partial failures
        )

        updates = [
            EtaUpdate(
                kpi_id="",  # Invalid
                service_id="svc-456",
                action_item_id="action-789",
                new_eta=datetime(2026, 3, 1, tzinfo=timezone.utc),
                notes="Test",
            )
        ]

        # Act
        result = endpoint.save_etas(updates)

        # Assert
        assert result.success is False
        assert "action-789" in result.failed_items

    @responses.activate
    def test_save_etas_unauthorized(self, test_config: S360Config):
        """Given expired token, when calling save_etas, then return failure result."""
        # Arrange
        config = S360Config(
            timeout_seconds=5,
            retry_count=0,  # No retry for this test
            cache_directory=test_config.cache_directory,
        )
        get_token = MagicMock(return_value="expired_token")
        endpoint = ActionItemsEndpoint(config, get_token)

        responses.add(
            responses.POST,
            f"{config.base_url}/ActionItems/SaveETAsByIds",
            json={"error": "Unauthorized"},
            status=401,
        )

        updates = [
            EtaUpdate(
                kpi_id="kpi-123",
                service_id="svc-456",
                action_item_id="action-789",
                new_eta=datetime(2026, 3, 1, tzinfo=timezone.utc),
                notes="Test",
            )
        ]

        # Act
        result = endpoint.save_etas(updates)

        # Assert - save_etas returns SaveResult with error instead of raising
        assert result.success is False
        assert result.error_message is not None
        assert "401" in result.error_message


class TestApiErrorHandling:
    """Tests for API error handling."""

    @responses.activate
    def test_api_timeout(self, test_config: S360Config):
        """Given slow API, when timeout exceeded, then raise S360ApiError."""
        # Arrange
        config = S360Config(
            timeout_seconds=1,
            retry_count=0,
            cache_directory=test_config.cache_directory,
        )
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(config, get_token)

        responses.add(
            responses.GET,
            f"{config.base_url}/ActionItems/GetEtaHistoryById",
            body=requests.exceptions.Timeout("Connection timed out"),
        )

        # Act & Assert
        with pytest.raises(S360ApiError) as exc_info:
            endpoint.get_eta_history("kpi-123", "action-456")

        assert "timeout" in str(exc_info.value).lower() or "timed out" in str(exc_info.value).lower()

    @responses.activate
    def test_server_error_500(self, test_config: S360Config):
        """Given API returns 500, when calling, then raise S360ApiError."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
            json={"error": "Internal server error"},
            status=500,
        )

        # Act & Assert
        with pytest.raises(S360ApiError) as exc_info:
            endpoint.get_eta_history("kpi-123", "action-456")

        assert exc_info.value.status_code == 500

    @responses.activate
    def test_malformed_json_response(self, test_config: S360Config):
        """Given API returns invalid JSON, when parsing, then raise S360ApiError."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
            body="not valid json {{{",
            status=200,
            content_type="application/json",
        )

        # Act & Assert
        with pytest.raises(S360ApiError) as exc_info:
            endpoint.get_eta_history("kpi-123", "action-456")

        assert "json" in str(exc_info.value).lower() or "parse" in str(exc_info.value).lower()

    @responses.activate
    def test_forbidden_error(self, test_config: S360Config):
        """Given user lacks permission, when calling API, then raise S360AuthError."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        endpoint = ActionItemsEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/ActionItems/GetEtaHistoryById",
            json={"error": "Forbidden"},
            status=403,
        )

        # Act & Assert
        with pytest.raises(S360AuthError) as exc_info:
            endpoint.get_eta_history("kpi-123", "action-456")

        assert "permission" in str(exc_info.value).lower()
