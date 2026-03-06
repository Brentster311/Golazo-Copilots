**Status**: IMPLEMENTED

**User Story**
- Title: Fix Windows Azure CLI preflight detection in `golazo_update`
- As a: Golazo Copilot user on Windows
- I want: `golazo_update(action="install")` to correctly detect and run Azure CLI authentication checks
- So that: update installs do not fail with false "az not installed" errors when Azure CLI is available and logged in
- Out of scope: redesigning update workflow, changing feed/auth model, or adding new update targets beyond current scope
- Assumptions:
  - Assumption (explicit): Interface type remains existing MCP tool invocation (`golazo_update`).
  - Assumption (explicit): Target platform remains cross-platform, with explicit Windows process-resolution hardening.
  - Assumption (explicit): Data persistence remains repository code/tests/docs only.
- Acceptance Criteria (bulleted, testable):
  - On Windows, `golazo_update` preflight resolves Azure CLI robustly (including common executable naming/lookup behavior) before failing with not-found.
  - Error messages distinguish: CLI missing, CLI found but not logged in, and CLI execution failure/timeout.
  - Existing non-Windows behavior remains backward compatible.
  - Automated tests cover Windows path/executable resolution behavior and failure-mode messaging.
  - Documentation for `golazo_update` prerequisites/behavior is updated if wording changes are needed.
- Non-functional requirements:
  - No regression to install success path or security posture.
  - Deterministic, actionable error output.
- Telemetry / metrics expected:
  - Targeted tests proving Windows preflight no longer produces false negatives when CLI is available.
  - Regression test pass for update/status tool suites.
- Rollout / rollback notes:
  - Rollout: ship code, tests, and docs together.
  - Rollback: revert preflight resolution changes if cross-platform regressions appear.

## Closure

### Summary of Delivery
- Implemented Windows-aware Azure CLI resolution in `golazo_update` preflight (`az` with `az.cmd` fallback).
- Preserved non-Windows executable resolution behavior.
- Added focused tests for Windows fallback and missing-CLI fail-fast behavior.
- Updated README update-tool prerequisite behavior notes and included release-note entry.

### Acceptance Criteria Validation
- AC1 PASS: Windows preflight resolver behavior validated by `TestGcp0068WindowsAzPreflight::test_windows_uses_az_cmd_fallback_when_az_missing`.
- AC2 PASS: Missing CLI, not logged in, timeout, and execution-failure branches validated by update-tool tests and preflight branch assertions.
- AC3 PASS: Regression suites passed without non-Windows behavioral regressions (`test_server_formatters.py`, `test_server_dispatch.py`, and broader `test_golazo_update.py`).
- AC4 PASS: Automated tests added and executed for Windows resolution and failure-mode messaging.
- AC5 PASS: Documentation updated in `golazo-copilot/README.md` with Windows preflight details.

### Future Work Items
- Capture workflow-role asset version drift handling as a new process-improvement item.
- Add a version-handshake checkpoint between documenter and builder roles.
- Improve coverage instrumentation reliability for `test_golazo_update.py` import style.

### Final Status Confirmation
- User Story status is set to **IMPLEMENTED**.
