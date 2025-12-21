"""Data models for the Golazo process."""

from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TicketPriority(str, Enum):
    """Priority levels for tickets."""
    SWARM = "swarm"  # Urgent, drop everything
    INTERRUPT = "interrupt"  # Important but not urgent
    PLANNED = "planned"  # Normal planned work


class TicketStatus(str, Enum):
    """Status of a ticket in the workflow."""
    BACKLOG = "backlog"
    DESIGN = "design"
    DESIGN_REVIEW = "design_review"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    CODE_REVIEW = "code_review"
    VALIDATION = "validation"
    DONE = "done"


class DesignDoc(BaseModel):
    """A lightweight design document for a ticket."""
    id: str
    ticket_id: str
    title: str
    problem_statement: str
    proposed_solution: str
    alternatives_considered: Optional[str] = None
    risks: Optional[str] = None
    success_criteria: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    author: str
    approvals: list[str] = Field(default_factory=list)
    required_approvals: int = 2


class Ticket(BaseModel):
    """A work ticket in the Golazo process."""
    id: str
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    design_doc: Optional[DesignDoc] = None
    assignee: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    estimated_days: Optional[float] = None
    actual_days: Optional[float] = None
    labels: list[str] = Field(default_factory=list)
    validation_notes: Optional[str] = None


class CodeReview(BaseModel):
    """A code review for a pull request."""
    id: str
    ticket_id: str
    pr_url: str
    reviewer: str
    status: str  # "pending", "approved", "changes_requested"
    comments: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)


class WorkflowState(BaseModel):
    """Current state of the workflow board."""
    tickets: list[Ticket] = Field(default_factory=list)
    wip_limit: int = 3  # Default WIP limit
    current_wip: int = 0
    team_members: list[str] = Field(default_factory=list)
