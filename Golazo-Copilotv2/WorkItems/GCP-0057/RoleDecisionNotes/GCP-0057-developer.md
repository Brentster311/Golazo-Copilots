# GCP-0057 — Developer Notes

## Implementation Summary
- Added `mode` support to `golazo_bootstrap` with values `full` and `orchestrator-only`.
- Implemented `orchestrator-only` behavior to manage only `.github/copilot-instructions.md`.
- Added invalid-mode validation with explicit supported values.
- Added workflow preflight gating in server dispatch when orchestrator instructions are missing.
- Added version-only `golazo_status` bypass to keep diagnostics available.

## Files Changed
- `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/tests/test_gcp_bootstrap.py`
- `golazo-copilot/tests/test_server_dispatch.py`
- `golazo-copilot/README.md`

## Test-First / Verification Notes
- Added mode and preflight tests before/with code changes.
- Executed targeted tests with workspace virtual environment:
  - `..\\.venv\\Scripts\\python.exe -m pytest tests/test_gcp_bootstrap.py tests/test_server_dispatch.py tests/test_server_formatters.py`
- Result: all tests passed.

## Risks Addressed
- Avoided hidden writes by limiting file mutation to bootstrap tool.
- Scoped gating to workflow tools only.
- Preserved backward compatibility by defaulting mode to `full`.

