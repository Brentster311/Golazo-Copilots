"""
Data models for S360 Client.

All models use dataclasses for type safety and auto-generated methods.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class UserInfo:
    """Information about the current authenticated user."""

    display_name: str
    alias: str
    user_principal_name: str
    mail: str

    @classmethod
    def from_graph_response(cls, data: dict[str, Any]) -> "UserInfo":
        """Create UserInfo from Microsoft Graph API response."""
        upn = data.get("userPrincipalName", "")
        alias = upn.split("@")[0] if "@" in upn else upn
        return cls(
            display_name=data.get("displayName", "Unknown"),
            alias=alias,
            user_principal_name=upn,
            mail=data.get("mail", upn),
        )


@dataclass
class EtaHistoryItem:
    """A single ETA history entry."""

    id: str
    eta: datetime | None
    status: str
    notes: str
    created_at: datetime | None = None

    @classmethod
    def from_api_response(cls, data: dict[str, Any]) -> "EtaHistoryItem":
        """Create EtaHistoryItem from S360 API response."""
        eta_str = data.get("eta") or data.get("Eta") or data.get("ETA")
        created_str = data.get("createdAt") or data.get("CreatedAt") or data.get("created_at")
        
        eta = None
        if eta_str:
            try:
                eta = datetime.fromisoformat(eta_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        created_at = None
        if created_str:
            try:
                created_at = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return cls(
            id=str(data.get("id") or data.get("Id") or data.get("ID", "")),
            eta=eta,
            status=data.get("status") or data.get("Status") or "",
            notes=data.get("notes") or data.get("Notes") or "",
            created_at=created_at,
        )


@dataclass
class EtaUpdate:
    """Request model for updating ETAs."""

    kpi_id: str
    service_id: str
    action_item_id: str
    new_eta: datetime
    notes: str
    sla_type: str = "InSla"

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to S360 API payload format."""
        return {
            "KpiId": self.kpi_id,
            "ServiceId": self.service_id,
            "ActionItemId": self.action_item_id,
            "Eta": self.new_eta.isoformat(),
            "UserStatus": self.notes,
            "SLAType": self.sla_type,
        }


@dataclass
class SaveResult:
    """Result of a save operation."""

    success: bool
    failed_items: list[str] = field(default_factory=list)
    error_message: str | None = None


@dataclass
class EndpointInfo:
    """Information about a discovered API endpoint."""

    path: str
    method: str
    description: str = ""
    parameters: list[str] = field(default_factory=list)
    discovered: bool = False  # True if discovered via probing, False if known
