"""State creation and validation logic."""

import re
from datetime import datetime, timezone
from typing import Literal

from .types import WorkItemState, RoleHistoryEntry


Profile = Literal["complete", "express", "spike"]
VALID_PROFILES = {"complete", "express", "spike"}


def create_initial_state(work_item_id: str, profile: Profile) -> WorkItemState:
    """Create initial state for a new work item."""
    now = datetime.now(timezone.utc)
    
    return WorkItemState(
        schema_version="1.0",
        work_item_id=work_item_id,
        profile=profile,
        current_phase="definition",
        current_role="project-owner-assistant",
        created_at=now,
        updated_at=now,
        role_history=[
            RoleHistoryEntry(
                role="project-owner-assistant",
                entered_at=now,
                exited_at=None,
            )
        ],
        deviations=[],
    )


def validate_work_item_id(work_item_id: str) -> tuple[bool, str | None]:
    """
    Validate work item ID.
    
    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message is None.
    """
    if not work_item_id:
        return False, "Invalid work item ID. Must not be empty."
    
    if work_item_id in (".", ".."):
        return False, "Invalid work item ID. Cannot be '.' or '..'."
    
    if len(work_item_id) > 100:
        return False, "Invalid work item ID. Must be 100 characters or less (too long)."
    
    # Enforce format: 1-4 letters, dash, 3+ digits (e.g., GCP-0001, AB-001)
    if not re.fullmatch(r'[A-Za-z]{1,4}-\d{3,}', work_item_id):
        return False, (
            f"Invalid work item ID '{work_item_id}'. "
            "Must be 1-4 letters, a dash, then 3 or more digits "
            "(e.g., GCP-0001, AB-001, TEST-1234)."
        )
    
    return True, None


def validate_profile(profile: str) -> tuple[bool, str | None]:
    """
    Validate profile.
    
    Returns:
        Tuple of (is_valid, error_message).
    """
    if profile not in VALID_PROFILES:
        return False, f"Invalid profile. Must be one of: {', '.join(sorted(VALID_PROFILES))}"
    return True, None
