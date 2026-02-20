# GCP-0002 Design Document: Role Transitions

## Summary

Implement the `gcp_transition` MCP tool that enables workflow role transitions with validation, DoR gate enforcement, and phase tracking.

---

## Problem Statement

After initializing a work item with `gcp_init` (GCP-0001), users need a way to progress through the workflow roles. Without transition validation, Copilot could skip roles or enter the development phase without completing required artifacts.

**GCP-0002** solves: How does a user move between roles with proper gate enforcement?

---

## Business Case

### Why Now
- GCP-0001 (init) is complete but users can't progress
- Role transitions are the core workflow mechanic
- DoR gate is critical for process compliance

### Impact
- **Process compliance**: Prevents premature coding
- **Audit trail**: Role history tracks all transitions
- **Guidance**: Returns role instructions on each transition

### KPIs
- Transitions update state correctly
- Invalid transitions are blocked with clear messages
- DoR gate prevents development phase entry

---

## Stakeholders

| Role | Interest |
|------|----------|
| Developer (primary user) | Needs to progress through workflow |
| Team Lead | Wants DoR enforcement |
| Golazo Copilot maintainers | Need clean, testable transition logic |

---

## Functional Requirements

### FR1: Role Transition
- Update `currentRole` in state
- Close previous role in `roleHistory` (set `exitedAt`)
- Add new role entry with `enteredAt`, `exitedAt: null`
- Update `updatedAt` timestamp
- Save state atomically

### FR2: Transition Validation
- Only allow transitions defined in transition matrix
- Return clear error for invalid transitions

### FR3: DoR Gate
- Block transition to `developer` if any DoR item is false
- Return list of missing items
- Suggest using consent mechanism for override

### FR4: Phase Tracking
- Update `currentPhase` when crossing phase boundaries:
  - `definition`: project-owner, program-manager, quality-assurance, architect
  - `development`: developer, refactor-expert, builder
  - `completion`: Documenter

### FR5: Backward Transitions
- Allow backward transitions with warning
- Do NOT reset DoR/DoD items

---

## Non-Functional Requirements

### NFR1: Performance
- Transition completes in <50ms (state file I/O only)

### NFR2: Reliability
- Atomic state updates (no partial transitions)

### NFR3: Testability
- Transition logic pure functions where possible
- File I/O mockable

---

## Proposed Approach

### Technology Stack
- **Runtime**: Python 3.10+
- **Existing**: Builds on GCP-0001 (persistence, state, types)

### Module Structure
```
golazo_copilot/
??? src/golazo_copilot/
?   ??? core/
?   ?   ??? transitions.py    # NEW: Transition logic
?   ?   ??? ...existing...
?   ??? tools/
?   ?   ??? gcp_transition.py # NEW: MCP tool
?   ?   ??? ...existing...
?   ??? server.py             # MODIFY: Add tool
??? tests/
    ??? test_gcp_transition.py # NEW: Tests
```

### Transition Matrix (Python)
```python
TRANSITIONS = {
    "project-owner": ["program-manager"],
    "program-manager": ["quality-assurance", "project-owner"],
    "quality-assurance": ["architect", "program-manager"],
    "architect": ["developer", "quality-assurance"],
    "developer": ["refactor-expert", "architect"],
    "refactor-expert": ["builder", "developer"],
    "builder": ["Documenter", "refactor-expert"],
    "Documenter": ["builder"],
}

PHASE_MAP = {
    "project-owner": "definition",
    "program-manager": "definition",
    "quality-assurance": "definition",
    "architect": "definition",
    "developer": "development",
    "refactor-expert": "development",
    "builder": "development",
    "Documenter": "completion",
}

DOR_GATE_ROLE = "developer"  # Role that requires DoR complete
```

### Implementation Sequence
1. Create `transitions.py` with validation logic
2. Create `gcp_transition.py` tool
3. Update `server.py` to register tool
4. Write tests

---

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Hard-code transitions | Simpler | Less flexible | **Accepted for v1** |
| Config-driven transitions | Flexible | More complex, GCP-0008 scope | **Deferred** |
| Allow any transition | Simpler | No enforcement | **Rejected** |

---

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| State corruption during transition | Low | High | Atomic file writes (existing) |
| Invalid transition matrix | Low | Medium | Unit tests for all paths |
| DoR gate too strict | Medium | Medium | force flag with consent (GCP-0005) |

---

## Open Questions

1. **Q**: Should we track transition count/frequency?
   **A**: Not in v1. Future analytics feature.

2. **Q**: What if user tries to transition with no active work item?
   **A**: Return error: "No active work item. Use gcp_init first."

---

## Dependencies

### Internal
- GCP-0001: State persistence, types, role loader

### External
- None new (uses existing mcp, pydantic)

---

## Test Strategy Summary

### Unit Tests
- Transition matrix validation (all valid paths)
- Invalid transition rejection
- DoR gate blocking
- Phase updates
- Backward transition warnings
- Role history updates

### Integration Tests
- Full transition flow with state file
- Server tool registration

---

## Appendix: State Changes on Transition

**Before** (at `project-owner`):
```json
{
  "currentRole": "project-owner",
  "currentPhase": "definition",
  "roleHistory": [
    { "role": "project-owner", "enteredAt": "...", "exitedAt": null }
  ]
}
```

**After** `gcp_transition({ role: "program-manager" })`:
```json
{
  "currentRole": "program-manager",
  "currentPhase": "definition",
  "roleHistory": [
    { "role": "project-owner", "enteredAt": "...", "exitedAt": "2026-02-02T..." },
    { "role": "program-manager", "enteredAt": "2026-02-02T...", "exitedAt": null }
  ]
}
```
