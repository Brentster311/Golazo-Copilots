"""gcp_transition tool - Transition between workflow roles."""

from datetime import datetime, timezone
from pathlib import Path

from ..core.types import RoleHistoryEntry
from ..core.persistence import load_state, save_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..core.transitions import (
    validate_role,
    validate_transition,
    is_backward_transition,
    get_phase_for_role,
    check_dor_gate,
    DOR_GATE_ROLE,
)
from ..roles.loader import load_role_instructions
from .gcp_consent import has_valid_consent, consume_consent


async def gcp_transition(
    work_item_id: str,
    role: str,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    project_root: Path | None = None,
    force: bool = False,
) -> dict:
    """
    Transition to a new role in the workflow.
    
    Args:
        work_item_id: Work item identifier
        role: Target role to transition to
        work_items_dir: Directory for work items
        project_root: Project root for local role overrides
        force: Force transition even if gates not met (requires prior consent)
    
    Returns:
        Dict with success status, current role/phase, and role instructions
    """
    # Check work item exists
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error": f"Work item '{work_item_id}' does not exist. Use gcp_init first.",
        }
    
    # Validate role name
    valid, error = validate_role(role)
    if not valid:
        return {"success": False, "error": error}
    
    # Load current state
    state = load_state(work_item_id, work_items_dir)
    current_role = state.current_role
    
    # Same role - no-op success
    if current_role == role:
        role_instructions = load_role_instructions(role, project_root)
        return {
            "success": True,
            "message": f"Already at '{role}'",
            "current_role": role,
            "current_phase": state.current_phase,
            "role_instructions": role_instructions,
        }
    
    # Validate transition is allowed
    valid, error = validate_transition(current_role, role)
    if not valid:
        return {"success": False, "error": error}
    
    # Check DoR gate if transitioning to developer
    if role == DOR_GATE_ROLE:
        dor_complete, missing = check_dor_gate(state.dor)
        if not dor_complete:
            if force:
                # Check for consent
                if not has_valid_consent(state, "skip_dor"):
                    return {
                        "success": False,
                        "error": "Cannot force transition without recorded consent. Call gcp_consent first.",
                        "missing": missing,
                    }
                # Consume the consent
                consume_consent(state, "skip_dor")
            else:
                return {
                    "success": False,
                    "error": "DoR must be complete before Development phase",
                    "missing": missing,
                }
    
    
    # Check if backward transition
    backward = is_backward_transition(current_role, role)
    warning = None
    if backward:
        warning = "Moving backward to rework. Previous progress preserved."
    
    # Update state
    now = datetime.now(timezone.utc)
    
    # Close current role in history
    if state.role_history:
        state.role_history[-1].exited_at = now
    
    # Add new role to history
    state.role_history.append(
        RoleHistoryEntry(
            role=role,
            entered_at=now,
            exited_at=None,
        )
    )
    
    # Update current role and phase
    state.current_role = role
    state.current_phase = get_phase_for_role(role)
    state.updated_at = now
    
    # Save state
    save_state(work_item_id, state, work_items_dir)
    
    # Load role instructions
    role_instructions = load_role_instructions(role, project_root)
    
    result = {
        "success": True,
        "current_role": role,
        "current_phase": state.current_phase,
        "role_instructions": role_instructions,
    }
    
    if warning:
        result["warning"] = warning
    
    return result
