"""Helper functions for composing golazo_status results.

GCP-0064: Internal modularization only. Public golazo_status behavior remains unchanged.
"""

from pathlib import Path

from ..core.output_validator import validate_all_outputs
from ..core.transitions import get_role_order_for_profile
from .golazo_transition import get_role_notes_path


def validate_required_outputs(output_specs, workspace_root: Path) -> tuple[bool, list[dict]]:
    """Validate required outputs and return response-shaped output entries."""
    results = []
    all_valid = True
    if output_specs:
        validation_result = validate_all_outputs(output_specs, workspace_root)
        all_valid = validation_result.valid
        for output in validation_result.outputs:
            results.append(
                {
                    "path": output["spec"].path_or_pattern,
                    "type": output["spec"].type,
                    "valid": output["valid"],
                }
            )
    return all_valid, results


def find_missing_role_notes(state, work_item_id: str, work_items_dir: Path) -> list[str]:
    """Return completed roles that are missing notes files."""
    missing = []
    seen = set()
    for entry in state.role_history:
        if entry.exited_at is not None:
            if entry.role not in seen:
                notes_path = get_role_notes_path(work_item_id, entry.role, work_items_dir)
                if not notes_path.exists():
                    missing.append(entry.role)
                seen.add(entry.role)
    return missing


def unwrap_parallel_results(
    output_result,
    missing_notes_result,
    stale_files_result,
    registry_result,
    progress_result,
    state,
) -> dict:
    """Normalize gathered parallel results with error-safe defaults."""
    if isinstance(output_result, BaseException):
        outputs_complete = True
        required_outputs = []
    else:
        outputs_complete, required_outputs = output_result

    missing_notes = [] if isinstance(missing_notes_result, BaseException) else missing_notes_result
    stale_files = [] if isinstance(stale_files_result, BaseException) else stale_files_result
    registry_hint = None if isinstance(registry_result, BaseException) else registry_result
    role_progress = (
        {
            "roles": [],
            "roles_completed": 0,
            "roles_total": len(get_role_order_for_profile(state.profile)),
        }
        if isinstance(progress_result, BaseException)
        else progress_result
    )

    return {
        "outputs_complete": outputs_complete,
        "required_outputs": required_outputs,
        "missing_notes": missing_notes,
        "stale_files": stale_files,
        "registry_hint": registry_hint,
        "role_progress": role_progress,
    }


def apply_closure_completion_override(
    role_progress: dict,
    closure_mode: bool,
    current_role: str,
    outputs_complete: bool,
) -> dict:
    """Apply closure-specific completion adjustment for project-owner-assistant."""
    if not (closure_mode and current_role == "project-owner-assistant" and outputs_complete):
        return role_progress

    updated_progress = dict(role_progress)
    updated_progress["roles_completed"] = updated_progress.get(
        "roles_total", updated_progress.get("roles_completed", 0)
    )

    updated_roles = []
    for role in updated_progress.get("roles", []):
        if role.get("role") == "project-owner-assistant":
            updated_roles.append({"role": role["role"], "status": "completed"})
        else:
            updated_roles.append(role)
    updated_progress["roles"] = updated_roles
    return updated_progress


def build_deviations(deviations) -> list[dict]:
    """Convert deviation objects to response-shaped dictionaries."""
    return [
        {
            "id": d.id,
            "action": d.action,
            "reason": d.reason,
            "timestamp": d.timestamp.isoformat(),
            "consumed": d.consumed,
        }
        for d in deviations
    ]


def build_version_warning(stale_files: list[dict]) -> str | None:
    """Create stale-version warning text from stale file entries."""
    if not stale_files:
        return None

    details = ", ".join(f"{s['file']} (v{s['deployed']} → v{s['source']})" for s in stale_files)
    return (
        f"{len(stale_files)} file(s) are stale: {details}. "
        f"Run golazo_bootstrap to update."
    )
