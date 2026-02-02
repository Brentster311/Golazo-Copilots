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
        current_role="project-owner",
        created_at=now,
        updated_at=now,
        dor={
            "userStory": False,
            "designDoc": False,
            "reviewComments": False,
            "testCases": False,
        },
        dod={
            "branchCreated": False,
            "testsWrittenFirst": False,
            "testsPass": False,
            "buildPasses": False,
            "docsUpdated": False,
            "refactorComplete": False,
            "committed": False,
        },
        role_history=[
            RoleHistoryEntry(
                role="project-owner",
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
    
    # Only allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', work_item_id):
        return False, "Invalid work item ID. Use alphanumeric, hyphens, underscores only."
    
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
