# GCP2-001a: Program Manager Decision Notes

**Work Item**: GCP2-001a - Core State Machine  
**Role**: Program Manager  
**Date**: 2026-01-31

---

## Decisions Made

1. **Custom state machine over library**: No external dependencies, simple transition dict approach.

2. **Role-based phase derivation**: Phase is derived from current role rather than stored separately. This prevents phase/role mismatches.

3. **Transition matrix as dict**: Simple `TRANSITIONS = {"from_role": ["valid_targets"]}` structure.

4. **DoR gate at architect?developer boundary**: This is the design?development phase transition.

5. **File location**: `src/golazo/machine.py` alongside `state.py`.

---

## Sequencing Rationale

GCP2-001a must complete before:
- GCP2-001b needs state machine to add consent logic
- GCP2-001c needs state machine to expose via CLI
- GCP2-001d needs state machine to wrap as MCP tools

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| External FSM library? | No - keep deps minimal |
| Phase stored separately? | No - derive from role |
| Skip roles allowed? | No - sequential only (consent logic in GCP2-001b) |

---

## Handoff Notes for Architect

- Review transition matrix for completeness
- Verify phase derivation logic
- Consider: should `transition()` return the new state or just bool?
