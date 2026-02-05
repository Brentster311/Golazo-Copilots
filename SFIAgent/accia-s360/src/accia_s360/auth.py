"""
Azure authentication manager for S360 Client.
"""

import logging
from typing import Any

import requests
from azure.core.exceptions import ClientAuthenticationError
from azure.identity import AzureCliCredential

from accia_s360.config import S360Config
from accia_s360.exceptions import S360AuthError
from accia_s360.models import UserInfo

logger = logging.getLogger(__name__)

__all__ = ["S360Auth", "AuthManager"]


class S360Auth:
    """
    Handles Azure authentication for S360 API.
    
    This is the public authentication interface.
    """

    def __init__(self, config: S360Config | None = None) -> None:
        self._manager = AuthManager(config)

    def get_token(self) -> str:
        """Get S360 API token."""
        return self._manager.get_s360_token()

    def get_current_user(self) -> UserInfo:
        """Get current authenticated user info."""
        return self._manager.get_current_user()


class AuthManager:
    """Handles Azure authentication and token management."""

    def __init__(self, config: S360Config | None = None) -> None:
        self.config = config or S360Config()
        self._credential: AzureCliCredential | None = None
        self._cached_user_info: UserInfo | None = None

    def _get_credential(self) -> AzureCliCredential:
        """Get or create the Azure CLI credential."""
        if self._credential is None:
            self._credential = AzureCliCredential()
        return self._credential

    def get_s360_token(self) -> str:
        """
        Get a bearer token for S360 API access.

        Returns:
            str: The bearer token.

        Raises:
            S360AuthError: If authentication fails.
        """
        logger.debug("Acquiring S360 bearer token...")
        try:
            credential = self._get_credential()
            token = credential.get_token(self.config.s360_scope)
            logger.debug("Successfully acquired S360 bearer token")
            return token.token
        except ClientAuthenticationError as e:
            logger.error("S360 authentication failed: %s", str(e))
            raise S360AuthError(
                "Failed to acquire S360 token",
                scope=self.config.s360_scope,
                suggestion="Try running 'az login' to authenticate.",
            ) from e
        except Exception as e:
            logger.error("Unexpected auth error: %s", str(e))
            raise S360AuthError(
                f"Authentication error: {str(e)}",
                scope=self.config.s360_scope,
            ) from e

    def get_graph_token(self) -> str:
        """
        Get a bearer token for Microsoft Graph API access.

        Returns:
            str: The bearer token.

        Raises:
            S360AuthError: If authentication fails.
        """
        logger.debug("Acquiring Graph API bearer token...")
        try:
            credential = self._get_credential()
            token = credential.get_token(self.config.graph_scope)
            logger.debug("Successfully acquired Graph API bearer token")
            return token.token
        except ClientAuthenticationError as e:
            logger.error("Graph authentication failed: %s", str(e))
            raise S360AuthError(
                "Failed to acquire Graph token",
                scope=self.config.graph_scope,
                suggestion="Try running 'az login' to authenticate.",
            ) from e
        except Exception as e:
            logger.error("Unexpected auth error: %s", str(e))
            raise S360AuthError(
                f"Authentication error: {str(e)}",
                scope=self.config.graph_scope,
            ) from e

    def get_current_user(self, force_refresh: bool = False) -> UserInfo:
        """
        Get information about the currently authenticated user.

        Args:
            force_refresh: If True, bypass cache and fetch fresh data.

        Returns:
            UserInfo: The current user's information.

        Raises:
            S360AuthError: If authentication or API call fails.
        """
        if self._cached_user_info and not force_refresh:
            return self._cached_user_info

        logger.debug("Retrieving current user information...")
        try:
            token = self.get_graph_token()
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            response = requests.get(
                "https://graph.microsoft.com/v1.0/me",
                headers=headers,
                timeout=self.config.timeout_seconds,
            )

            if response.status_code == 200:
                data: dict[str, Any] = response.json()
                self._cached_user_info = UserInfo.from_graph_response(data)
                logger.info("Retrieved user info for: %s", self._cached_user_info.alias)
                return self._cached_user_info
            elif response.status_code in (401, 403):
                raise S360AuthError(
                    f"Access denied to Graph API (HTTP {response.status_code})",
                    scope=self.config.graph_scope,
                    suggestion="Your token may have expired. Try 'az login' again.",
                )
            else:
                raise S360AuthError(
                    f"Failed to get user info: {response.status_code}",
                    scope=self.config.graph_scope,
                )
        except requests.RequestException as e:
            logger.error("Network error getting user info: %s", str(e))
            raise S360AuthError(f"Network error: {str(e)}") from e
