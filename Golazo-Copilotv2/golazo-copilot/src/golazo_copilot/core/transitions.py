"""Transition validation logic for Golazo Copilot workflow."""

from typing import Literal

# Profile type for workflow role sequencing
Profile = Literal["complete", "express", "spike"]

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

# All valid roles
VALID_ROLES = set(ROLE_ORDER)

# Profile-specific role sequences
PROFILE_ROLES: dict[Profile, list[str]] = {
    "complete": ROLE_ORDER,
    "express": [
        "project-owner-assistant",
        "quality-assurance",
        "developer",
        "builder",
        "retrospective",
    ],
    "spike": [
        "project-owner-assistant",
        "domain-expert",
        "architect",
        "developer",
        "retrospective",
    ],
}


def get_role_order_for_profile(profile: str = "complete") -> list[str]:
    """Return role order for a profile; fallback to complete for unknown profiles."""
    return PROFILE_ROLES.get(profile, ROLE_ORDER)


def _build_transitions_for_profile(profile: str = "complete") -> dict[str, list[str]]:
    """Build forward-only transition map from profile role order.

    Forward transitions permit only the immediate next role in the profile sequence.
    Backward transitions are handled separately in `validate_transition`.
    """
    roles = get_role_order_for_profile(profile)
    transitions: dict[str, list[str]] = {role: [] for role in VALID_ROLES}

    for idx, role in enumerate(roles[:-1]):
        transitions[role] = [roles[idx + 1]]

    # Complete profile supports closure re-entry from retrospective.
    if profile == "complete":
        transitions["retrospective"] = ["project-owner-assistant"]

    return transitions


# Legacy default transition map kept for compatibility with existing callers.
TRANSITIONS: dict[str, list[str]] = _build_transitions_for_profile("complete")


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


def validate_transition(
    current_role: str,
    target_role: str,
    profile: str = "complete",
) -> tuple[bool, str | None]:
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
    if current_role not in VALID_ROLES or target_role not in VALID_ROLES:
        return False, "Invalid role for transition"

    profile_roles = get_role_order_for_profile(profile)
    if current_role not in profile_roles:
        return False, f"Role '{current_role}' is not part of the '{profile}' profile"
    if target_role not in profile_roles:
        return False, f"Role '{target_role}' is not part of the '{profile}' profile"

    if is_backward_transition(current_role, target_role, profile=profile):
        # All backward transitions are allowed
        return True, None
    
    # Forward transition - must be in allowed list (no skipping)
    allowed = _build_transitions_for_profile(profile).get(current_role, [])
    if target_role in allowed:
        return True, None
    
    return False, f"Cannot transition from '{current_role}' to '{target_role}'. Allowed: {', '.join(allowed)}"


def is_backward_transition(
    current_role: str,
    target_role: str,
    profile: str = "complete",
) -> bool:
    """Check if transition is moving backward in workflow."""
    if current_role == target_role:
        return False

    role_order = get_role_order_for_profile(profile)
    if current_role not in role_order or target_role not in role_order:
        return False

    current_idx = role_order.index(current_role)
    target_idx = role_order.index(target_role)
    
    return target_idx < current_idx


def get_phase_for_role(role: str) -> Literal["definition", "development", "completion", "closure"]:
    """Get the phase for a given role."""
    return PHASE_MAP.get(role, "definition")
