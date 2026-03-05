# GCP-0020: Design Document

## Summary

Modify `gcp_transition` to **block** transitions when outgoing role's decision notes file is missing, replacing the warning-only behavior from GCP-0019.

## Problem Statement

GCP-0019 implemented warning-only enforcement. Real-world testing proved this insufficient:
- 16 work items had missing role notes despite warnings
- 127 notes created retroactively
- AI assistants acknowledge warnings but don't change behavior

## Business Case

**Why now**: Technical debt from missing notes is expensive to fix retroactively
**Impact**: Every role produces required artifacts as workflow mandates
**KPIs**: Zero transitions without role notes (or explicit consent)

## Stakeholders

- Developers using Golazo Copilot
- Project Owners who need audit trails

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | `gcp_transition` checks if outgoing role's notes file exists |
| FR2 | If missing, transition fails with actionable error message |
| FR3 | Error includes exact file path to create |
| FR4 | `force_without_notes=True` parameter allows bypass with prior consent |
| FR5 | First role (project-owner-assistant) is exempt on entry |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | File check < 10ms |
| NFR2 | Error messages must be actionable |

## Proposed Approach

### Phase 1: Modify `gcp_transition` logic

```python
# In gcp_transition, after validating role sequence:

# Check for role notes (skip for first role entry)
if current_role != "project-owner-assistant":
    notes_path = get_role_notes_path(work_item_id, current_role)
    if not notes_path.exists():
        if force_without_notes:
            # Check for unconsumed consent
            if not has_unconsumed_consent(state):
                return {"success": False, "error": "Cannot force without consent. Call gcp_consent first."}
        else:
            return {
                "success": False,
                "error": f"Cannot transition from {current_role}: Missing role notes.",
                "missing_file": str(notes_path),
                "hint": f"Create the file first, or use force_without_notes=True with prior gcp_consent"
            }
```

### Phase 2: Update tool schema

Add `force_without_notes: bool = False` parameter to `gcp_transition`.

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Warning only (GCP-0019) | Non-breaking | Proved insufficient | Rejected |
| Always block, no bypass | Strictest | Too rigid for spikes | Rejected |
| Block with consent bypass | Balanced | Requires consent mechanism | **Selected** |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaks existing workflows | Medium | High | Consent bypass available |
| User frustration | Low | Medium | Clear error messages with file path |

## Dependencies

- GCP-0019: Existing `get_role_notes_path()` function
- GCP-0005: Consent mechanism for force bypass

## Migration / Rollout / Rollback

- **Breaking change**: Transitions that succeeded with warning will now fail
- **Rollout**: Deploy with release notes explaining change
- **Rollback**: Revert to warning-only behavior

## Observability Plan

- Log blocked transitions with reason
- Count forced transitions with consent

## Test Strategy

1. Transition without notes → blocked
2. Transition with notes → succeeds
3. Force without consent → error
4. Force with consent → succeeds
5. First role entry → exempt (no prior notes needed)
