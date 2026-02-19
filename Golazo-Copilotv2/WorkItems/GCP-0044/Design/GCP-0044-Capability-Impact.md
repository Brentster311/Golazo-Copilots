# GCP-0044 — Capability Impact Analysis

## Impact Analysis Results

Ran `gcp_capabilities(action="impact", files=["golazo-copilot/src/golazo_copilot/server.py"])`

## Directly Affected Capabilities

### 1. `mcp-server`
- **Contract**: Registers tools via `list_tools()`, routes calls via `call_tool()`, formats responses
- **Change**: `workspace_path` moves from optional to required in all 6 tool schemas. `resolve_work_items_dir()` no longer accepts None.
- **Contract implication**: Breaking change to MCP tool input schemas (narrower accepted inputs).

## Transitively Affected Capabilities
None directly — `mcp-server` has no downstream capability dependents in the registry. All tool functions are called by the server but their contracts are unchanged.

## Summary
- **One schema contract narrowed**: `workspace_path` optional → required on all 6 tools
- **One function contract narrowed**: `resolve_work_items_dir(None)` now raises instead of falling back
- **No tool function contracts changed**: `gcp_create_workitem`, `gcp_transition`, etc. still accept the same parameters
