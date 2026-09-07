"""golazo_create_workitem tool - Create a new work item."""

from importlib import resources
from pathlib import Path
from typing import Literal

from ..core.persistence import DEFAULT_WORKITEMS_DIR, save_state, work_item_exists
from ..core.state import create_initial_state, validate_profile, validate_work_item_id
from ..roles.loader import load_role_instructions
from .golazo_capabilities import ensure_registry_path

Profile = Literal["complete", "express", "spike"]
DEFAULT_PROFILE: Profile = "complete"


def _ensure_capabilities_registry(workspace_root: Path) -> None:
    """Create or migrate the canonical capabilities registry."""
    try:
        files_pkg = resources.files("golazo_copilot")
        template = files_pkg.joinpath("capabilities-template.yaml")
        content = template.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError):
        content = "capabilities: []\n"

    ensure_registry_path(workspace_root, content)


async def golazo_create_workitem(
    work_item_id: str,
    profile: str = DEFAULT_PROFILE,
    initial_role: str = "project-owner-assistant",
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    project_root: Path | None = None,
) -> dict:
    """
    Create a new work item with persistent state.
    
    Args:
        work_item_id: Unique identifier for the work item
        profile: Workflow profile ("complete", "express", "spike")
        initial_role: Initial role ("project-owner-assistant" or "planner")
        work_items_dir: Directory for work items (default: WorkItems)
        project_root: Project root for local role overrides
    
    Returns:
        Dict with success status, current role, and role instructions
    """
    # Validate work_item_id
    valid, error = validate_work_item_id(work_item_id)
    if not valid:
        return {"success": False, "error": error}

    valid_initial_roles = {"project-owner-assistant", "planner"}
    if initial_role not in valid_initial_roles:
        return {
            "success": False,
            "error": f"Invalid initial_role '{initial_role}'. Must be one of: {sorted(valid_initial_roles)}",
        }

    if initial_role == "planner":
        if profile != "complete":
            return {
                "success": False,
                "error": "Planner can only be the initial role for the complete profile.",
            }
        existing_states = (
            any(
                child.is_dir() and (child / "state.json").is_file()
                for child in work_items_dir.iterdir()
            )
            if work_items_dir.is_dir()
            else False
        )
        if existing_states:
            return {
                "success": False,
                "error": "Planner can only be the initial role for the first work item in a workspace.",
            }
    
    # Validate profile
    valid, error = validate_profile(profile)
    if not valid:
        return {"success": False, "error": error}
    
    # Check if work item already exists
    if work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error": (
                f"Work item '{work_item_id}' already exists. Resume it by passing its "
                "work_item_id to golazo_status or golazo_role_context."
            ),
        }

    workspace_root = Path(project_root) if project_root is not None else Path(work_items_dir).parent
    try:
        _ensure_capabilities_registry(workspace_root)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create capabilities.yaml: {e}",
        }
    
    # Create initial state
    state = create_initial_state(work_item_id, profile, initial_role)  # type: ignore
    
    # Save state to file
    try:
        save_state(work_item_id, state, work_items_dir)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to create work item: {e}",
        }
    
    # Load role instructions for initial role
    role_instructions = load_role_instructions(state.current_role, project_root)
    
    return {
        "success": True,
        "work_item_id": work_item_id,
        "current_role": state.current_role,
        "role_instructions": role_instructions,
    }


# Alias for backward compatibility
golazo_init = golazo_create_workitem
