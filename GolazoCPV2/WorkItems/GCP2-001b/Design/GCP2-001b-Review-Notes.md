# GCP2-001b: Architect Review Notes

**Work Item**: GCP2-001b - Consent Enforcement  
**Role**: Architect  
**Date**: 2026-01-31

---

## Review Summary

| Area | Status | Notes |
|------|--------|-------|
| Architectural Alignment | ? Pass | Clean layering on GCP2-001a |
| APIs and Contracts | ?? Issue | `force_transition` location |
| Security/Privacy | ? Pass | Audit log is append-only |
| Scalability | ? Pass | Patterns are O(n) |
| Resilience | ? Pass | Deterministic behavior |
| Dependencies | ? Pass | Uses only GCP2-001a, GCP2-003 |

**Overall**: Approved with required changes

---

## Architectural Alignment

### Layering
```
???????????????????????????????????????
?     GCP2-001c/d (CLI/MCP)           ?  ? Future: uses consent
???????????????????????????????????????
?     GCP2-001b (ConsentEnforcer)     ?  ? This module
???????????????????????????????????????
?     GCP2-001a (StateMachine)        ?  ? Uses this
???????????????????????????????????????
?     GCP2-003 (State Persistence)    ?  ? Uses this
???????????????????????????????????????
```

? Clean separation. ConsentEnforcer wraps state machine, doesn't modify it.

---

## API Issues

### Issue 1: `force_transition()` Responsibility

**Design Doc proposes**: `ConsentEnforcer.force_transition()`
**Concern**: This creates tight coupling. ConsentEnforcer should analyze and record, not execute transitions.

**Recommendation**: Keep transition execution in StateMachine. Add `force` parameter:

```python
# In machine.py (modify existing)
def transition(self, target: str, force: bool = False, reason: str = None) -> tuple[bool, str]:
    """If force=True, skip validation gates."""

# In consent.py (new)
class ConsentEnforcer:
    def record_deviation(self, action: str, reason: str, skipped_roles: list[str]) -> None:
        """Record deviation to state. Does NOT transition."""
```

Then caller (CLI/MCP) orchestrates:
```python
enforcer.record_deviation("skip_role", user_words, ["tester"])
machine.transition("developer", force=True)
```

### Issue 2: Missing `is_quality_gate()` Helper

**Recommendation**: Add to expose quality gate logic:
```python
def is_quality_gate(self, role: str) -> bool:
    """Returns True if role is a quality gate (tester, architect)."""
```

---

## Pattern Design Review

### Explicit Patterns: ? Adequate
```python
r"skip\s+(the\s+)?(\w+)\s+role"  # "skip the tester role"
r"skip\s+to\s+(\w+)"              # "skip to developer"
r"fast[- ]?track"                  # "fast-track", "fast track"
```

### Ambiguous Patterns: ? Conservative
```python
r"just\s+fix"       # "just fix this"
r"quick\s+fix"      # "quick fix"
```

### Recommendation: Add Pattern for Profile Selection
```python
r"use\s+(express|spike)\s+(mode|profile)"  # "use express mode"
```
This should map to profile selection, not ad-hoc skipping.

---

## Deviation Record Format

**Proposed format is good**. One addition:

```python
{
    "action": "skip_role",
    "reason": "just fix it",
    "skipped_roles": ["tester"],
    "from_role": "program-manager",
    "to_role": "developer",
    "timestamp": "2026-01-31T...",
    "consent_type": "explicit"  # ADD: 'explicit' or 'confirmed_ambiguous'
}
```

---

## Required Changes Before Implementation

| Priority | Change | Rationale |
|----------|--------|-----------|
| **High** | Remove `force_transition()` from ConsentEnforcer | Separation of concerns |
| **High** | Add `force` param to StateMachine.transition() | Single responsibility |
| **Medium** | Add `is_quality_gate()` method | Clean API |
| **Low** | Add `consent_type` to deviation record | Better audit trail |

---

## Approval

**Status**: ? **Approved with required changes**

The design is sound. Address the 4 issues above in implementation.
