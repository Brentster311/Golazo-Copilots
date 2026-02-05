"""
Tests for discovery endpoint.
"""

import pytest
from unittest.mock import MagicMock
import responses

from s360_client.config import S360Config
from s360_client.endpoints.discovery import DiscoveryEndpoint


class TestDiscoveryEndpoint:
    """Tests for API discovery."""

    def test_discover_returns_known_endpoints(self, test_config: S360Config):
        """Given API access, when discovering, then return at least known endpoints."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        discovery = DiscoveryEndpoint(test_config, get_token)

        # Act
        result = discovery.discover_endpoints(
            include_known=True,
            probe_common=False,  # Don't probe, just return known
        )

        # Assert
        assert len(result) >= 2
        paths = [e.path for e in result]
        assert "/ActionItems/GetEtaHistoryById" in paths
        assert "/ActionItems/SaveETAsByIds" in paths

    @responses.activate
    def test_discover_finds_new_endpoints(self, test_config: S360Config):
        """Given API responds to probed paths, when discovering, then return new endpoints."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        discovery = DiscoveryEndpoint(test_config, get_token)

        # Mock a successful response for /Services
        responses.add(
            responses.GET,
            f"{test_config.base_url}/Services",
            json={"services": []},
            status=200,
        )

        # Mock 404 for all other probed paths
        responses.add_passthru("https://")

        # Act - only probe /Services
        result = discovery.discover_endpoints(
            include_known=False,
            probe_common=False,
            additional_paths=[("/Services", "GET")],
        )

        # Assert
        assert any(e.path == "/Services" and e.discovered for e in result)

    @responses.activate
    def test_discover_handles_not_found(self, test_config: S360Config):
        """Given API returns 404 for probed path, when discovering, then skip without error."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        discovery = DiscoveryEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/NonExistentEndpoint",
            json={"error": "Not found"},
            status=404,
        )

        # Act
        result = discovery.discover_endpoints(
            include_known=False,
            probe_common=False,
            additional_paths=[("/NonExistentEndpoint", "GET")],
        )

        # Assert - should not include 404 endpoint
        paths = [e.path for e in result]
        assert "/NonExistentEndpoint" not in paths

    @responses.activate
    def test_discover_handles_400_as_exists(self, test_config: S360Config):
        """Given API returns 400, then treat endpoint as existing (needs params)."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        discovery = DiscoveryEndpoint(test_config, get_token)

        responses.add(
            responses.GET,
            f"{test_config.base_url}/NeedsParams",
            json={"error": "Missing required parameter"},
            status=400,
        )

        # Act
        result = discovery.discover_endpoints(
            include_known=False,
            probe_common=False,
            additional_paths=[("/NeedsParams", "GET")],
        )

        # Assert - 400 means endpoint exists but needs params
        assert any(e.path == "/NeedsParams" and e.discovered for e in result)


class TestGetSwaggerSpec:
    """Tests for OpenAPI/Swagger spec retrieval."""

    @responses.activate
    def test_get_swagger_spec_found(self, test_config: S360Config):
        """Given swagger.json exists, when fetching, then return spec dict."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        discovery = DiscoveryEndpoint(test_config, get_token)

        swagger_spec = {
            "openapi": "3.0.0",
            "info": {"title": "S360 API", "version": "1.0"},
            "paths": {},
        }

        responses.add(
            responses.GET,
            f"{test_config.base_url}/swagger.json",
            json=swagger_spec,
            status=200,
        )

        # Act
        result = discovery.get_swagger_spec()

        # Assert
        assert result is not None
        assert result["openapi"] == "3.0.0"

    @responses.activate
    def test_get_swagger_spec_not_found(self, test_config: S360Config):
        """Given no swagger spec exists, when fetching, then return None."""
        # Arrange
        get_token = MagicMock(return_value="mock_token")
        discovery = DiscoveryEndpoint(test_config, get_token)

        # Mock 404 for all swagger paths
        for path in ["/swagger.json", "/swagger/v1/swagger.json", "/openapi.json", "/api/swagger.json"]:
            responses.add(
                responses.GET,
                f"{test_config.base_url}{path}",
                json={"error": "Not found"},
                status=404,
            )

        # Act
        result = discovery.get_swagger_spec()

        # Assert
        assert result is None
