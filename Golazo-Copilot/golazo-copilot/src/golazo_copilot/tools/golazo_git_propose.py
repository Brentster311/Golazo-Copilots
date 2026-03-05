"""golazo_git_propose tool - Proposal-only git intent capture for auditability."""

from datetime import datetime, timezone
from pathlib import Path

from ..core.persistence import DEFAULT_WORKITEMS_DIR, load_state, save_state, work_item_exists

VALID_ACTIONS = {"add", "commit", "push", "branch"}


def _utc_iso8601_z() -> str:
    """Return current UTC timestamp in normalized ISO-8601 format with trailing Z."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _parameter_required(action: str, parameter: str) -> dict:
    """Deterministic parameter-required error payload."""
    return {
        "success": False,
        "error_code": "parameter_required",
        "action": action,
        "parameter": parameter,
        "error": f"Parameter required for action '{action}': {parameter}.",
    }


async def golazo_git_propose(
    work_item_id: str,
    action: str,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    files: list[str] | None = None,
    message: str | None = None,
    branch: str | None = None,
) -> dict:
    """Record a proposal-only git action intent in work-item state (append-only)."""
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error_code": "workitem_not_found",
            "error": f"Work item '{work_item_id}' does not exist. Use golazo_create_workitem first.",
        }

    if action not in VALID_ACTIONS:
        return {
            "success": False,
            "error_code": "invalid_action",
            "error": f"Invalid action '{action}'. Must be one of: add, branch, commit, push.",
        }

    if action == "add" and (not files or len(files) == 0):
        return _parameter_required(action, "files")
    if action == "commit" and (not message or not message.strip()):
        return _parameter_required(action, "message")
    if action in {"push", "branch"} and (not branch or not branch.strip()):
        return _parameter_required(action, "branch")

    state = load_state(work_item_id, work_items_dir)

    if not isinstance(state.git_actions, list):
        state.git_actions = []

    proposal = {
        "action": action,
        "status": "proposed",
        "timestamp": _utc_iso8601_z(),
    }

    if action == "add":
        proposal["files"] = list(files or [])
    elif action == "commit":
        proposal["message"] = message.strip() if message else ""
    elif action in {"push", "branch"}:
        proposal["branch"] = branch.strip() if branch else ""

    state.git_actions.append(proposal)
    state.updated_at = datetime.now(timezone.utc)

    try:
        save_state(work_item_id, state, work_items_dir)
    except Exception as e:
        return {
            "success": False,
            "error_code": "persistence_failure",
            "error": f"Failed to persist proposal for work item '{work_item_id}': {e}",
        }

    return {
        "success": True,
        "work_item_id": work_item_id,
        "proposal": proposal,
        "proposal_count": len(state.git_actions),
    }
