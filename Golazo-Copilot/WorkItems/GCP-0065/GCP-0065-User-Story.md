**Status**: BACKLOG

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
