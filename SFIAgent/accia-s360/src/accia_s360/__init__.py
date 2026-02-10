"""
accia-s360 - Python client for Microsoft S360 API.

Usage:
    from accia_s360 import S360Client

    client = S360Client()
    user = client.get_current_user()
    items = client.get_action_items(params)
"""

from accia_s360.client import S360Client
from accia_s360.config import S360Config
from accia_s360.exceptions import (
    S360Error,
    S360AuthError,
    S360ApiError,
    S360CacheError,
)
from accia_s360.models import (
    UserInfo,
    EtaHistoryItem,
    EtaUpdate,
    SaveResult,
    EndpointInfo,
    OrgPerson,
    OrgTree,
)
from accia_s360 import auth

__version__ = "0.1.0"

__all__ = [
    "S360Client",
    "S360Config",
    "S360Error",
    "S360AuthError",
    "S360ApiError",
    "S360CacheError",
    "UserInfo",
    "EtaHistoryItem",
    "EtaUpdate",
    "SaveResult",
    "EndpointInfo",
    "OrgPerson",
    "OrgTree",
    "auth",
]
