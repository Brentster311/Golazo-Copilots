# GCP2-001a: Core State Machine - Design Document

**Work Item**: GCP2-001a  
**Version**: 1.0  
**Created**: 2026-01-31  
**Author**: Program Manager

---

## Summary

Implement a `GolazoStateMachine` class that manages workflow state transitions, validates role sequencing, and enforces DoR/DoD gates. This builds on GCP2-003 (state persistence) to provide the core workflow enforcement logic.

---

## Problem Statement

GCP2-003 provides state persistence but no business logic. We need:
- Role transition validation (which roles can follow which)
- Phase boundary enforcement (DoR must be complete before Development)
- DoR/DoD status checking
- Deterministic state management

Without this, the agent cannot programmatically enforce the Golazo workflow.

---

## Business Case

### Why Now?
This is the core logic layer. Without it:
- GCP2-001b (Consent) has nothing to enforce
- GCP2-001c (CLI) has no commands to expose
- GCP2-001d (MCP) has no tools to wrap

**Blocking**: Must complete before all other GCP2-001 sub-items.

### Impact
| Metric | Before | After |
|--------|--------|-------|
| Programmatic transition validation | None | Full |
| DoR enforcement | Human only | Automated |
| Phase tracking | Implicit | Explicit |

---

## Requirements

### Functional Requirements

| ID | Requirement | Source |
|----|-------------|--------|
| FR-1 | `GolazoStateMachine` class with role/phase tracking | AC-1 |
| FR-2 | `current_role` property returns active role | AC-2 |
| FR-3 | `current_phase` property returns active phase | AC-2 |
| FR-4 | `can_transition(target)` returns (bool, reason) | AC-3 |
| FR-5 | `transition(target)` updates state and persists | AC-4 |
| FR-6 | `check_dor()` returns DoR status dict | AC-5 |
| FR-7 | `check_dod()` returns DoD status dict | AC-5 |
| FR-8 | Block Developer role if DoR incomplete | AC-6 |
| FR-9 | Load/save state via GCP2-003 functions | AC-7 |

### Non-Functional Requirements

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-1 | Synchronous operations | No async |
| NFR-2 | Deterministic behavior | Same input = same output |
| NFR-3 | Standard library only | No external deps |
| NFR-4 | Clear error messages | Include reason for blocked transitions |

---

## Proposed Approach

### High-Level Design

```
???????????????????????????????????????
?       GolazoStateMachine            ?
???????????????????????????????????????
? - state: State                      ?
? - work_item_id: str                 ?
? - base_path: Path                   ?
???????????????????????????????????????
? + current_role: str                 ?
? + current_phase: str                ?
? + profile: str                      ?
? + can_transition(target) ? (bool,str)?
? + transition(target) ? bool         ?
? + check_dor() ? dict                ?
? + check_dod() ? dict                ?
? + update_dor(item, value)           ?
? + update_dod(item, value)           ?
???????????????????????????????????????
           ?
           ?
    GCP2-003: State Layer
    (load_state, save_state)
```

### Role Transition Rules

Based on GCP2-002 (Workflow Phases and Role Structure):

```
Design Phase:
  project-owner ? program-manager ? tester ? architect

Development Phase (requires DoR complete):
  developer ? refactor-expert

Release Phase:
  builder ? documentor

Special:
  Any role ? builder (branch creation at start)
```

### Phase Boundaries

| From Phase | To Phase | Gate |
|------------|----------|------|
| design | development | DoR must be complete |
| development | release | Tests must pass |

### Valid Transition Matrix

```python
TRANSITIONS = {
    # Design phase
    "project-owner": ["program-manager"],
    "program-manager": ["tester"],
    "tester": ["architect"],
    "architect": ["developer"],  # Crosses to Development
    
    # Development phase
    "developer": ["refactor-expert"],
    "refactor-expert": ["builder"],  # Crosses to Release
    
    # Release phase
    "builder": ["documentor"],
    "documentor": [],  # Terminal
}
```

### DoR Check Logic

```python
def is_dor_complete(state: State) -> bool:
    return all([
        state.dor.get("userStory", False),
        state.dor.get("designDoc", False),
        state.dor.get("reviewComments", False),
        state.dor.get("testCases", False),
    ])
```

---

## Implementation Phases

| Phase | Deliverable | Description |
|-------|-------------|-------------|
| 1 | State machine class | Basic structure, properties |
| 2 | Transition validation | `can_transition()` logic |
| 3 | Transition execution | `transition()` with state updates |
| 4 | DoR/DoD helpers | Checklist methods |
| 5 | Phase boundary gates | DoR enforcement at developer entry |

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| External FSM library (transitions) | Battle-tested | Adds dependency | Rejected |
| Enum-based states | Type safety | Less flexible | Rejected |
| Dict-based transitions | Simple, readable | Custom code | **Selected** |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Transition logic bugs | Medium | High | Comprehensive test coverage |
| State corruption | Low | High | Validate before save |
| Phase mismatch | Low | Medium | Derive phase from role |

---

## Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| GCP2-003 (State persistence) | Upstream | ? Complete |
| Python 3.10+ | Runtime | Available |

**Downstream dependents**:
- GCP2-001b (Consent Enforcement) - uses state machine
- GCP2-001c (CLI) - wraps state machine
- GCP2-001d (MCP) - exposes state machine

---

## Test Strategy Summary

| Test Type | Coverage |
|-----------|----------|
| Unit tests | Each transition, DoR/DoD checks |
| Integration | Full workflow traversal |
| Edge cases | Invalid transitions, incomplete DoR |

**Key scenarios**:
1. Valid transition sequence through all roles
2. Blocked transition to developer with incomplete DoR
3. Invalid transition (skip role) rejected
4. State persists across machine instances

---

## File Location

```
src/golazo/
??? __init__.py
??? state.py          # GCP2-003 (existing)
??? machine.py        # GCP2-001a (new)
```
