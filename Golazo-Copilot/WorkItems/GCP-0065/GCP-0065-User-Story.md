**Status**: IMPLEMENTED

**User Story**
- Title: Resolve `capabilities.yaml` from `WorkItems/` root location
- As a: Golazo workflow maintainer
- I want: Golazo commands that read `capabilities.yaml` to treat `WorkItems/capabilities.yaml` as the canonical location
- So that: capability listing and impact analysis work with the new repository layout without manual path workarounds
- Out of scope: changing capability schema, adding new capability fields, or redesigning impact semantics
- Assumptions:
  - Assumption (explicit): Interface type is existing Golazo MCP command surface (no new UI).
  - Assumption (explicit): Target platform remains cross-platform (Windows/Linux/macOS) with path-safe handling.
  - Assumption (explicit): Data persistence remains repository files only.
- Acceptance Criteria (bulleted, testable):
  - `golazo_capabilities(action="list")` succeeds when capability data exists at `WorkItems/capabilities.yaml`.
  - `golazo_capabilities(action="impact", files=[...])` resolves capability dependencies from `WorkItems/capabilities.yaml`.
  - Existing workflows that pass workspace root continue to work without requiring user-supplied alternate paths.
  - Error messaging clearly indicates expected location when capability file is missing.
- Non-functional requirements:
  - Path resolution logic must be deterministic and covered by tests.
  - No regression in command latency for typical project sizes.
- Telemetry / metrics expected:
  - Manual verification: successful `list` and `impact` execution against relocated file.
  - Test verification: unit/integration coverage for relocated path resolution.
- Rollout / rollback notes:
  - Rollout: merge with tests validating `WorkItems/capabilities.yaml` handling.
  - Rollback: revert path-resolution changes and tests if regressions are discovered.

## Closure

### Summary of what was delivered
- Capability registry canonical path handling now uses `WorkItems/capabilities.yaml`.
- Legacy root `capabilities.yaml` is automatically moved to `WorkItems/capabilities.yaml` when canonical is absent.
- Dual-file scenario is deterministic: canonical file is used and legacy remains untouched.
- Error messaging for missing registry clearly points to `WorkItems/capabilities.yaml`.
- Documentation text was updated to reflect canonical-path and migration behavior.

### Acceptance criteria pass/fail status
- AC1 PASS: `golazo_capabilities(action="list")` resolves and operates with `WorkItems/capabilities.yaml` (covered by updated tests in `golazo-copilot/tests/test_gcp_capabilities.py`).
- AC2 PASS: `golazo_capabilities(action="impact", files=[...])` resolves from canonical registry path (covered by updated tests and impact-analysis checks).
- AC3 PASS: workspace-root workflows remain functional through legacy-to-canonical migration behavior (covered by migration test scenario).
- AC4 PASS: missing-file errors now reference canonical expected path `WorkItems/capabilities.yaml` (covered by missing-file test scenario).

### Future work items
- Candidate follow-up: address unrelated baseline test failure in `golazo-copilot/tests/test_golazo_update.py::TestCheckAction::test_tc06b_check_http_401_fallback_pip_index_success`.

### Final status confirmation
- Work item implementation scope completed and verified against acceptance criteria.
