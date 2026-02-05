"""
S360 Client - Python library for Microsoft S360 API access.

Usage:
    from s360_client import S360Client

    client = S360Client()
    user = client.get_current_user()
    history = client.get_eta_history(kpi_id, action_item_id)
"""

from s360_client.client import S360Client
from s360_client.config import S360Config
from s360_client.exceptions import (
    S360Error,
    S360AuthError,
    S360ApiError,
    S360CacheError,
)
from s360_client.models import (
    UserInfo,
    EtaHistoryItem,
    EtaUpdate,
    SaveResult,
    EndpointInfo,
)

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
]
