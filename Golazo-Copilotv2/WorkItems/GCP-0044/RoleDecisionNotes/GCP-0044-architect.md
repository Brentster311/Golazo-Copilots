# GCP-0044 — Architect Decision Notes

## Architecture Decisions

### D1: Remove `Path.cwd()` fallback from `resolve_work_items_dir()`
- **Decision**: When `workspace_path` is `None` or empty, raise `ValueError` instead of falling back to `Path.cwd() / "WorkItems"`.
- **Rationale**: In MCP servers, `Path.cwd()` resolves to the server process's directory (e.g., `C:\Users\Brent`), NOT the user's VS Code workspace. This causes state files to be created in wrong directories with no recovery path.
- **Alternative Rejected**: Auto-detect workspace by walking up directory tree — fragile, MCP server CWD is unpredictable.

### D2: Make `workspace_path` required on all 6 tool schemas
- **Decision**: Move `workspace_path` into the `required` array for every tool in `list_tools()`.
- **Rationale**: MCP clients (e.g., Copilot) will always populate required fields from context. Optional fields may be silently omitted, causing the bug. Since we can't trust CWD, explicitness is the only safe approach.
- **Tools affected**: `gcp_create_workitem`, `gcp_transition`, `gcp_status`, `gcp_consent`, `gcp_bootstrap`, `gcp_capabilities`

### D3: Add validation guard in `call_tool()` for bootstrap and capabilities
- **Decision**: Add explicit `workspace_path` presence/non-empty validation in the `gcp_bootstrap` and `gcp_capabilities` handlers before passing to their function calls.
- **Rationale**: These two tools bypass `resolve_work_items_dir()` and do their own path resolution. Without explicit validation, a `None` value could still cause `Path.cwd()` fallback via `Path(None)` coercion or similar bugs.

### D4: No changes to tool function signatures
- **Decision**: Keep existing function signatures for `create_work_item()`, `transition()`, etc. unchanged.
- **Rationale**: The functions already accept workspace paths — the bug is in the MCP schema (not requiring the field) and the resolver (falling back silently). Fixing the entry point is sufficient.

## Capability Impact
- Only `mcp-server` capability directly affected (schema contract narrowed)
- No downstream capability dependencies impacted
