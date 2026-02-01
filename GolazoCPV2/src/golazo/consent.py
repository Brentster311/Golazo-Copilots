"""
GCP2-001b: Consent Enforcement

Provides consent-based skip detection and deviation logging for Golazo V2.
"""

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .machine import GolazoStateMachine
from .state import save_state


# Quality gate roles that require extra warning
QUALITY_GATE_ROLES = ["tester", "architect"]

# Explicit skip patterns - user clearly wants to skip
EXPLICIT_SKIP_PATTERNS = [
    (r"skip\s+(?:the\s+)?(\w+)\s+role", "role"),  # "skip the tester role"
    (r"skip\s+to\s+(\w+)", "target"),              # "skip to developer"
    (r"don'?t\s+need\s+(?:a\s+)?(?:design\s+doc|test|review)", "artifact"),
    (r"fast[- ]?track", "fasttrack"),              # "fast-track", "fast track"
    (r"use\s+express\s+(?:mode|profile)", "profile"),
]

# Ambiguous patterns - might mean skip, need clarification
AMBIGUOUS_PATTERNS = [
    r"just\s+fix",
    r"quick\s+fix",
    r"this\s+is\s+simple",
    r"don'?t\s+need\s+all\s+that",
]


@dataclass
class RequestAnalysis:
    """Result of analyzing a user request for skip intent."""
    type: str  # 'normal', 'explicit_skip', 'ambiguous'
    detected_skips: list  # Roles/targets detected for skipping
    matched_pattern: Optional[str] = None  # The pattern that matched


class ConsentEnforcer:
    """
    Consent-based enforcement for Golazo V2 workflow.
    
    Analyzes user messages for skip intent, handles clarification,
    and logs all deviations to the state file.
    """
    
    def __init__(self, machine: GolazoStateMachine):
        """
        Initialize consent enforcer with state machine reference.
        
        Args:
            machine: GolazoStateMachine instance
        """
        self._machine = machine
    
    def analyze_request(self, user_message: str) -> RequestAnalysis:
        """
        Analyze user message for skip intent.
        
        Args:
            user_message: Raw user input
            
        Returns:
            RequestAnalysis with type and detected skips
        """
        if not user_message:
            return RequestAnalysis(type="normal", detected_skips=[])
        
        msg_lower = user_message.lower()
        
        # Check explicit patterns first (take precedence)
        for pattern, pattern_type in EXPLICIT_SKIP_PATTERNS:
            match = re.search(pattern, msg_lower)
            if match:
                detected = []
                if match.groups():
                    detected = [g for g in match.groups() if g]
                return RequestAnalysis(
                    type="explicit_skip",
                    detected_skips=detected,
                    matched_pattern=pattern_type
                )
        
        # Check ambiguous patterns
        for pattern in AMBIGUOUS_PATTERNS:
            if re.search(pattern, msg_lower):
                return RequestAnalysis(
                    type="ambiguous",
                    detected_skips=[],
                    matched_pattern=pattern
                )
        
        # Normal request
        return RequestAnalysis(type="normal", detected_skips=[])
    
    def get_clarification_prompt(self, analysis: RequestAnalysis) -> Optional[str]:
        """
        Generate clarification prompt for ambiguous requests.
        
        Args:
            analysis: RequestAnalysis from analyze_request()
            
        Returns:
            Clarification prompt string, or None/empty if not needed
        """
        if analysis.type == "ambiguous":
            return (
                "It sounds like you want to skip some workflow steps. "
                "To proceed, please explicitly confirm which roles to skip, "
                "or say 'continue normally' to follow the full workflow."
            )
        
        # No clarification needed for normal or explicit
        return None
    
    def get_quality_gate_warning(self, role: str) -> Optional[str]:
        """
        Generate warning for skipping quality gate roles.
        
        Args:
            role: Role being skipped
            
        Returns:
            Warning string if role is a quality gate, None otherwise
        """
        if role in QUALITY_GATE_ROLES:
            return (
                f"?? Warning: '{role}' is a quality gate role. "
                f"Skipping this role will be logged in the audit trail. "
                f"Confirm with 'Yes, skip {role}' to proceed."
            )
        return None
    
    def is_quality_gate(self, role: str) -> bool:
        """
        Check if role is a quality gate.
        
        Args:
            role: Role to check
            
        Returns:
            True if role is a quality gate
        """
        return role in QUALITY_GATE_ROLES
    
    def record_deviation(
        self,
        action: str,
        reason: str,
        skipped_roles: list,
        consent_type: str = "explicit"
    ) -> None:
        """
        Record a deviation to the state file.
        
        Args:
            action: Type of deviation (e.g., 'skip_role', 'skip_dor')
            reason: User's exact words / justification
            skipped_roles: List of roles being skipped
            consent_type: 'explicit' or 'confirmed_ambiguous'
        """
        deviation = {
            "action": action,
            "reason": reason,
            "skipped_roles": skipped_roles,
            "from_role": self._machine.current_role,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "consent_type": consent_type,
        }
        
        # Append to state's deviations list
        self._machine._state.deviations.append(deviation)
        self._machine._save()
    
    def get_deviations(self) -> list:
        """
        Return all logged deviations for current work item.
        
        Returns:
            List of deviation records
        """
        return list(self._machine._state.deviations)
