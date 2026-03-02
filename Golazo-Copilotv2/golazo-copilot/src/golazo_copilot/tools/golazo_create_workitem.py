"""golazo_create_workitem tool - Create a new work item."""

from importlib import resources
from pathlib import Path
from typing import Literal

from ..core.types import GcpInitResult
from ..core.state import create_initial_state, validate_work_item_id, validate_profile
from ..core.persistence import save_state, work_item_exists, DEFAULT_WORKITEMS_DIR
from ..roles.loader import load_role_instructions


Profile = Literal["complete", "express", "spike"]
DEFAULT_PROFILE: Profile = "complete"


def _ensure_capabilities_registry(workspace_root: Path) -> None:
    """Create capabilities.yaml in workspace root if it does not exist."""
    capabilities_path = workspace_root / "capabilities.yaml"
    if capabilities_path.exists():
        return

    try:
        files_pkg = resources.files("golazo_copilot")
        template = files_pkg.joinpath("capabilities-template.yaml")
        content = template.read_text(encoding="utf-8")
    except (FileNotFoundError, TypeError):
        content = "capabilities: []\n"

    capabilities_path.write_text(content, encoding="utf-8")


async def golazo_create_workitem(
    work_item_id: str,
    profile: str = DEFAULT_PROFILE,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
    project_root: Path | None = None,
) -> dict:
    """
    Create a new work item with persistent state.
    
    Args:
        work_item_id: Unique identifier for the work item
        profile: Workflow profile ("complete", "express", "spike")
        work_items_dir: Directory for work items (default: WorkItems)
        project_root: Project root for local role overrides
    
    Returns:
        Dict with success status, current role, and role instructions
    """
    # Validate work_item_id
    valid, error = validate_work_item_id(work_item_id)
    if not valid:
        return {"success": False, "error": error}
    
    # Validate profile
    valid, error = validate_profile(profile)
    if not valid:
        return {"success": False, "error": error}
    
    # Check if work item already exists
    if work_item_exists(work_item_id, work_items_dir):
        return {
            "success": False,
            "error": f"Work item '{work_item_id}' already exists. Use golazo_switch to resume.",
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
    state = create_initial_state(work_item_id, profile)  # type: ignore
    
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
