**Status**: IMPLEMENTED

**User Story**
- Title: Bootstrap Supports User-Scope Agent Installation
- As a: Golazo Copilot user running the agent from my user Copilot directory
- I want: `golazo_bootstrap` to accept a `scope` parameter that installs orchestrator instructions into either workspace scope or user scope
- So that: workflow operations succeed when the active Golazo agent is installed from the user directory instead of the target workspace
- Out of scope:
  - Changing the default bootstrap target away from workspace scope
  - Adding more than two scope values
  - Broad redesign of bootstrap beyond instruction placement and validation resolution needed for this scenario
  - Migrating or deleting existing workspace-scoped instructions automatically
- Assumptions:
  - Assumption (explicit): this change is for the existing MCP/bootstrap tool interface, not a new CLI or UI surface.
  - Assumption (explicit): valid `scope` values are exactly `Workspace` and `User`, with empty or omitted input treated as `Workspace`.
  - Assumption (explicit): when `scope="User"`, orchestrator instructions should be written under the active user Copilot directory used by the running agent, such as `C:\Users\brentj\.copilot`.
  - Assumption (explicit): workflow preflight checks should accept orchestrator instructions from user scope when the agent is running from user scope, while preserving current workspace-scope behavior.
- Acceptance Criteria (bulleted, testable):
  - Calling `golazo_bootstrap` with no `scope` value, empty `scope`, or `scope="Workspace"` preserves the current behavior and writes orchestrator instructions into `.github/agents/Golazo-Copilot.md` under the target workspace.
  - Calling `golazo_bootstrap` with `scope="User"` writes the orchestrator instructions to the active user Copilot directory instead of the target workspace and reports that location in the bootstrap result.
  - Workflow preflight validation for operations such as `golazo_create_workitem` succeeds when required orchestrator instructions are present in the active user Copilot directory, even if the target workspace does not contain `.github/agents/Golazo-Copilot.md`.
  - Invalid `scope` input is rejected with a clear validation error that names the supported values.
  - Automated tests cover workspace-default behavior, user-scope bootstrap behavior, and instruction resolution used by workflow preflight checks.
- Non-functional requirements:
  - Backward compatibility for existing callers is required.
  - Path handling must work on Windows and remain safe for other supported Python platforms.
  - The implementation should remain minimal and localized to bootstrap and instruction-resolution paths.
- Telemetry / metrics expected:
  - No external telemetry pipeline is required.
  - Bootstrap results should expose the resolved install target so callers can tell which scope was used.
- Rollout / rollback notes:
  - Rollout: release as a backward-compatible MCP server update with `scope` defaulting to workspace behavior.
  - Rollback: revert the new parameter and restore workspace-only instruction resolution if regressions are found.

## Closure

- Summary of what was delivered:
  - Added `scope` support to `golazo_bootstrap` with `Workspace` and `User` values.
  - Preserved default workspace behavior for omitted or empty `scope`.
  - Enabled workflow preflight checks to accept orchestrator instructions from workspace scope or user Copilot scope.
  - Updated bootstrap formatting and README documentation to surface the resolved scope and target path.
  - Released the change as package version `4.4.0` in `golazo-copilot/pyproject.toml`.
- Acceptance criteria pass/fail status:
  - PASS: Calling `golazo_bootstrap` with no `scope` value, empty `scope`, or `scope="Workspace"` preserves current behavior and writes orchestrator instructions into `.github/agents/Golazo-Copilot.md` under the target workspace.
    - Evidence: targeted automated coverage in `golazo-copilot/tests/test_gcp_bootstrap.py`; validated in the focused pytest run with `78 passed`, then revalidated post-version-bump in the builder run with `80 passed`.
  - PASS: Calling `golazo_bootstrap` with `scope="User"` writes the orchestrator instructions to the active user Copilot directory instead of the target workspace and reports that location in the bootstrap result.
    - Evidence: targeted automated coverage in `golazo-copilot/tests/test_gcp_bootstrap.py` and formatter coverage in `golazo-copilot/tests/test_server_formatters.py`; focused pytest runs passed.
  - PASS: Workflow preflight validation for operations such as `golazo_create_workitem` succeeds when required orchestrator instructions are present in the active user Copilot directory, even if the target workspace does not contain `.github/agents/Golazo-Copilot.md`.
    - Evidence: targeted automated coverage in `golazo-copilot/tests/test_server_dispatch.py` and `golazo-copilot/tests/test_server_legacy_coverage.py`; focused pytest runs passed.
  - PASS: Invalid `scope` input is rejected with a clear validation error that names the supported values.
    - Evidence: targeted automated coverage in `golazo-copilot/tests/test_gcp_bootstrap.py`; focused pytest runs passed.
  - PASS: Automated tests cover workspace-default behavior, user-scope bootstrap behavior, and instruction resolution used by workflow preflight checks.
    - Evidence: targeted pytest suite and post-version-bump package test run passed.
- List of future work items:
  - Follow-up candidate: clean up the placeholder canonical capability registry entry that currently fails builder validation (`example-capability` -> `src/example.py`).
- Final status confirmation:
  - This work item is IMPLEMENTED. No open feature-scope blockers remain for GCP-0069.
