"""gcp_status tool - Get comprehensive workflow status."""

from pathlib import Path

from .. import __version__
from ..core.persistence import load_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..core.checklists import get_missing_items, is_checklist_complete
from ..roles.loader import load_role_instructions
from .gcp_transition import get_role_notes_path


async def gcp_status(
    work_item_id: str,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    project_root: Path | None = None,
) -> dict:
    """
    Get comprehensive workflow status for a work item.
    
    Args:
        work_item_id: Work item identifier
        work_items_dir: Work items directory
        project_root: Project root for local role overrides
    
    Returns:
        Dict with full workflow status
    """
    # Check work item exists
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "active": False,
            "message": f"No active work item '{work_item_id}'. Use gcp_init to start.",
            "version": __version__,
        }
    
    # Load state
    state = load_state(work_item_id, work_items_dir)
    
    # Load role instructions
    role_instructions = load_role_instructions(state.current_role, project_root)
    
    # Build DoR status
    dor_missing = get_missing_items(state.dor)
    dor_complete = is_checklist_complete(state.dor)
    
    # Build DoD status
    dod_missing = get_missing_items(state.dod)
    dod_complete = is_checklist_complete(state.dod)
    
    # Generate next steps
    next_steps = _generate_next_steps(state, dor_complete, dod_complete, dor_missing)
    
    # Build deviations list
    deviations = [
        {
            "id": d.id,
            "action": d.action,
            "reason": d.reason,
            "timestamp": d.timestamp.isoformat(),
            "consumed": d.consumed,
        }
        for d in state.deviations
    ]
    
    # Check for missing role notes (completed roles only)
    missing_notes = []
    seen_roles = set()
    for entry in state.role_history:
        if entry.exited_at is not None:  # Role has been exited (completed)
            if entry.role not in seen_roles:
                notes_path = get_role_notes_path(work_item_id, entry.role, work_items_dir)
                if not notes_path.exists():
                    missing_notes.append(entry.role)
                seen_roles.add(entry.role)
    
    return {
        "active": True,
        "version": __version__,
        "work_item_id": state.work_item_id,
        "profile": state.profile,
        "current_phase": state.current_phase,
        "current_role": state.current_role,
        "dor": {
            "complete": dor_complete,
            "items": dict(state.dor),
            "missing": dor_missing,
        },
        "dod": {
            "complete": dod_complete,
            "items": dict(state.dod),
            "missing": dod_missing,
        },
        "deviations": deviations,
        "missing_notes": missing_notes,
        "role_instructions": role_instructions,
        "next_steps": next_steps,
    }


def _generate_next_steps(state, dor_complete: bool, dod_complete: bool, dor_missing: list[str]) -> list[str]:
    """Generate intelligent next steps based on current state."""
    steps = []
    
    if state.current_phase == "definition":
        if not dor_complete:
            for item in dor_missing:
                steps.append(f"Complete {item}")
            steps.append("Then transition to next role")
        else:
            steps.append("DoR complete - ready to transition to developer")
    
    elif state.current_phase == "development":
        if state.current_role == "developer":
            steps.append("Implement feature following TDD")
            steps.append("Mark testsWrittenFirst when tests are written")
        elif state.current_role == "refactor-expert":
            steps.append("Review code for refactoring opportunities")
            steps.append("Mark refactorComplete when done")
        elif state.current_role == "builder":
            steps.append("Build and verify")
            steps.append("Mark buildPasses when build succeeds")
    
    elif state.current_phase == "completion":
        if not dod_complete:
            steps.append("Complete remaining DoD items")
        else:
            steps.append("DoD complete - work item finished!")
    
    return steps if steps else ["Continue with current role responsibilities"]
