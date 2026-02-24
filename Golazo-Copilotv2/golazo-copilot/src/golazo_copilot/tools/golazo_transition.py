"""golazo_transition tool - Transition between workflow roles."""

from datetime import datetime, timezone
from pathlib import Path

from ..core.types import RoleHistoryEntry
from ..core.persistence import load_state, save_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..core.transitions import (
    validate_role,
    validate_transition,
    is_backward_transition,
    get_phase_for_role,
)
from ..core.output_validator import parse_required_outputs, validate_all_outputs
from ..roles.loader import load_role_instructions, get_role_content
from .golazo_consent import has_valid_consent, consume_consent


# Role suffix mapping for notes files
ROLE_SUFFIX_MAP = {
    "project-owner-assistant": "project-owner-assistant",
    "program-manager": "program-manager",
    "quality-assurance": "quality-assurance",
    "architect": "architect",
    "developer": "developer",
    "refactor-expert": "refactor",  # Shortened
    "builder": "builder",
    "documenter": "documenter",
    "retrospective": "retrospective",
}


def get_role_notes_path(work_item_id: str, role: str, work_items_dir: Path) -> Path:
    """Get the expected path for a role's decision notes file."""
    suffix = ROLE_SUFFIX_MAP.get(role, role)
    return work_items_dir / work_item_id / "RoleDecisionNotes" / f"{work_item_id}-{suffix}.md"


def check_role_notes_exist(work_item_id: str, role: str, work_items_dir: Path) -> bool:
    """Check if role decision notes file exists."""
    notes_path = get_role_notes_path(work_item_id, role, work_items_dir)
    return notes_path.exists()


async def golazo_transition(
    work_item_id: str,
    role: str,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    project_root: Path | None = None,
    force: bool = False,
    force_without_notes: bool = False,
) -> dict:
    """
    Transition to a new role in the workflow.
    
    Args:
        work_item_id: Work item identifier
        role: Target role to transition to
        work_items_dir: Directory for work items
        project_root: Project root for local role overrides
        force: Force transition even if output gates not met (requires prior consent)
        force_without_notes: Force transition even if role notes missing (requires prior consent)
    
    Returns:
        Dict with success status, current role/phase, and role instructions
    """
    # Check work item exists
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error": f"Work item '{work_item_id}' does not exist. Use golazo_create_workitem first.",
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
    
    # Check if backward transition
    backward = is_backward_transition(current_role, role)
    warning = None
    if backward:
        warning = "Moving backward to rework. Previous progress preserved."
    
    # Check if outgoing role has decision notes (BLOCK if missing - GCP-0020)
    if not check_role_notes_exist(work_item_id, current_role, work_items_dir):
        notes_path = get_role_notes_path(work_item_id, current_role, work_items_dir)
        if force_without_notes:
            # Check for consent
            if not has_valid_consent(state, "skip_role"):
                return {
                    "success": False,
                    "error": "Cannot force transition without recorded consent. Call golazo_consent with action='skip_role' first.",
                    "missing_file": str(notes_path),
                }
            # Consume the consent
            consume_consent(state, "skip_role")
            # Save state after consuming consent
            save_state(work_item_id, state, work_items_dir)
        else:
            # Show relative path from workspace root for clarity
            relative_path = f"WorkItems/{work_item_id}/RoleDecisionNotes/{work_item_id}-{ROLE_SUFFIX_MAP.get(current_role, current_role)}.md"
            return {
                "success": False,
                "error": f"Cannot transition from '{current_role}': Missing role notes file at '{relative_path}'. Create this file to document your work in the '{current_role}' role before transitioning.",
                "missing_file": relative_path,
                "hint": f"Create the file first, or use force_without_notes=True with prior golazo_consent(action='skip_role')",
            }
    
    # GCP-0025: Check required outputs for current role
    # Use project_root if provided, otherwise fall back to work_items_dir.parent
    workspace_root = project_root if project_root else work_items_dir.parent
    role_content = get_role_content(current_role, workspace_root)
    output_specs = parse_required_outputs(role_content, work_item_id)
    
    # GCP-0053: Filter closure-only outputs based on state
    # Backward transitions skip closure-only gates (user is reworking before completing closure)
    closure_mode = getattr(state, 'closure_pending', False) and not backward
    output_specs = [s for s in output_specs if not s.closure_only or closure_mode]
    
    if output_specs:
        validation_result = validate_all_outputs(output_specs, workspace_root)
        if not validation_result.valid:
            missing_outputs = [o["spec"].path_or_pattern for o in validation_result.outputs if not o["valid"]]
            if force:
                # Check for consent to skip outputs
                if not has_valid_consent(state, "skip_outputs"):
                    return {
                        "success": False,
                        "error": "Cannot force transition without recorded consent. Call golazo_consent(action='skip_outputs') first.",
                        "missing_outputs": missing_outputs,
                    }
                # Consume the consent
                consume_consent(state, "skip_outputs")
                save_state(work_item_id, state, work_items_dir)
            else:
                return {
                    "success": False,
                    "error": f"Cannot transition from '{current_role}': {validation_result.message}",
                    "missing_outputs": missing_outputs,
                    "hint": "Create the missing outputs, or use force=True with prior golazo_consent(action='skip_outputs')",
                }
    
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
    
    # GCP-0053: Set closure_pending when retro→POA in complete profile
    if (
        state.profile == "complete"
        and current_role == "retrospective"
        and role == "project-owner-assistant"
    ):
        state.closure_pending = True
        state.current_phase = "closure"
        # Override backward-transition warning — this is closure, not rework
        warning = "Entering CLOSURE MODE. Perform acceptance validation and create closure.md."
    
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
    
    if getattr(state, 'closure_pending', False):
        result["closure_pending"] = True
    
    if warning:
        result["warning"] = warning
    
    return result
