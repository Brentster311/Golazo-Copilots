# Design Review: Python Code Sandbox App

## Summary
A simple desktop GUI application that allows users to enter Python code and execute it in a restricted sandbox environment.

## Problem Statement
Developers and learners need a quick way to test Python code snippets without opening a full IDE or risking system access from untrusted code.

## Business Case
- **Why now:** Learning tools and quick experimentation environments are always in demand
- **Impact:** Provides a safe, simple way to test Python code
- **Success Metrics/KPIs:** Application runs, executes code, and displays output without crashing

## Stakeholders
- End users (developers, learners)

## Requirements

### Functional
1. GUI window with code input area
2. "Run" button to execute code
3. Output display area for stdout/stderr
4. Clear button to reset input/output

### Non-Functional
1. Sandboxed execution (no file/network/dangerous builtins)
2. 5-second execution timeout
3. Graceful error handling

## Proposed Approach

### Architecture
- Single Python file using `tkinter` for GUI (standard library, no dependencies)
- Use `exec()` with restricted `globals`/`locals` for sandboxing
- Use `threading` + timeout for execution control
- Capture stdout/stderr using `io.StringIO`

### Components
1. **MainWindow:** tkinter root window with layout
2. **CodeInput:** Text widget for code entry
3. **OutputDisplay:** Text widget for results (read-only)
4. **RunButton:** Triggers sandboxed execution
5. **Sandbox:** Restricted execution environment

### Restricted Builtins (allowed)
- `print`, `len`, `range`, `str`, `int`, `float`, `bool`, `list`, `dict`, `tuple`, `set`
- `abs`, `min`, `max`, `sum`, `round`, `sorted`, `reversed`, `enumerate`, `zip`, `map`, `filter`
- `type`, `isinstance`, `hasattr`, `getattr`

### Blocked Builtins
- `open`, `exec`, `eval`, `compile`, `__import__`, `input`
- `globals`, `locals`, `vars`, `dir` (for security)

## Alternatives Considered
1. **Use subprocess:** More isolated but complex IPC
2. **Use RestrictedPython library:** External dependency, overkill for simple app
3. **No sandbox:** Security risk, rejected

## Risks, Mitigations, and Open Questions

| Risk | Mitigation |
|------|------------|
| Infinite loops | 5-second timeout with thread termination |
| Resource exhaustion | Restricted builtins, no file/network |
| Code injection | No nested exec/eval allowed |

**Open Questions:** None

## Dependencies
- Python 3.x standard library only (tkinter, threading, io)

## Migration/Rollout Plan
- N/A (new application)

## Rollback
- Delete the file

## Observability Plan
- None required (simple desktop app)

## Test Strategy Summary
- Unit tests for sandbox restrictions
- Manual GUI testing
- Test timeout behavior
- Test error handling
