**Status**: IMPLEMENTED

**User Story**
- Title: Clarify and enforce `golazo_status` vs `golazo_update` behavior and install target selection
- As a: Golazo Copilot user
- I want: `golazo_status` to clearly report state/version context and `golazo_update` to clearly support and communicate install target scope
- So that: I can safely understand what is happening before an update and choose where the update is installed (active environment vs global/system)
- Out of scope: redesigning the overall workflow engine, changing non-update tools, or introducing a separate package manager abstraction
- Assumptions:
  - Assumption (explicit): Interface type is the existing Golazo MCP tool interface (`golazo_status`, `golazo_update`) and accompanying documentation.
  - Assumption (explicit): Target platform is cross-platform (Windows, macOS, Linux) with behavior defined at the Python environment/tooling level.
  - Assumption (explicit): Data persistence remains repository files and runtime environment state (no new database/service).
- Acceptance Criteria (bulleted, testable):
  - `golazo_status` output text and documentation explicitly describe what status reports and what it does not modify.
  - `golazo_update` output text and documentation explicitly describe update actions and available install-target modes.
  - Update execution path supports deterministic install target behavior (for example: active interpreter/environment and explicit global/system target), with safe defaults and clear confirmation messages.
  - Automated tests validate status/update clarity and install-target selection behavior, including at least one negative/error path.
  - Backward compatibility is preserved for existing callers that use current update inputs, except where explicitly documented behavior clarifications are required.
- Non-functional requirements:
  - Messages must be unambiguous and action-oriented to reduce operator confusion.
  - Update behavior must remain idempotent/safe when no newer version is available.
- Telemetry / metrics expected:
  - Unit/integration tests demonstrating status/update behavior clarity and target-selection correctness.
  - Release-note/changelog entry explicitly describing the clarified semantics and target behavior.
- Rollout / rollback notes:
  - Rollout: ship code, tests, and docs together in one release.
  - Rollback: revert update-target additions and message/doc changes if regressions occur in update flow.

## Closure

### Summary of what was delivered
- Clarified `golazo_status` as read-only/reporting in tool descriptions and formatter output.
- Clarified `golazo_update` as state-changing install action and added explicit install target support: `active` (default) and `global`.
- Added deterministic target validation and invalid-target error handling before install attempts.
- Added/updated tests covering semantics clarity, target selection behavior, invalid target handling, and contract parity.
- Updated README documentation and changelog; aligned package version to `4.3.4`.

### Acceptance criteria pass/fail status
- AC1 PASS: `golazo_status` output/docs now explicitly state read-only, non-mutating behavior.
- AC2 PASS: `golazo_update` output/docs now explicitly state install behavior and target modes.
- AC3 PASS: install target behavior is deterministic with explicit confirmation in output (`target`, install command context).
- AC4 PASS: automated tests validate new behavior, including negative/error path for invalid target.
- AC5 PASS: omitted `target` remains backward-compatible with active interpreter install path.

### Future work items
- Candidate follow-up: workflow pre-check for registry parity tests before builder to reduce late-stage rework.
- Candidate follow-up: make stale role-version warning actionable via optional bootstrap reminder gate.

### Final status confirmation
- Scope implemented and validated. Full suite passed in closure validation (`530 passed`).
