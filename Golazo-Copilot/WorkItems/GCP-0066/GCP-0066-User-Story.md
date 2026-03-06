**Status**: IMPLEMENTED

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

## Closure

### Summary of what was delivered
- Documenter role defaults now require changelog maintenance at the end of `README.md`.
- Builder/Documenter role guidance now enforces version-first sequencing (version defined/updated before changelog maintenance).
- Added policy test coverage to validate changelog requirement and version-before-changelog semantics.
- Updated checked-in role documentation under `.github/agents/golazo-copilot/roles/` for consistency with defaults.
- Bumped package version from `4.3.2` to `4.3.3` before changelog maintenance work.

### Acceptance criteria pass/fail status
- AC1 PASS: Documenter role instructions explicitly require changelog maintenance at end of `README.md`.
- AC2 PASS: Version-first sequencing requirement is explicit in role guidance.
- AC3 PASS: Tests cover policy semantics (`test_gcp0066_documenter_changelog_policy.py`) and targeted regression suite remains green.
- AC4 PASS: Existing role workflow behavior remains compatible; changes are guidance/test focused.

### Future work items
- Candidate follow-up: introduce optional runtime transition gate to hard-enforce version/changelog evidence, rather than relying on policy+tests only.
- Candidate follow-up: resolve unrelated baseline failure in `golazo-copilot/tests/test_golazo_update.py::TestCheckAction::test_tc06b_check_http_401_fallback_pip_index_success`.

### Final status confirmation
- Work item scope is implemented and validated against acceptance criteria.
