"""golazo_consent tool - Record consent for workflow deviations."""

from pathlib import Path
from datetime import datetime, timezone
from typing import Literal

from ..core.types import Deviation
from ..core.persistence import load_state, save_state, work_item_exists, DEFAULT_WORKITEMS_DIR


# Valid deviation actions
VALID_ACTIONS = {
    "skip_outputs",     # Bypass required outputs gate
    "skip_role",        # Skip a role in the workflow
    "revert_progress",  # Undo completed items
    "custom",           # Custom deviation
}

MINIMUM_REASON_LENGTH = 10


async def golazo_consent(
    work_item_id: str,
    action: str,
    reason: str,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
) -> dict:
    """
    Record consent for a workflow deviation.
    
    Args:
        work_item_id: Work item identifier
        action: Type of deviation (skip_dor, skip_dod, skip_role, etc.)
        reason: Justification for the deviation (min 10 chars)
        work_items_dir: Directory for work items
    
    Returns:
        Dict with success status and deviation ID
    """
    # Check work item exists
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error": f"Work item '{work_item_id}' not found.",
        }
    
    # Validate action
    if action not in VALID_ACTIONS:
        return {
            "success": False,
            "error": f"Invalid action '{action}'. Valid actions: {', '.join(sorted(VALID_ACTIONS))}",
        }
    
    # Validate reason
    if not reason or len(reason.strip()) < MINIMUM_REASON_LENGTH:
        return {
            "success": False,
            "error": f"Reason required for deviation. Must be at least {MINIMUM_REASON_LENGTH} characters.",
        }
    
    # Load current state
    state = load_state(work_item_id, work_items_dir)
    
    # Generate deviation ID
    deviation_count = len(state.deviations) + 1
    deviation_id = f"dev-{deviation_count:03d}"
    
    # Create deviation record
    now = datetime.now(timezone.utc)
    deviation = Deviation(
        id=deviation_id,
        action=action,
        reason=reason.strip(),
        role=state.current_role,
        timestamp=now,
        consumed=False,
    )
    
    # Append to deviations
    state.deviations.append(deviation)
    state.updated_at = now
    
    # Save state
    save_state(work_item_id, state, work_items_dir)
    
    return {
        "success": True,
        "deviation_id": deviation_id,
        "action": action,
        "message": f"Consent recorded from Project Owner. You may now use force=True for {action}.",
    }


def has_valid_consent(state, action: str) -> bool:
    """
    Check if there's a valid (unconsumed) consent for the given action.
    
    Args:
        state: WorkItemState
        action: Action type to check
    
    Returns:
        True if valid consent exists
    """
    for deviation in state.deviations:
        if deviation.action == action and not deviation.consumed:
            return True
    return False


def consume_consent(state, action: str) -> str | None:
    """
    Mark a consent as consumed and return its ID.
    
    Args:
        state: WorkItemState
        action: Action type to consume
    
    Returns:
        Deviation ID if found and consumed, None otherwise
    """
    for deviation in state.deviations:
        if deviation.action == action and not deviation.consumed:
            deviation.consumed = True
            deviation.consumed_at = datetime.now(timezone.utc)
            return deviation.id
    return None
