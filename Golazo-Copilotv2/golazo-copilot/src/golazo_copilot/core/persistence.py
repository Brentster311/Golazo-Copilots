"""State persistence - JSON file read/write with atomic saves."""

import json
import os
import tempfile
from pathlib import Path

from .types import WorkItemState


DEFAULT_WORKITEMS_DIR = Path("WorkItems")


def get_state_path(work_item_id: str, work_items_dir: Path = DEFAULT_WORKITEMS_DIR) -> Path:
    """Get the path to a work item's state file."""
    return work_items_dir / work_item_id / "state.json"


def work_item_exists(work_item_id: str, work_items_dir: Path = DEFAULT_WORKITEMS_DIR) -> bool:
    """Check if a work item exists."""
    return get_state_path(work_item_id, work_items_dir).exists()


def save_state(
    work_item_id: str,
    state: WorkItemState,
    work_items_dir: Path = DEFAULT_WORKITEMS_DIR,
) -> None:
    """
    Save state to file with atomic write (write to temp, then rename).
    
    This prevents corruption if the write is interrupted.
    """
    work_item_path = work_items_dir / work_item_id
    state_path = get_state_path(work_item_id, work_items_dir)
    
    # Ensure directory exists
    work_item_path.mkdir(parents=True, exist_ok=True)
    
    # Serialize state to JSON
    state_json = state.model_dump_json(indent=2)
    
    # Write to temp file first (atomic write pattern)
    fd, temp_path = tempfile.mkstemp(dir=work_item_path, suffix=".tmp")
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(state_json)
        # Rename temp to final (atomic on same filesystem)
        # On Windows, we may need to delete existing file first
        try:
            os.replace(temp_path, state_path)
        except PermissionError:
            # Windows workaround: delete target then rename
            if state_path.exists():
                os.unlink(state_path)
            os.rename(temp_path, state_path)
    except Exception:
        # Clean up temp file if rename failed
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


def load_state(work_item_id: str, work_items_dir: Path = DEFAULT_WORKITEMS_DIR) -> WorkItemState:
    """Load state from file."""
    state_path = get_state_path(work_item_id, work_items_dir)
    content = state_path.read_text(encoding='utf-8')
    return WorkItemState.model_validate_json(content)
