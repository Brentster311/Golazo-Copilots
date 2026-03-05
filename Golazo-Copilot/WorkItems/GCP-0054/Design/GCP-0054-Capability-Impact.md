# GCP-0054 Capability Impact — Rename MCP Tools from `gcp_` to `golazo_`

## Impact Analysis

**Files analyzed:** `server.py`, `tools/__init__.py`

### Directly Affected

| Capability | Description | Impact |
|---|---|---|
| **mcp-server** | MCP server entry point — registers all tools, routes calls, formats responses | Tool name strings change from `gcp_*` to `golazo_*`. No behavioral change. |

### Transitively Affected

None — tool names are terminal identifiers consumed by the MCP client (Copilot). No downstream capabilities depend on the string values of tool names.

### Contract Implications

- **Changed interfaces:** 7 MCP tool names rename (`gcp_status` → `golazo_status`, etc.)
- **No new interfaces.**
- **No removed interfaces** (same 7 tools, different names).
- **Breaking change** for any client referencing old `gcp_*` names (`.github/copilot-instructions.md` updated in same commit).

### Conclusion

Single capability affected. Pure rename, no contract structure changes. Low risk.
