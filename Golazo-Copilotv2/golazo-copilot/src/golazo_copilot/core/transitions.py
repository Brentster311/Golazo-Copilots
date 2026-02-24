"""Transition validation logic for Golazo Copilot workflow."""

from typing import Literal

# Valid transitions from each role
TRANSITIONS: dict[str, list[str]] = {
    "project-owner-assistant": ["program-manager"],
    "program-manager": ["domain-expert", "project-owner-assistant"],
    "domain-expert": ["quality-assurance", "program-manager"],
    "quality-assurance": ["architect", "domain-expert"],
    "architect": ["developer", "quality-assurance"],
    "developer": ["refactor-expert", "architect"],
    "refactor-expert": ["documenter", "developer"],
    "documenter": ["builder", "refactor-expert"],
    "builder": ["retrospective", "documenter"],
    "retrospective": ["project-owner-assistant", "builder"],
}

# Phase for each role
PHASE_MAP: dict[str, Literal["definition", "development", "completion", "closure"]] = {
    "project-owner-assistant": "definition",
    "program-manager": "definition",
    "domain-expert": "definition",
    "quality-assurance": "definition",
    "architect": "definition",
    "developer": "development",
    "refactor-expert": "development",
    "documenter": "completion",
    "builder": "completion",
    "retrospective": "completion",
}

# All valid roles
VALID_ROLES = set(TRANSITIONS.keys())

# Role order for determining forward/backward
ROLE_ORDER = [
    "project-owner-assistant",
    "program-manager",
    "domain-expert",
    "quality-assurance",
    "architect",
    "developer",
    "refactor-expert",
    "documenter",
    "builder",
    "retrospective",
]


def validate_role(role: str) -> tuple[bool, str | None]:
    """
    Validate that role is a known role name.
    
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not role:
        return False, "Invalid role. Role name cannot be empty."
    
    if role not in VALID_ROLES:
        return False, f"Invalid role '{role}'. Must be one of: {', '.join(sorted(VALID_ROLES))}"
    
    return True, None


def validate_transition(current_role: str, target_role: str) -> tuple[bool, str | None]:
    """
    Validate that transition from current_role to target_role is allowed.
    
    Rules:
    - Same role is always allowed (no-op)
    - Backward transitions are always allowed (any earlier role in sequence)
    - Forward transitions must be to an explicitly allowed next role (no skipping)
    
    Returns:
        Tuple of (is_valid, error_message).
    """
    # Same role is allowed (no-op)
    if current_role == target_role:
        return True, None
    
    # Check if this is a backward transition
    if is_backward_transition(current_role, target_role):
        # All backward transitions are allowed
        return True, None
    
    # Forward transition - must be in allowed list (no skipping)
    allowed = TRANSITIONS.get(current_role, [])
    if target_role in allowed:
        return True, None
    
    return False, f"Cannot transition from '{current_role}' to '{target_role}'. Allowed: {', '.join(allowed)}"


def is_backward_transition(current_role: str, target_role: str) -> bool:
    """Check if transition is moving backward in workflow."""
    if current_role == target_role:
        return False
    
    current_idx = ROLE_ORDER.index(current_role) if current_role in ROLE_ORDER else 0
    target_idx = ROLE_ORDER.index(target_role) if target_role in ROLE_ORDER else 0
    
    return target_idx < current_idx


def get_phase_for_role(role: str) -> Literal["definition", "development", "completion", "closure"]:
    """Get the phase for a given role."""
    return PHASE_MAP.get(role, "definition")
