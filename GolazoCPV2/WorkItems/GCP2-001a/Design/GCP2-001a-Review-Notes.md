# GCP2-001a: Architect Review Notes

**Work Item**: GCP2-001a - Core State Machine  
**Role**: Architect  
**Date**: 2026-01-31

---

## Review Summary

| Area | Status | Notes |
|------|--------|-------|
| Architectural Alignment | ? Pass | Clean layering on GCP2-003 |
| APIs and Contracts | ?? Issue | Transition return type needs clarification |
| Security/Privacy | ? Pass | No sensitive data |
| Scalability | ? Pass | Single work item, deterministic |
| Resilience | ?? Issue | Missing validation on role names |
| Dependencies | ? Pass | Only uses GCP2-003 |

**Overall**: Approved with required changes

---

## Architectural Alignment

### Layering
```
???????????????????????????????????????
?     GCP2-001b (Consent)             ?  ? Future: wraps machine
???????????????????????????????????????
?     GCP2-001a (State Machine)       ?  ? This module
???????????????????????????????????????
?     GCP2-003 (State Persistence)    ?  ? Uses this
???????????????????????????????????????
```

? Clean separation. State machine handles transitions, state layer handles persistence.

---

## API Contract Issues

### Issue 1: `transition()` Return Type

**Design Doc says**: `transition(target) ? bool`
**Problem**: Caller can't distinguish between:
- Transition succeeded
- Transition failed (invalid)
- Transition failed (DoR incomplete)

**Recommendation**: Return `tuple[bool, str]` like `can_transition()`:
```python
def transition(self, target_role: str) -> tuple[bool, str]:
    """Returns (success, message)"""
```

### Issue 2: Missing `mark_dor_item()` / `mark_dod_item()` Methods

**Design Doc shows**: `update_dor(item, value)` and `update_dod(item, value)`
**But API in User Story doesn't include these.**

**Recommendation**: Add to API:
```python
def mark_dor(self, item: str, complete: bool = True) -> None:
    """Mark DoR item as complete/incomplete."""

def mark_dod(self, item: str, complete: bool = True) -> None:
    """Mark DoD item as complete/incomplete."""
```

---

## Resilience Issues

### Issue 3: Role Name Validation

**Problem**: What if caller passes invalid role name?
```python
machine.can_transition("invalid-role")  # What happens?
```

**Recommendation**: Validate role names against known roles list:
```python
VALID_ROLES = ["project-owner", "program-manager", "tester", "architect", 
               "developer", "refactor-expert", "builder", "documentor"]

def can_transition(self, target_role: str) -> tuple[bool, str]:
    if target_role not in VALID_ROLES:
        return (False, f"Unknown role: {target_role}")
```

### Issue 4: Role History Update

**Problem**: Design doesn't specify how `roleHistory` is updated on transition.

**Recommendation**: On transition:
1. Set `exitedAt` on current role entry
2. Append new entry with `enteredAt`, `exitedAt=None`

---

## Phase Derivation Logic

**Design says**: "Phase is derived from current role"

**Recommendation**: Explicit mapping:
```python
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
```

Update `currentPhase` when role changes.

---

## Required Changes Before Implementation

| Priority | Change | Rationale |
|----------|--------|-----------|
| **High** | `transition()` returns `tuple[bool, str]` | Consistent with `can_transition()` |
| **High** | Add role name validation | Prevent silent failures |
| **Medium** | Add `mark_dor()` / `mark_dod()` methods | Complete API |
| **Medium** | Document roleHistory update logic | Ensure audit trail |

---

## Approval

**Status**: ? **Approved with required changes**

The design is sound. Address the 4 issues above in implementation.
