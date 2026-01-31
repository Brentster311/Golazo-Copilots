# GCP2-003: Architect Decision Notes

**Work Item**: GCP2-003 - Structured State Management  
**Role**: Architect  
**Date**: 2026-01-27

---

## Decisions Made

1. **Atomic writes**: Recommended write-to-temp-then-rename pattern to prevent state file corruption from interrupted writes.

2. **Path sanitization**: WorkItemId must be validated to prevent path traversal attacks (reject `..`, `/`, `\` characters).

3. **UTF-8 encoding**: Use `ensure_ascii=False` in json.dumps for proper Unicode support.

4. **UTC timestamps**: All timestamps should be UTC to avoid timezone confusion.

5. **Schema migration**: Version check on load with migration function for forward compatibility.

6. **Missing fields on load**: Use defaults and log warning rather than failing.

---

## Alternatives Considered

| Decision | Alternative | Why Rejected |
|----------|-------------|--------------|
| Atomic writes | Direct write | Risk of corruption on interrupt |
| Dataclass | TypedDict | Dataclass provides better ergonomics |
| Relative paths | Absolute paths | Relative is more portable |

---

## Tradeoffs Accepted

- **No file locking**: Single-user assumption means no concurrent access protection. Acceptable for MVP; GCP2-006 may revisit.
- **No backup on save**: Simplicity over safety. Users can rely on git for history.

---

## Security Considerations

- Path traversal: MUST validate workItemId
- No sensitive data in state files
- File permissions: OS defaults sufficient

---

## Coupling Analysis

| Component | Coupling Level | Notes |
|-----------|---------------|-------|
| GCP2-001a | Low | Consumes State dataclass |
| GCP2-005 | Low | Reads JSON file directly |
| File system | High | Direct dependency (acceptable) |

---

## Handoff Notes for Tester

- Test atomic write behavior (simulate interrupt)
- Test path traversal rejection
- Test schema migration from v1.0 to future versions
- Test corrupted JSON handling
