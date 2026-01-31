# GCP2-001c: Project Owner Assistant Decision Notes

**Work Item**: GCP2-001c - Golazo Protocol + CLI  
**Role**: Project Owner Assistant  
**Date**: 2026-01-27

---

## Decisions Made

1. **JSON-RPC over stdio**: Chose this protocol because:
   - Proven pattern (similar to LSP)
   - Works with IDE extensions spawning child processes
   - Language-agnostic

2. **CLI as primary interface for MVP**: CLI provides:
   - Standalone usage without IDE
   - Scripting and automation support
   - Easy testing during development

3. **Server mode for IDE integration**: `golazo serve` starts the JSON-RPC server for IDE extensions to connect.

---

## Alternatives Considered

| Option | Rejected Because |
|--------|------------------|
| REST API | Requires running HTTP server; overkill for local tool |
| gRPC | Too heavy; requires protobuf compilation |
| Raw stdin/stdout | No standard message framing |

---

## Tradeoffs Accepted

- **No WebSocket support**: stdio is sufficient for IDE integration; WebSocket would add complexity.

---

## Known Limitations

- Single client at a time in server mode
- No authentication (local use only)

---

## Must-Ask Checklist Responses

- **Interface type**: CLI + JSON-RPC protocol
- **Target platform**: Cross-platform (Python 3.10+)
- **Data persistence**: Via GCP2-003 state files
- **User type**: Technical (developers, IDE extensions)
