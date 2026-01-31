# GCP2-003: Project Owner Assistant Decision Notes

**Work Item**: GCP2-003 - Structured State Management  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **JSON over YAML**: Chose JSON for state files because:
   - Native support in Python (`json` module, no dependencies)
   - Easier programmatic manipulation
   - Better IDE/tooling support for validation

2. **File-based persistence**: State stored in local files rather than database because:
   - Simpler implementation
   - Works offline
   - Aligns with existing `WorkItems/` artifact structure
   - No additional dependencies

3. **Schema versioning**: Added `schemaVersion` field to enable future migrations without breaking existing state files.

4. **Acceptance criteria scoped to 7 items**: Per PO Assistant rules, kept AC count within 3-7 range.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| YAML format | Requires PyYAML dependency; less tooling support |
| SQLite database | Overkill for single-user local state |
| In-memory only | Wouldn't persist across sessions |
| Cloud storage | Out of scope; adds complexity and dependencies |

---

## Tradeoffs Accepted

- **No real-time sync**: State file is read/written on demand, not watched for changes. This is acceptable for single-user scenarios.
- **No schema validation at runtime**: Relying on code to produce valid JSON rather than JSON Schema validation. May add validation later if issues arise.

---

## Known Limitations

- State file can become stale if edited outside the agent
- No conflict resolution for concurrent access (not needed for single-user MVP)
- Role history array will grow unbounded (acceptable for typical work item lifecycle)

---

## Must-Ask Checklist Responses

- **Interface type**: Library (Python module for state management)
- **Target platform**: Cross-platform (Python 3.10+)
- **Data persistence**: JSON files in `WorkItems/<id>/state.json`
- **User type**: Technical (developers)
