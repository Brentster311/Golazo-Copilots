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
    assigned_to: str = ""
    sla_type: str = "InSla"

    def to_api_payload(self) -> dict[str, Any]:
        """Convert to S360 API payload format.

        Produces the payload shape used by the production Sauron SFI_Agent::

            {
              "ETADate": "2026-02-28",
              "UserStatus": "...",
              "KpiId": "guid",
              "ActionItems": [{
                "ServiceId": "guid",
                "ActionItemId": "id",
                "AssignedTo": "alias",
                "SLAType": "InSla"
              }]
            }
        """
        return {
            "ETADate": self.new_eta.strftime("%Y-%m-%d"),
            "UserStatus": self.notes,
            "KpiId": self.kpi_id,
            "ActionItems": [
                {
                    "ServiceId": self.service_id,
                    "ActionItemId": self.action_item_id,
                    "AssignedTo": self.assigned_to,
                    "SLAType": self.sla_type,
                }
            ],
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


@dataclass
class OrgPerson:
    """A person in the Microsoft org hierarchy (from MS Graph API)."""

    alias: str
    display_name: str
    job_title: str | None = None
    department: str | None = None
    object_id: str = ""

    @classmethod
    def from_graph_response(cls, data: dict[str, Any]) -> "OrgPerson":
        """Create OrgPerson from Microsoft Graph API response.

        Expected fields (via $select): displayName, mailNickname,
        jobTitle, department, id.
        """
        alias = data.get("mailNickname", "")
        if not alias:
            # Fallback: extract from userPrincipalName
            upn = data.get("userPrincipalName", "")
            alias = upn.split("@")[0] if "@" in upn else upn
        return cls(
            alias=alias,
            display_name=data.get("displayName", "Unknown"),
            job_title=data.get("jobTitle"),
            department=data.get("department"),
            object_id=str(data.get("id", "")),
        )

    def is_sc_alt(self) -> bool:
        """Check if this person is a non-EA SC ALT account."""
        if self.alias.lower().startswith("sc-"):
            return True
        if self.display_name and "NON EA SC ALT" in self.display_name.upper():
            return True
        return False


@dataclass
class OrgTree:
    """A recursive org tree node: a person and their direct reports."""

    person: OrgPerson
    direct_reports: list["OrgTree"] = field(default_factory=list)
