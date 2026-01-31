# GCP2-001a: Project Owner Assistant Decision Notes

**Work Item**: GCP2-001a - Core State Machine  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **Custom state machine over library**: Chose to implement custom rather than using `transitions` library because:
   - Simpler dependency management
   - Full control over transition logic
   - Easier to integrate consent-based enforcement later

2. **Synchronous operations**: All state machine operations are synchronous because:
   - Simpler to reason about
   - File I/O is fast enough for local JSON files
   - Async would add unnecessary complexity for MVP

3. **Acceptance criteria reduced to 7**: Consolidated 10 original criteria into 7 to comply with PO Assistant rules.

4. **DoR gate at phase boundary**: Transition from Design to Development phase requires DoR complete, enforcing the quality gate.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| `transitions` library | External dependency; custom is simpler for our needs |
| Async state operations | Unnecessary complexity; file I/O is fast |
| In-memory only state | Wouldn't support session persistence |
| Database-backed state | Overkill; files are sufficient |

---

## Tradeoffs Accepted

- **No parallel transitions**: State machine assumes sequential role progression. Parallel work on multiple roles not supported.
- **No undo/rollback**: Once a transition occurs, there's no built-in way to go back. Must manually edit state file if needed.

---

## Known Limitations

- Only supports the three defined profiles (complete/express/spike)
- Adding new roles requires code changes (not data-driven yet)
- No validation that artifacts actually exist when checking DoR

---

## Must-Ask Checklist Responses

- **Interface type**: Python library (class API)
- **Target platform**: Cross-platform (Python 3.10+)
- **Data persistence**: JSON files via GCP2-003
- **User type**: Technical (consumed by agent and CLI)
