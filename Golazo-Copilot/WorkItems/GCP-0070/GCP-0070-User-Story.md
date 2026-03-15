**Status**: IMPLEMENTED

**User Story**
- Title: Remove golazo_update and replace it with spine install guidance
- As a: Golazo Copilot maintainer
- I want: the `golazo_update` MCP tool removed and the orchestrator spine updated with clear `pip install` guidance from the correct package location
- So that: update/install behavior is handled explicitly through documented package installation steps instead of a state-changing MCP tool
- Out of scope:
  - Changing the Azure Artifacts package source itself
  - Redesigning bootstrap beyond the spine/install guidance needed for this change
  - Introducing a replacement MCP tool for package updates
- Assumptions:
  - Assumption (explicit): the relevant spine content is the bootstrapped orchestrator instructions content used to create `.github/agents/Golazo-Copilot.md`.
  - Assumption (explicit): the correct install location is the Azure Artifacts feed already documented in this repository for `golazo-copilot` package installation.
  - Assumption (explicit): removing `golazo_update` includes tool registration, dispatch, formatting, documentation, and tests that reference the tool.
- Acceptance Criteria (bulleted, testable):
  - The MCP server no longer advertises or dispatches a `golazo_update` tool in either modular or legacy paths.
  - Bootstrap-generated orchestrator instructions include clear `pip install` guidance for installing `golazo-copilot` from the correct package feed/location.
  - User-facing documentation is updated so update/install guidance no longer points users to `golazo_update`.
  - Automated tests cover tool removal and the new spine guidance behavior.
- Non-functional requirements:
  - Keep the change backward-safe for all remaining tools.
  - Keep install guidance explicit and consistent across the spine and public docs.
  - Remove dead code and dead tests related only to `golazo_update`.
- Telemetry / metrics expected:
  - No external telemetry changes are required.
  - Success is measured by absence of the removed tool in registration/dispatch outputs and presence of correct install guidance in generated instructions.
- Rollout / rollback notes:
  - Rollout: ship as a backward-incompatible tool-surface cleanup with updated bootstrap/documentation guidance.
  - Rollback: restore the removed tool registration, implementation, and tests if downstream workflows still require it.

## Closure

- Summary of what was delivered:
  - Removed the `golazo_update` MCP tool implementation, registration, dispatch handling, formatter support, and dedicated tests.
  - Added explicit `pip install --upgrade golazo-copilot --index-url ...` guidance to the bootstrap spine and README, tied to the MCP server's configured Python environment.
  - Updated regression coverage and verified the package still builds successfully.
- Acceptance criteria status:
  - PASS: The MCP server no longer advertises or dispatches a `golazo_update` tool in either modular or legacy paths.
  - PASS: Bootstrap-generated orchestrator instructions include clear `pip install` guidance for installing `golazo-copilot` from the correct package feed/location.
  - PASS: User-facing documentation is updated so update/install guidance no longer points users to `golazo_update`.
  - PASS: Automated tests cover tool removal and the new spine guidance behavior.
- Future work items:
  - Restore an orchestrator-accessible role transition wrapper so closure does not need a fallback execution path.
  - Remove or replace the placeholder `example-capability` entry so builder validation is actionable.
  - Refresh stale bootstrapped instruction files in a separate maintenance work item.
- Final status confirmation:
  - IMPLEMENTED. Code, tests, and packaging validation are complete for this work item.
