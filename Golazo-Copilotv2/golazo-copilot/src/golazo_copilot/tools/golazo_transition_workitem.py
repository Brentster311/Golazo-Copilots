"""golazo_transition_workitem tool - project-level completion and next-item sequencing."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..core.persistence import DEFAULT_WORKITEMS_DIR, load_state, work_item_exists


WORK_ITEM_ID_PATTERN = re.compile(r"^([A-Za-z]{1,4})-(\d{3,})$")


def _utc_iso8601_z() -> str:
    """Return current UTC timestamp in normalized ISO-8601 format with trailing Z."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _compute_next_work_item_id(work_item_id: str) -> str | None:
    """Compute the next sequential work item id while preserving numeric width."""
    match = WORK_ITEM_ID_PATTERN.fullmatch(work_item_id)
    if not match:
        return None
    prefix, number_text = match.groups()
    next_number = int(number_text) + 1
    return f"{prefix}-{next_number:0{len(number_text)}d}"


def _global_state_path(work_items_dir: Path) -> Path:
    """Return workspace-level global state path."""
    return work_items_dir.parent / "global_state.json"


def _load_global_state(path: Path) -> tuple[dict[str, Any], bool]:
    """Load existing global_state.json or initialize a new schema payload."""
    if not path.exists():
        now = _utc_iso8601_z()
        return {
            "schema_version": "1.0",
            "created_at": now,
            "updated_at": now,
            "completed_work_items": [],
            "next_work_item": None,
        }, True

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("global_state.json must contain a JSON object")
    return payload, False


def _save_global_state(path: Path, payload: dict[str, Any]) -> None:
    """Persist global state with atomic write semantics."""
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2)

    fd, temp_path = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file_handle:
            file_handle.write(serialized)
        try:
            os.replace(temp_path, path)
        except PermissionError:
            if path.exists():
                os.unlink(path)
            os.rename(temp_path, path)
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


async def golazo_transition_workitem(
    work_item_id: str,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
) -> dict:
    """Mark a retrospective-complete work item as completed and set next work item id."""
    if not work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error_code": "workitem_not_found",
            "error": f"Work item '{work_item_id}' does not exist. Use golazo_create_workitem first.",
        }

    state = load_state(work_item_id, work_items_dir)
    if state.current_role != "retrospective":
        return {
            "success": False,
            "error_code": "role_precondition_failed",
            "error": (
                f"Work item '{work_item_id}' must be in role 'retrospective' to transition at project level. "
                f"Current role is '{state.current_role}'."
            ),
            "current_role": state.current_role,
        }

    next_work_item_id = _compute_next_work_item_id(work_item_id)
    if not next_work_item_id:
        return {
            "success": False,
            "error_code": "invalid_work_item_id_format",
            "error": (
                f"Cannot compute next work item for '{work_item_id}'. "
                "Expected format '<prefix>-<number>' (e.g., GCP-0001)."
            ),
        }

    global_state_file = _global_state_path(work_items_dir)
    try:
        global_state, created = _load_global_state(global_state_file)
    except Exception as error:
        return {
            "success": False,
            "error_code": "global_state_load_failure",
            "error": f"Failed to load global state from '{global_state_file}': {error}",
        }

    completed_items = global_state.get("completed_work_items")
    if not isinstance(completed_items, list):
        completed_items = []
    if work_item_id not in completed_items:
        completed_items.append(work_item_id)
    global_state["completed_work_items"] = completed_items

    global_state.setdefault("schema_version", "1.0")
    global_state.setdefault("created_at", _utc_iso8601_z())
    global_state["next_work_item"] = next_work_item_id
    global_state["updated_at"] = _utc_iso8601_z()

    try:
        _save_global_state(global_state_file, global_state)
    except Exception as error:
        return {
            "success": False,
            "error_code": "global_state_save_failure",
            "error": f"Failed to save global state to '{global_state_file}': {error}",
        }

    next_exists = work_item_exists(next_work_item_id, work_items_dir)
    message = (
        f"Work item '{work_item_id}' marked completed. Next work item: '{next_work_item_id}'."
        if next_exists
        else (
            f"Work item '{work_item_id}' marked completed. Next work item '{next_work_item_id}' does not exist yet. "
            f"Create it with golazo_create_workitem(work_item_id='{next_work_item_id}')."
        )
    )

    return {
        "success": True,
        "work_item_id": work_item_id,
        "completed_work_item": work_item_id,
        "next_work_item": next_work_item_id,
        "next_work_item_exists": next_exists,
        "global_state_created": created,
        "global_state_path": str(global_state_file),
        "message": message,
    }