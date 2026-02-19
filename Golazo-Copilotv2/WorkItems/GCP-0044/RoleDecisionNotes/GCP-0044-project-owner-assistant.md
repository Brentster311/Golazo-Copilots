# GCP-0044 — Project Owner Assistant Decision Notes

## Decisions Made

### 1. No Decomposition Needed
Single user-observable outcome: tools reject calls without `workspace_path` instead of silently using `cwd`. The schema changes and code changes are all part of one deliverable.

### 2. Must-Ask Checklist — Pre-answered
- **Interface type**: MCP tool (Python library) — unchanged.
- **Target platform**: Cross-platform Python — unchanged.
- **Data persistence**: Files (state.json) — unchanged.

### 3. Chose "Required" Over "Smart Detection"
Three options were considered:
1. **Make `workspace_path` required** — chosen. Simple, correct, no heuristic risk.
2. **Persist workspace path at bootstrap time** — rejected. Adds complexity, requires a new config file, bootstrap might not always run first.
3. **Walk upward from cwd looking for markers** — rejected. Fragile, can match wrong workspace in monorepo setups.

### 4. Root Cause Analysis
The bug was observed in production: `gcp_create_workitem` was called without `workspace_path`, `Path.cwd()` resolved to `C:\Users\Brent` (the MCP server's process working directory), and state.json was created there. Subsequent calls with `workspace_path` looked in the correct workspace and couldn't find it. This is an MCP design characteristic — the server process cwd is not the user's workspace.

### 5. `gcp_status` Version-Only Mode
Could exempt version-only calls (no `work_item_id`) from requiring `workspace_path`. Chose consistency — require it always. The MCP client should always know which workspace it's operating in.

## Open Questions
None.
