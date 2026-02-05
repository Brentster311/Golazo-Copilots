"""
S360 API endpoint implementations.
"""

from s360_client.endpoints.action_items import ActionItemsEndpoint
from s360_client.endpoints.discovery import DiscoveryEndpoint
from s360_client.endpoints.extended import ExtendedEndpoints

__all__ = ["ActionItemsEndpoint", "DiscoveryEndpoint", "ExtendedEndpoints"]
