# GCP-0069 Developer Decision Notes

## Scope Implemented
- Added `scope` support to `golazo_bootstrap` with supported values `Workspace` and `User`.
- Preserved backward compatibility by treating omitted or empty `scope` as `Workspace`.
- Added shared scope-aware orchestrator instruction resolution so workflow preflight accepts either workspace-scoped or user-scoped orchestrator instructions.
- Kept the change localized to bootstrap, path resolution, dispatch wiring, formatter output, and legacy server parity.

## TDD Evidence
### Red phase
Ran the existing focused GCP-0069 suites before changing production code:

```powershell
$env:PYTHONPATH='Q:\src\Golazo-Copilots\Golazo-Copilot\golazo-copilot\src'
q:/src/Golazo-Copilots/Golazo-Copilot/.venv/Scripts/python.exe -m pytest golazo-copilot/tests/test_gcp_bootstrap.py golazo-copilot/tests/test_server_dispatch.py golazo-copilot/tests/test_server_legacy_coverage.py -q
```

Observed expected failures:
- bootstrap result missing `scope`
- `golazo_bootstrap(..., scope=...)` rejected because `scope` was not implemented
- bootstrap tool schema missing `scope`
- workflow preflight rejected valid user-scope instructions
- legacy `has_orchestrator_instructions` remained workspace-only

### Green phase
After implementation, ran the focused validation suites:

```powershell
$env:PYTHONPATH='Q:\src\Golazo-Copilots\Golazo-Copilot\golazo-copilot\src'
q:/src/Golazo-Copilots/Golazo-Copilot/.venv/Scripts/python.exe -m pytest golazo-copilot/tests/test_gcp_bootstrap.py golazo-copilot/tests/test_server_dispatch.py golazo-copilot/tests/test_server_legacy_coverage.py golazo-copilot/tests/test_server_formatters.py -q
```

Result: `78 passed`.

## Implementation Decisions
- Added shared helpers in `golazo-copilot/src/golazo_copilot/dispatch/paths.py` for:
  - workspace orchestrator path resolution
  - user-scope orchestrator path resolution under `Path.home() / '.copilot'`
  - scope normalization and validation
  - effective bootstrap target resolution
- Updated `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py` to:
  - accept `scope`
  - validate supported values early
  - write orchestrator instructions to user scope when requested
  - return `scope` and `target_path` metadata in success results
  - keep non-orchestrator bootstrap artifacts (`WorkItems`, `capabilities.yaml`, role files) workspace-scoped
- Updated modular dispatch wiring in:
  - `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
  - `golazo-copilot/src/golazo_copilot/handlers/tools.py`
  - `golazo-copilot/src/golazo_copilot/dispatch/router.py`
- Updated `golazo-copilot/src/golazo_copilot/formatters/results.py` so successful bootstrap output exposes scope and resolved target path.
- Updated legacy parity in `golazo-copilot/src/golazo_copilot/server.py` so pre-modular coverage behavior matches the shared helper behavior.
- Added formatter coverage in `golazo-copilot/tests/test_server_formatters.py` for the visible target-path output.

## Environment / Validation Notes
- The active virtual environment initially contained only `pip`, so I installed the repository-declared runtime and dev dependencies needed to execute the requested tests:
  - `mcp>=1.0.0`
  - `pydantic>=2.0.0`
  - `PyYAML>=6.0`
  - `pytest>=7.0.0`
  - `pytest-asyncio>=0.21.0`
- Editor error check on all touched source and test files reported no errors.

## Files Changed
- `golazo-copilot/src/golazo_copilot/dispatch/paths.py`
- `golazo-copilot/src/golazo_copilot/tools/golazo_bootstrap.py`
- `golazo-copilot/src/golazo_copilot/dispatch/registry.py`
- `golazo-copilot/src/golazo_copilot/handlers/tools.py`
- `golazo-copilot/src/golazo_copilot/dispatch/router.py`
- `golazo-copilot/src/golazo_copilot/formatters/results.py`
- `golazo-copilot/src/golazo_copilot/server.py`
- `golazo-copilot/tests/test_server_formatters.py`
- `WorkItems/GCP-0069/RoleDecisionNotes/GCP-0069-developer.md`

## Capability Impact
- Ran capability impact analysis on the changed implementation/test files.
- Result: `0 capabilities affected`.

## Assumptions
- `scope="User"` only redirects orchestrator-instruction placement; the rest of full bootstrap remains workspace-scoped.
- The active user Copilot root for this story is defined by `Path.home() / '.copilot'`, matching the approved design and tests.
- README updates were deferred to keep the developer-role change minimal and localized; the public contract change is covered by tool schema, formatter output, and tests.