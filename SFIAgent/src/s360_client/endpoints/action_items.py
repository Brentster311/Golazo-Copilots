"""
Action Items endpoint implementations.
"""

import logging
import time
from typing import Any

import requests

from s360_client.config import S360Config
from s360_client.exceptions import S360ApiError, S360AuthError
from s360_client.models import EtaHistoryItem, EtaUpdate, SaveResult

logger = logging.getLogger(__name__)

__all__ = ["ActionItemsEndpoint"]


class ActionItemsEndpoint:
    """Handles Action Items API operations."""

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

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> requests.Response:
        """Make an HTTP request with retry logic."""
        url = f"{self.config.base_url}{endpoint}"
        headers = self._get_headers()

        for attempt in range(self.config.retry_count + 1):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json_data,
                    timeout=self.config.timeout_seconds,
                )

                # Retry on transient errors
                if response.status_code in (429, 503, 504) and attempt < self.config.retry_count:
                    logger.warning(
                        "Transient error %d, retrying in %ds...",
                        response.status_code,
                        self.config.retry_delay_seconds,
                    )
                    time.sleep(self.config.retry_delay_seconds)
                    continue

                return response

            except requests.Timeout:
                if attempt < self.config.retry_count:
                    logger.warning("Request timeout, retrying...")
                    time.sleep(self.config.retry_delay_seconds)
                    continue
                raise S360ApiError(
                    "Request timed out",
                    endpoint=endpoint,
                )
            except requests.ConnectionError as e:
                raise S360ApiError(
                    f"Network connection error: {str(e)}",
                    endpoint=endpoint,
                ) from e
            except requests.RequestException as e:
                raise S360ApiError(
                    f"Request failed: {str(e)}",
                    endpoint=endpoint,
                ) from e

        # Should not reach here, but just in case
        raise S360ApiError("Max retries exceeded", endpoint=endpoint)

    def _handle_response(
        self,
        response: requests.Response,
        endpoint: str,
    ) -> Any:
        """Handle API response and raise appropriate errors."""
        if response.status_code == 401:
            raise S360AuthError(
                "Authentication expired",
                suggestion="Your token may have expired. Try 'az login' again.",
            )

        if response.status_code == 403:
            raise S360AuthError(
                "Access forbidden",
                suggestion="You may not have permission for this operation.",
            )

        if response.status_code == 404:
            raise S360ApiError(
                "Resource not found",
                endpoint=endpoint,
                status_code=404,
                response_body=response.text,
            )

        if response.status_code >= 400:
            raise S360ApiError(
                f"API error: {response.text}",
                endpoint=endpoint,
                status_code=response.status_code,
                response_body=response.text,
            )

        # Handle empty responses
        if not response.text:
            return None

        try:
            return response.json()
        except ValueError as e:
            raise S360ApiError(
                "Failed to parse JSON response",
                endpoint=endpoint,
                status_code=response.status_code,
                response_body=response.text,
            ) from e

    def get_eta_history(
        self,
        kpi_id: str,
        action_item_id: str,
    ) -> list[EtaHistoryItem]:
        """
        Get ETA history for an action item.

        Args:
            kpi_id: The KPI ID.
            action_item_id: The action item ID.

        Returns:
            List of ETA history items.

        Raises:
            S360ApiError: If the API call fails.
            S360AuthError: If authentication fails.
        """
        logger.info("Getting ETA history for action item: %s", action_item_id)
        
        endpoint = "/ActionItems/GetEtaHistoryById"
        params = {"KpiId": kpi_id, "id": action_item_id}

        response = self._make_request("GET", endpoint, params=params)
        data = self._handle_response(response, endpoint)

        if data is None:
            return []

        if isinstance(data, list):
            return [EtaHistoryItem.from_api_response(item) for item in data]

        # Handle wrapped response
        if isinstance(data, dict):
            items = data.get("items") or data.get("Items") or data.get("data") or []
            return [EtaHistoryItem.from_api_response(item) for item in items]

        return []

    def save_etas(self, updates: list[EtaUpdate]) -> SaveResult:
        """
        Save ETA updates.

        Args:
            updates: List of ETA updates to save.

        Returns:
            SaveResult indicating success/failure.

        Raises:
            S360ApiError: If the API call fails.
            S360AuthError: If authentication fails.
        """
        logger.info("Saving %d ETA updates", len(updates))
        
        endpoint = "/ActionItems/SaveETAsByIds"
        payload = {
            "items": [update.to_api_payload() for update in updates]
        }

        response = self._make_request("POST", endpoint, json_data=payload)

        # Handle non-200 responses
        if response.status_code != 200:
            try:
                data = response.json()
                return SaveResult(
                    success=False,
                    error_message=f"HTTP {response.status_code}: {data.get('message', data.get('error', response.text))}",
                )
            except ValueError:
                return SaveResult(
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}",
                )

        # Handle 200 response - check for partial failures
        try:
            data = response.json()
            if data is None:
                return SaveResult(success=True)
            
            failed = data.get("failedItems", [])
            if failed:
                logger.warning("Partial failure: %d items failed", len(failed))
                return SaveResult(
                    success=False,
                    failed_items=failed,
                    error_message=data.get("message"),
                )
            
            logger.info("ETA updates saved successfully")
            return SaveResult(success=True)
        except ValueError:
            # If we got 200 but can't parse JSON, assume success
            logger.info("ETA updates saved successfully")
            return SaveResult(success=True)
