"""
GCP2-003: Structured State Management

Provides JSON-based state persistence for Golazo V2 workflow tracking.
"""

import json
import logging
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Schema version for future migrations
SCHEMA_VERSION = "1.0"

# Valid work item ID pattern (alphanumeric, dash, underscore)
VALID_ID_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,99}$')

logger = logging.getLogger(__name__)


@dataclass
class State:
    """Golazo workflow state for a work item."""
    
    schemaVersion: str
    workItemId: str
    profile: str
    currentPhase: str
    currentRole: str
    createdAt: str
    updatedAt: str
    dor: dict = field(default_factory=dict)
    dod: dict = field(default_factory=dict)
    roleHistory: list = field(default_factory=list)
    deviations: list = field(default_factory=list)


def _validate_work_item_id(work_item_id: str) -> None:
    """Validate work item ID for path safety."""
    if not work_item_id:
        raise ValueError("Invalid work item ID: cannot be empty")
    
    if not VALID_ID_PATTERN.match(work_item_id):
        raise ValueError(
            f"Invalid work item ID: '{work_item_id}'. "
            "Must be alphanumeric with dashes/underscores, max 100 chars."
        )
    
    # Extra safety: reject any path traversal attempts
    if '..' in work_item_id or '/' in work_item_id or '\\' in work_item_id:
        raise ValueError(f"Invalid work item ID: '{work_item_id}' contains path characters")


def _get_state_path(work_item_id: str, base_path: Optional[Path] = None) -> Path:
    """Get the path to state.json for a work item."""
    _validate_work_item_id(work_item_id)
    
    if base_path is None:
        base_path = Path.cwd()
    
    return base_path / "WorkItems" / work_item_id / "state.json"


def _default_dor() -> dict:
    """Return default DoR status."""
    return {
        "userStory": False,
        "designDoc": False,
        "reviewComments": False,
        "testCases": False,
    }


def _default_dod() -> dict:
    """Return default DoD status."""
    return {
        "branchCreated": False,
        "testsWrittenFirst": False,
        "testsPass": False,
        "buildPasses": False,
        "docsUpdated": False,
        "refactorComplete": False,
        "committed": False,
    }


def create_state(
    work_item_id: str,
    profile: str = "complete",
    base_path: Optional[Path] = None,
) -> State:
    """
    Create a new state for a work item, or return existing state if present.
    
    Args:
        work_item_id: The work item identifier
        profile: Workflow profile (complete, express, spike)
        base_path: Base path for WorkItems directory
    
    Returns:
        State object (existing or newly created)
    """
    _validate_work_item_id(work_item_id)
    
    # Check if state already exists
    existing = load_state(work_item_id, base_path=base_path)
    if existing is not None:
        return existing
    
    now = datetime.now(timezone.utc).isoformat()
    
    state = State(
        schemaVersion=SCHEMA_VERSION,
        workItemId=work_item_id,
        profile=profile,
        currentPhase="design",
        currentRole="project-owner",
        createdAt=now,
        updatedAt=now,
        dor=_default_dor(),
        dod=_default_dod(),
        roleHistory=[{
            "role": "project-owner",
            "enteredAt": now,
            "exitedAt": None,
        }],
        deviations=[],
    )
    
    save_state(state, base_path=base_path)
    return state


def load_state(
    work_item_id: str,
    base_path: Optional[Path] = None,
) -> Optional[State]:
    """
    Load state for a work item.
    
    If file is corrupted, backs up the corrupted file and creates fresh state.
    
    Args:
        work_item_id: The work item identifier
        base_path: Base path for WorkItems directory
    
    Returns:
        State object if found, None if not found
    """
    _validate_work_item_id(work_item_id)
    
    state_path = _get_state_path(work_item_id, base_path)
    
    if not state_path.exists():
        return None
    
    try:
        content = state_path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        # Check schema version
        file_version = data.get("schemaVersion", "unknown")
        if file_version != SCHEMA_VERSION:
            logger.warning(
                f"State file has schema version {file_version}, "
                f"expected {SCHEMA_VERSION}"
            )
        
        # Apply defaults for missing fields
        return State(
            schemaVersion=data.get("schemaVersion", SCHEMA_VERSION),
            workItemId=data.get("workItemId", work_item_id),
            profile=data.get("profile", "complete"),
            currentPhase=data.get("currentPhase", "design"),
            currentRole=data.get("currentRole", "project-owner"),
            createdAt=data.get("createdAt", datetime.now(timezone.utc).isoformat()),
            updatedAt=data.get("updatedAt", datetime.now(timezone.utc).isoformat()),
            dor=data.get("dor", _default_dor()),
            dod=data.get("dod", _default_dod()),
            roleHistory=data.get("roleHistory", []),
            deviations=data.get("deviations", []),
        )
        
    except json.JSONDecodeError as e:
        # Corrupted JSON - backup and create fresh
        logger.warning(
            f"state.json was corrupted: {e}. "
            f"Backed up to state.json.corrupted and creating fresh state."
        )
        
        backup_path = state_path.with_suffix(".json.corrupted")
        state_path.replace(backup_path)
        
        # Create fresh state
        return create_state(work_item_id, base_path=base_path)


def save_state(state: State, base_path: Optional[Path] = None) -> None:
    """
    Save state to file using atomic write pattern.
    
    Args:
        state: State object to save
        base_path: Base path for WorkItems directory
    
    Raises:
        ValueError: If state has invalid workItemId
    """
    if not state.workItemId:
        raise ValueError("Cannot save state with empty workItemId")
    
    _validate_work_item_id(state.workItemId)
    
    state_path = _get_state_path(state.workItemId, base_path)
    
    # Ensure directory exists
    state_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Update timestamp
    state.updatedAt = datetime.now(timezone.utc).isoformat()
    
    # Convert to dict for JSON serialization
    data = asdict(state)
    
    # Atomic write: write to temp file, then rename
    temp_path = state_path.with_suffix(".json.tmp")
    temp_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    temp_path.replace(state_path)
    
    logger.debug(f"Saved state for {state.workItemId}")


def state_exists(work_item_id: str, base_path: Optional[Path] = None) -> bool:
    """
    Check if state file exists for a work item.
    
    Args:
        work_item_id: The work item identifier
        base_path: Base path for WorkItems directory
    
    Returns:
        True if state file exists, False otherwise
    """
    try:
        _validate_work_item_id(work_item_id)
        state_path = _get_state_path(work_item_id, base_path)
        return state_path.exists()
    except ValueError:
        return False
