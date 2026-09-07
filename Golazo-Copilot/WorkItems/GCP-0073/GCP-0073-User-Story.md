# GCP-0073 User Story

**Status**: BACKLOG

**User Story**
- Title: Migrate Golazo Copilot to MCP SDK 2.x
- As a: Golazo Copilot installer
- I want: Golazo Copilot to use the MCP 2.x server API and validate startup from a clean installation
- So that: current MCP dependencies install successfully without breaking server startup or the existing Golazo tool contract
- Out of scope: Pinning Golazo to MCP 1.x as the final solution; changing Golazo workflow behavior; adding or removing MCP tools; publishing a release.
- Assumptions:
  - **Assumption (explicit):** This is a Python MCP server and CI validation change with no new user interface.
  - **Assumption (explicit):** The package remains cross-platform on Windows, macOS, and Linux.
  - **Assumption (explicit):** MCP 2.x is the supported dependency line, expressed as `mcp>=2,<3`; smoke-test artifacts are ephemeral and do not add runtime persistence.
- Acceptance Criteria (bulleted, testable):
  - Golazo server registration, tool listing, and tool dispatch use supported MCP 2.x APIs without relying on removed `Server.list_tools` or equivalent MCP 1.x decorator behavior.
  - All existing Golazo MCP tools remain advertised with equivalent names, input schemas, result formatting, and workflow behavior after migration.
  - A clean-environment smoke test installs the built wheel with MCP 2.x, then imports and starts the installed server without compatibility failures.
  - Existing unit and integration tests pass against both the minimum supported and latest available MCP 2.x releases, and compatibility documentation records the supported range plus resolved Golazo and MCP versions on startup-test failure.
- Non-functional requirements: Declare `mcp>=2,<3` using valid PEP 440 dependency constraints so MCP 3.x requires an explicit compatibility release; keep validation cross-platform and deterministic; avoid duplicate legacy and modular registration paths where MCP 2.x provides one canonical integration surface; do not require Azure credentials after the artifact is available to the test environment.
- Telemetry / metrics expected: No external telemetry. CI records resolved package versions and startup success or failure.
- Rollout / rollback notes: Release as an MCP compatibility update only after minimum/latest MCP 2.x, clean-install, and full-regression validation pass. MCP 3.x adoption requires explicit compatibility validation and a new release. Roll back by restoring the last supported MCP 1.x package version and server integration together; do not retain a mixed API/dependency state.