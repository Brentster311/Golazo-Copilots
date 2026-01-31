# GCP2-003: Program Manager Decision Notes

**Work Item**: GCP2-003 - Structured State Management  
**Role**: Program Manager  
**Date**: 2026-01-27

---

## Decisions Made

1. **JSON over YAML**: Confirmed PO Assistant decision. JSON requires no external dependencies and has excellent Python support via standard library.

2. **Per-work-item state files**: Each work item gets its own `state.json` rather than a global state file. This:
   - Keeps state co-located with artifacts
   - Simplifies multi-work-item scenarios
   - Allows state to be committed to git if desired

3. **Schema versioning from day one**: Including `schemaVersion` field enables future migrations without breaking existing state files.

4. **Pretty-printed JSON**: Human readability is worth the minor file size increase. Developers may need to inspect state manually during debugging.

5. **No gitignore recommendation**: State files should NOT be gitignored by default. This allows:
   - Sharing workflow state with team (future)
   - Resuming work on different machines
   - Audit trail in git history

---

## Scope Validation

The User Story scope is appropriate for this work item:
- ? Single responsibility: state persistence
- ? Clear boundaries: no state machine logic (GCP2-001a)
- ? Testable independently
- ? No scope creep identified

---

## Sequencing Rationale

GCP2-003 must be first because:
1. GCP2-001a (State Machine) cannot persist state without it
2. GCP2-001b (Consent Enforcement) logs deviations to state
3. GCP2-005 (IDE Extensions) reads state for display

**Critical path**: GCP2-003 ? GCP2-001a ? everything else

---

## Risks Highlighted

| Risk | Mitigation |
|------|------------|
| Schema evolution | schemaVersion field + migration functions |
| File corruption | Validate on load; don't crash on bad data |
| Path issues | Use pathlib for cross-platform paths |

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| JSON vs YAML? | JSON (no deps, native support) |
| Global vs per-item state? | Per-item (co-location, simpler) |
| Gitignore state files? | No (enable sharing/audit) |

---

## Handoff Notes for Reviewer/Architect

- Design is intentionally simple (single module, ~100-200 lines)
- No external dependencies
- Schema is documented in appendix
- Test strategy covers happy path + error cases
