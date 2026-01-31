# GCP2-006: Project Owner Assistant Decision Notes

**Work Item**: GCP2-006 - Multi-Session and Multi-Work-Item Support  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **File-based state enables persistence**: State files in WorkItems/ survive session restarts.

2. **Explicit switching required**: User must explicitly switch work items; no auto-detection.

3. **"Parking" concept**: User can pause a work item with notes and return later.

4. **Confirmation prompts**: Prevent accidental work on wrong work item.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| Auto-detect work item from context | Too magic; could cause confusion |
| Single work item only | Limits real-world usage patterns |
| Real-time collaboration | Out of scope for MVP |

---

## Tradeoffs Accepted

- **Manual switching**: User must remember to switch; no auto-detection.
- **No conflict resolution**: Single-user assumption; multi-user deferred.

---

## Known Limitations

- No locking mechanism for concurrent access
- Parked work items may become stale

---

## Must-Ask Checklist Responses

- **Interface type**: CLI commands + agent API
- **Target platform**: Cross-platform
- **Data persistence**: JSON files in WorkItems/
- **User type**: Technical (developers)
