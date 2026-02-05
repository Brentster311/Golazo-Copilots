"""
S360 API endpoint implementations.
"""

from accia_s360.endpoints.action_items import ActionItemsEndpoint
from accia_s360.endpoints.discovery import DiscoveryEndpoint
from accia_s360.endpoints.extended import ExtendedEndpoints

__all__ = ["ActionItemsEndpoint", "DiscoveryEndpoint", "ExtendedEndpoints"]
