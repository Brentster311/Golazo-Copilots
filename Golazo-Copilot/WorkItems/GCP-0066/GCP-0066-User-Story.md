**Status**: BACKLOG

**User Story**
- Title: Require Documenter changelog maintenance with pre-step version update
- As a: Golazo workflow maintainer
- I want: the Documenter role to update the changelog at the end of `README.md` and only after the version has been defined/updated for the release
- So that: release documentation is accurate, chronologically complete, and aligned with the published package version
- Out of scope: redesigning changelog format, introducing a separate changelog file, or changing versioning policy beyond ordering and enforcement
- Assumptions:
  - Assumption (explicit): Interface type remains the existing Golazo MCP workflow and role files (no new UI surface).
  - Assumption (explicit): Target platform remains cross-platform with markdown/file updates in-repo.
  - Assumption (explicit): Data persistence remains repository files (`README.md`, `pyproject.toml`, role notes/state).
- Acceptance Criteria (bulleted, testable):
  - Documenter role instructions explicitly require updating the changelog section at the end of `README.md`.
  - Builder/Documenter workflow order enforces that version is defined/updated before changelog is updated.
  - Tests cover role guidance/behavior expectations for changelog maintenance and version-before-changelog sequencing.
  - Existing workflows remain backward compatible except for the new required changelog/version sequencing checks.
- Non-functional requirements:
  - Clear, deterministic validation messages when sequencing is violated.
  - No regression in existing role-transition behavior outside this scope.
- Telemetry / metrics expected:
  - Tests proving changelog updates are required and ordered after version definition.
  - Manual verification by inspecting `README.md` and version source updates in a sample work item flow.
- Rollout / rollback notes:
  - Rollout: merge role instruction changes, workflow logic updates, and tests together.
  - Rollback: revert sequence enforcement and role text updates if workflow regressions appear.
