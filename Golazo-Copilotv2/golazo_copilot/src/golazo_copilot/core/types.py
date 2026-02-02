"""Pydantic models for Golazo Copilot state."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, Field


class RoleHistoryEntry(BaseModel):
    """Entry in the role history tracking transitions."""
    role: str
    entered_at: datetime
    exited_at: datetime | None = None


class Deviation(BaseModel):
    """Record of a workflow deviation/skip with justification."""
    action: str
    reason: str
    role: str
    timestamp: datetime


class WorkItemState(BaseModel):
    """Complete state for a work item."""
    schema_version: Literal["1.0"] = "1.0"
    work_item_id: str
    profile: Literal["complete", "express", "spike"]
    current_phase: Literal["definition", "development", "completion"]
    current_role: str
    created_at: datetime
    updated_at: datetime
    dor: dict[str, bool] = Field(default_factory=lambda: {
        "userStory": False,
        "designDoc": False,
        "reviewComments": False,
        "testCases": False,
    })
    dod: dict[str, bool] = Field(default_factory=lambda: {
        "branchCreated": False,
        "testsWrittenFirst": False,
        "testsPass": False,
        "buildPasses": False,
        "docsUpdated": False,
        "refactorComplete": False,
        "committed": False,
    })
    role_history: list[RoleHistoryEntry] = Field(default_factory=list)
    deviations: list[Deviation] = Field(default_factory=list)


class GcpInitResult(BaseModel):
    """Result from gcp_init tool."""
    success: bool
    error: str | None = None
    work_item_id: str | None = None
    current_role: str | None = None
    role_instructions: str | None = None
