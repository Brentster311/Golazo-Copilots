# GCP-0044 — Make `workspace_path` Required on All MCP Tools

**Status**: IMPLEMENTED

**User Story**
- **Title**: Make `workspace_path` required on all MCP tools
- **As a**: Golazo Copilot user working in a workspace that is not the MCP server's working directory
- **I want**: all MCP tools to require `workspace_path` so that work items are always created and resolved in the correct workspace
- **So that**: work items, state files, and output files never silently land in the wrong directory (e.g., `C:\Users\<user>\WorkItems\` instead of the actual project workspace).

- **Out of scope**:
  - Changing how `gcp_bootstrap` or `gcp_capabilities` internally resolve paths (they already accept `workspace_path`).
  - Adding workspace auto-detection heuristics (walk-up search for markers).
  - Persisting workspace path in a config file for auto-resolution.

- **Assumptions**:
  - **Assumption (explicit)**: The MCP client (VS Code / Copilot) is capable of passing `workspace_path` on every tool call. *(The MCP schema already defines the parameter; the issue is that it's optional and the fallback `Path.cwd()` is unreliable.)*
  - **Assumption (explicit)**: Making `workspace_path` required is a breaking change for callers that currently omit it, but this is the correct fix — the `Path.cwd()` fallback is fundamentally broken for MCP servers whose process cwd differs from the user's workspace. *(Observed in production: work items created at `C:\Users\Brent` instead of the intended project directory.)*
  - **Assumption (explicit)**: `gcp_status` with no `work_item_id` (version-only mode) still needs `workspace_path` since the version response is workspace-independent, but consistency is preferred. *(Alternative: exempt version-only calls. Choosing consistency.)* 

- **Acceptance Criteria (bulleted, testable)**:
  - All 6 MCP tool schemas in `list_tools()` include `workspace_path` in their `required` array.
  - When any tool is called without `workspace_path`, it returns a clear error message (not a silent fallback to `cwd`).
  - `resolve_work_items_dir()` no longer falls back to `Path.cwd()` — it raises/returns an error if `workspace_path` is `None`.
  - All existing tests continue to pass (they call tool functions directly with explicit paths, bypassing the server layer).

- **Non-functional requirements**:
  - Error message for missing `workspace_path` must be actionable (e.g., "workspace_path is required. Provide the workspace root path.").

- **Telemetry / metrics expected**:
  - None.

- **Rollout / rollback notes**:
  - Breaking change for any MCP client that omits `workspace_path`. Existing VS Code + Copilot configurations that pass it will be unaffected.
  - Rollback: revert `required` arrays and restore `Path.cwd()` fallback in `resolve_work_items_dir`.
