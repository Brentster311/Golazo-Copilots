# GCP-0020: Block Transition Without Role Notes

**Status**: IMPLEMENTED (v2.11.0)

---

## User Story

- **Title**: Block Role Transitions Until Decision Notes Are Created
- **As a**: Project Owner using Golazo workflow
- **I want**: `gcp_transition` to **block** (not just warn) when the outgoing role has not produced its required decision notes
- **So that**: Role notes are created at the right time, not retroactively

---

## Problem Statement

GCP-0019 implemented warning-only enforcement for role notes. Real-world testing proved this was **insufficient**:

- **16 work items** had missing role notes despite warnings
- **127 notes** had to be created retroactively
- AI assistants acknowledge warnings but don't change behavior
- Retroactive note creation loses context and is more expensive

**Conclusion**: Blocking is necessary to enforce compliance.

---

## Out of Scope
- Automatic generation of role notes content (AI still writes them)
- Retroactive blocking on existing work items
- Changing the role notes file structure

---

## Assumptions
- **Assumption (explicit)**: Blocking can be bypassed with `force_without_notes=True` + prior `gcp_consent`
- **Assumption (explicit)**: Project-owner-assistant role is exempt (first role, no prior notes needed)
- **Assumption (explicit)**: This is a breaking change from warning-only behavior

---

## Acceptance Criteria

- [x] `gcp_transition` fails if outgoing role's decision notes file is missing
- [x] Error message: "Cannot transition from <role>: Missing role notes file. Create `WorkItems/<id>/RoleDecisionNotes/<id>-<role>.md` first."
- [x] Error includes the expected file path for easy creation
- [x] `force_without_notes=True` parameter allows bypass IF prior `gcp_consent` recorded
- [x] Without prior consent, `force_without_notes=True` fails with: "Cannot force without consent. Call gcp_consent first."
- [x] First role (project-owner-assistant) is exempt from blocking on entry
- [x] `gcp_status` output reminds user to create notes before transitioning

---

## Non-Functional Requirements
- File existence check should be fast (<10ms)
- Error messages should be actionable (include exact file path)

---

## Telemetry / Metrics Expected
- Count of blocked transitions due to missing notes
- Count of forced transitions (with consent)

---

## Rollout / Rollback Notes
- **Breaking change**: Transitions that previously succeeded with warning will now fail
- Rollback: Revert to warning-only behavior (GCP-0019)

---

## Technical Notes

### Modified Tool: `gcp_transition`

```python
async def gcp_transition(
    work_item_id: str,
    role: str,
    force: bool = False,
    force_without_notes: bool = False  # NEW parameter
) -> dict:
```

### Logic Flow

```
1. Check if transitioning FROM a role (not initial entry)
2. If yes, check if role notes file exists
3. If missing:
   a. If force_without_notes=True AND has unconsumed consent → allow
   b. If force_without_notes=True AND no consent → error "consent required"
   c. Otherwise → error "create notes first"
4. If exists → proceed with transition
```

---

## Related Work Items
- GCP-0019: Warning-only enforcement (this replaces that approach)
- GCP-0005: Consent mechanism (reused for force bypass)

---

## Closure
- Summary: Backfilled during closure reconciliation.
- Acceptance Criteria: Validation deferred to original implementation records.
- Future Work Items: None.
- Final Status: IMPLEMENTED.
