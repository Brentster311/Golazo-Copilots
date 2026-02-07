"""Pydantic models for Golazo Copilot state."""

from datetime import datetime
from typing import Literal, Any
from pydantic import BaseModel, Field, field_validator


class ChecklistItem(BaseModel):
    """A DoR/DoD item with evidence support."""
    complete: bool = False
    evidence: str | None = None
    validated_at: datetime | None = None


class RoleHistoryEntry(BaseModel):
    """Entry in the role history tracking transitions."""
    role: str
    entered_at: datetime
    exited_at: datetime | None = None


class Deviation(BaseModel):
    """Record of a workflow deviation/skip with justification."""
    id: str
    action: str
    reason: str
    role: str
    timestamp: datetime
    consumed: bool = False
    consumed_at: datetime | None = None


class WorkItemState(BaseModel):
    """Complete state for a work item."""
    schema_version: Literal["1.0"] = "1.0"
    work_item_id: str
    profile: Literal["complete", "express", "spike"]
    current_phase: Literal["definition", "development", "completion"]
    current_role: str
    created_at: datetime
    updated_at: datetime
    dor: dict[str, ChecklistItem] = Field(default_factory=lambda: {
        "userStory": ChecklistItem(),
        "designDoc": ChecklistItem(),
        "reviewComments": ChecklistItem(),
        "testCases": ChecklistItem(),
    })
    dod: dict[str, ChecklistItem] = Field(default_factory=lambda: {
        "branchCreated": ChecklistItem(),
        "testsWrittenFirst": ChecklistItem(),
        "testsPass": ChecklistItem(),
        "buildPasses": ChecklistItem(),
        "docsUpdated": ChecklistItem(),
        "refactorComplete": ChecklistItem(),
        "committed": ChecklistItem(),
        "retroComplete": ChecklistItem(),
    })
    role_history: list[RoleHistoryEntry] = Field(default_factory=list)
    deviations: list[Deviation] = Field(default_factory=list)

    @field_validator("dor", "dod", mode="before")
    @classmethod
    def migrate_legacy_checklist(cls, v: Any) -> dict[str, Any]:
        """Migrate legacy boolean format to ChecklistItem format."""
        if not isinstance(v, dict):
            return v
        result = {}
        for key, value in v.items():
            if isinstance(value, bool):
                # Legacy format: just a boolean -> convert to dict for pydantic
                result[key] = {"complete": value}
            elif isinstance(value, dict):
                # New format: already a dict
                result[key] = value
            else:
                result[key] = value
        return result


class GcpInitResult(BaseModel):
    """Result from gcp_init tool."""
    success: bool
    error: str | None = None
    work_item_id: str | None = None
    current_role: str | None = None
    role_instructions: str | None = None
