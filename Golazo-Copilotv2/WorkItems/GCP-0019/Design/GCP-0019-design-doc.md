# GCP-0019: Design Doc - Enforce Role Decision Notes on Transition

## Summary

Add a warning mechanism to `gcp_transition` that alerts when the outgoing role has not created its required decision notes file. This enforces the workflow rule "Every role produces a document."

---

## Problem Statement

The Golazo workflow mandates that every role produces a written artifact, but this is not enforced. In GCP-0014, 8 of 9 role decision notes were skipped because there was no enforcement or reminder.

---

## Business Case

**Why now:** Process compliance failure discovered in GCP-0014.

**Impact:** Improved audit trail and decision documentation.

**KPIs:**
- Reduction in missing role notes (target: <10% of transitions)
- User acknowledgment of warnings

---

## Stakeholders

- Project Owner (benefits from documented decisions)
- AI Assistant (receives warnings to comply)
- Future maintainers (benefit from decision history)

---

## Functional Requirements

1. On `gcp_transition`, check if outgoing role's notes file exists
2. File naming: `WorkItems/<id>/RoleDecisionNotes/<id>-<role-suffix>.md`
3. Role suffix mapping:
   - `project-owner-assistant` → `project-owner-assistant`
   - `program-manager` → `program-manager`
   - `quality-assurance` → `quality-assurance`
   - `architect` → `architect`
   - `developer` → `developer`
   - `refactor-expert` → `refactor` (shortened)
   - `builder` → `builder`
   - `Documenter` → `Documenter`
   - `retrospective` → `retrospective`
4. If file missing, add `warning` to response
5. `gcp_status` includes `missing_notes` list

---

## Non-Functional Requirements

- File check < 10ms
- Works with custom work_items_dir
- No breaking changes to existing API

---

## Proposed Approach

### Phase 1: Add warning to gcp_transition

In `gcp_transition.py`:
1. Before returning success, check if role notes file exists
2. If missing, add `warning` field to result
3. Transition still succeeds (warning, not blocking)

### Phase 2: Add missing_notes to gcp_status

In `gcp_status.py`:
1. Check each role in role_history for notes file
2. Return list of roles missing notes

### Phase 3: Format warnings in server.py

Display warning in formatted output.

---

## Alternatives Considered

| Alternative | Reason Rejected |
|-------------|-----------------|
| Block transition | Too disruptive; some roles may have "No findings" |
| Auto-generate empty notes | Defeats purpose of documenting decisions |
| Require notes before DoR/DoD | Overcomplicates gate logic |

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| False positives for "No findings" | Can create note saying "No findings" |
| Performance impact | File exists check is fast |
| Breaking existing tests | Update test expectations for warning field |

---

## Dependencies

- None

---

## Migration / Rollout Plan

1. Implement warning in gcp_transition
2. Add missing_notes to gcp_status
3. Update tests
4. Version bump (MINOR - new feature)

**Rollback:** Remove warning logic

---

## Observability Plan

- Warning count in transition responses
- missing_notes visible in status

---

## Test Strategy Summary

- Unit test: transition returns warning when notes missing
- Unit test: transition succeeds even with warning
- Unit test: status includes missing_notes list
- Integration: full workflow with notes check
