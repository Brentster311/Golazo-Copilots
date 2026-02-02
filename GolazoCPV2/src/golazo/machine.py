"""
GCP2-001a: Core State Machine

Provides workflow state transitions and DoR/DoD enforcement for Golazo V2.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .state import State, create_state, load_state, save_state
from .config import GolazoConfig


# Legacy constants for backward compatibility (used if no config)
VALID_ROLES = [
    "project-owner",
    "program-manager", 
    "tester",
    "architect",
    "developer",
    "refactor-expert",
    "builder",
    "documentor",
]

ROLE_TO_PHASE = {
    "project-owner": "design",
    "program-manager": "design",
    "tester": "design",
    "architect": "design",
    "developer": "development",
    "refactor-expert": "development",
    "builder": "release",
    "documentor": "release",
}

TRANSITIONS = {
    "project-owner": ["program-manager"],
    "program-manager": ["tester"],
    "tester": ["architect"],
    "architect": ["developer"],
    "developer": ["refactor-expert"],
    "refactor-expert": ["builder"],
    "builder": ["documentor"],
    "documentor": [],
}

DOR_ITEMS = ["userStory", "designDoc", "reviewComments", "testCases"]

DOD_ITEMS = [
    "branchCreated", "testsWrittenFirst", "testsPass",
    "buildPasses", "docsUpdated", "refactorComplete", "committed"
]


class GolazoStateMachine:
    """
    State machine for Golazo V2 workflow management.
    
    Manages role transitions, DoR/DoD gates, and state persistence.
    """
    
    def __init__(
        self,
        work_item_id: str,
        profile: str = "complete",
        base_path: Optional[Path] = None,
        config: Optional[GolazoConfig] = None,
    ):
        """
        Initialize state machine for a work item.
        
        Args:
            work_item_id: The work item identifier
            profile: Workflow profile (complete, express, spike)
            base_path: Base path for WorkItems directory
            config: Optional GolazoConfig (loads from file if not provided)
        """
        self._work_item_id = work_item_id
        self._base_path = base_path
        self._config = config or GolazoConfig.load(base_path)
        self._state = create_state(
            work_item_id, 
            profile=profile, 
            base_path=base_path,
            dor_items=list(self._config.dor_items),
            dod_items=list(self._config.dod_items),
            initial_role=self._config.roles[0] if self._config.roles else "project-owner",
        )
    
    def _save(self) -> None:
        """Persist current state."""
        save_state(self._state, base_path=self._base_path)
    
    def _reload(self) -> None:
        """Reload state from disk."""
        loaded = load_state(self._work_item_id, base_path=self._base_path)
        if loaded:
            self._state = loaded
    
    @property
    def current_role(self) -> str:
        """Current active role."""
        return self._state.currentRole
    
    @property
    def current_phase(self) -> str:
        """Current phase (derived from role)."""
        return self._config.role_to_phase.get(self._state.currentRole, "design")
    
    @property
    def profile(self) -> str:
        """Workflow profile."""
        return self._state.profile
    
    def can_transition(self, target_role: str) -> tuple[bool, str]:
        """
        Check if transition to target role is valid.
        
        Args:
            target_role: Role to transition to
            
        Returns:
            (allowed, reason) tuple
        """
        # Validate target role
        if target_role not in self._config.roles:
            return (False, f"Unknown role: {target_role}")
        
        current = self._state.currentRole
        valid_targets = self._config.transitions.get(current, ())
        
        # Check if target is valid next role
        if target_role not in valid_targets:
            return (False, f"Invalid transition: {current} -> {target_role}. Valid: {list(valid_targets)}")
        
        # Check DoR gate at design -> development boundary
        if current == "architect" and target_role == "developer":
            if not self.is_dor_complete():
                return (False, "DoR must be complete before entering Development phase")
        
        return (True, f"Transition allowed: {current} -> {target_role}")
    
    def transition(self, target_role: str, force: bool = False) -> tuple[bool, str]:
        """
        Perform transition to target role if valid.
        
        Args:
            target_role: Role to transition to
            force: If True, skip validation gates (requires consent)
            
        Returns:
            (success, message) tuple
        """
        # Validate role name even when forcing
        if target_role not in self._config.roles:
            return (False, f"Unknown role: {target_role}")
        
        if not force:
            allowed, reason = self.can_transition(target_role)
            if not allowed:
                return (False, reason)
        
        now = datetime.now(timezone.utc).isoformat()
        
        # Update roleHistory - close current entry
        if self._state.roleHistory:
            self._state.roleHistory[-1]["exitedAt"] = now
        
        # Add new entry
        self._state.roleHistory.append({
            "role": target_role,
            "enteredAt": now,
            "exitedAt": None,
        })
        
        # Update current role and phase
        self._state.currentRole = target_role
        self._state.currentPhase = self._config.role_to_phase.get(target_role, "design")
        
        # Persist
        self._save()
        
        return (True, f"Transitioned to {target_role}")
    
    def check_dor(self) -> dict:
        """Return DoR checklist status."""
        return dict(self._state.dor)
    
    def check_dod(self) -> dict:
        """Return DoD checklist status."""
        return dict(self._state.dod)
    
    def mark_dor(self, item: str, complete: bool = True) -> None:
        """
        Mark DoR item as complete/incomplete.
        
        Args:
            item: DoR item name
            complete: Whether item is complete
            
        Raises:
            ValueError: If item is not a valid DoR item
        """
        if item not in self._config.dor_items:
            raise ValueError(f"Invalid DoR item: {item}. Valid: {list(self._config.dor_items)}")
        
        self._state.dor[item] = complete
        self._save()
    
    def mark_dod(self, item: str, complete: bool = True) -> None:
        """
        Mark DoD item as complete/incomplete.
        
        Args:
            item: DoD item name
            complete: Whether item is complete
            
        Raises:
            ValueError: If item is not a valid DoD item
        """
        if item not in self._config.dod_items:
            raise ValueError(f"Invalid DoD item: {item}. Valid: {list(self._config.dod_items)}")
        
        self._state.dod[item] = complete
        self._save()
    
    def is_dor_complete(self) -> bool:
        """Check if all DoR items are complete."""
        return all(self._state.dor.get(item, False) for item in self._config.dor_items)
    
    def is_dod_complete(self) -> bool:
        """Check if all DoD items are complete."""
        return all(self._state.dod.get(item, False) for item in self._config.dod_items)
