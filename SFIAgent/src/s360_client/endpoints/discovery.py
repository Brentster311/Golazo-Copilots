"""
API discovery endpoint for S360 Client.
"""

import logging
from typing import Any

import requests

from s360_client.config import S360Config
from s360_client.models import EndpointInfo

logger = logging.getLogger(__name__)

__all__ = ["DiscoveryEndpoint"]

# Common REST API paths to probe
PROBE_PATHS = [
    # Known endpoints
    ("/ActionItems/GetEtaHistoryById", "GET"),
    ("/ActionItems/SaveETAsByIds", "POST"),
    # Common patterns to discover
    ("/Services", "GET"),
    ("/Services/GetAll", "GET"),
    ("/KPIs", "GET"),
    ("/KPIs/GetAll", "GET"),
    ("/ActionItems", "GET"),
    ("/ActionItems/GetAll", "GET"),
    ("/Users", "GET"),
    ("/Users/GetCurrent", "GET"),
    ("/Health", "GET"),
    ("/Status", "GET"),
    ("/api/version", "GET"),
    ("/swagger", "GET"),
    ("/swagger.json", "GET"),
    ("/openapi.json", "GET"),
]


class DiscoveryEndpoint:
    """Discovers available S360 API endpoints."""

    def __init__(
        self,
        config: S360Config,
        get_token_func: callable,
    ) -> None:
        self.config = config
        self._get_token = get_token_func

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authorization."""
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _probe_endpoint(self, path: str, method: str) -> EndpointInfo | None:
        """
        Probe a single endpoint to check if it exists.

        Returns EndpointInfo if endpoint responds, None otherwise.
        """
        url = f"{self.config.base_url}{path}"
        headers = self._get_headers()

        try:
            # Use a shorter timeout for probing
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=10,
            )

            # Consider these as "endpoint exists"
            if response.status_code in (200, 400, 401, 403, 405):
                logger.debug("Found endpoint: %s %s (HTTP %d)", method, path, response.status_code)
                
                # Try to extract description from response
                description = ""
                if response.status_code == 405:
                    description = "Method not allowed (try different HTTP method)"
                elif response.status_code in (401, 403):
                    description = "Requires authentication/authorization"
                elif response.status_code == 400:
                    description = "Endpoint exists (bad request - may need parameters)"

                return EndpointInfo(
                    path=path,
                    method=method,
                    description=description,
                    discovered=True,
                )

            return None

        except requests.Timeout:
            logger.debug("Timeout probing: %s %s", method, path)
            return None
        except requests.RequestException as e:
            logger.debug("Error probing %s %s: %s", method, path, str(e))
            return None

    def discover_endpoints(
        self,
        include_known: bool = True,
        probe_common: bool = True,
        additional_paths: list[tuple[str, str]] | None = None,
    ) -> list[EndpointInfo]:
        """
        Discover available S360 API endpoints.

        Args:
            include_known: Include known endpoints from config.
            probe_common: Probe common REST API patterns.
            additional_paths: Additional (path, method) tuples to probe.

        Returns:
            List of discovered endpoints.
        """
        logger.info("Starting API discovery...")
        discovered: list[EndpointInfo] = []
        seen_paths: set[str] = set()

        # Add known endpoints
        if include_known:
            for method, path, description in self.config.KNOWN_ENDPOINTS:
                key = f"{method}:{path}"
                if key not in seen_paths:
                    discovered.append(EndpointInfo(
                        path=path,
                        method=method,
                        description=description,
                        discovered=False,  # Known, not discovered
                    ))
                    seen_paths.add(key)

        # Probe common paths
        paths_to_probe = []
        if probe_common:
            paths_to_probe.extend(PROBE_PATHS)
        if additional_paths:
            paths_to_probe.extend(additional_paths)

        for path, method in paths_to_probe:
            key = f"{method}:{path}"
            if key in seen_paths:
                continue

            endpoint_info = self._probe_endpoint(path, method)
            if endpoint_info:
                discovered.append(endpoint_info)
                seen_paths.add(key)

        logger.info("Discovery complete: found %d endpoints", len(discovered))
        return discovered

    def get_swagger_spec(self) -> dict[str, Any] | None:
        """
        Try to retrieve OpenAPI/Swagger specification.

        Returns:
            The spec dict if found, None otherwise.
        """
        swagger_paths = [
            "/swagger.json",
            "/swagger/v1/swagger.json",
            "/openapi.json",
            "/api/swagger.json",
        ]

        headers = self._get_headers()

        for path in swagger_paths:
            url = f"{self.config.base_url}{path}"
            try:
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    try:
                        spec = response.json()
                        logger.info("Found OpenAPI spec at: %s", path)
                        return spec
                    except ValueError:
                        continue
            except requests.RequestException:
                continue

        logger.info("No OpenAPI spec found")
        return None
