# GCP-0044 — Review Comments

## Design Review

### Verdict: **Approve with minor comments**

The design is well-scoped and addresses a real production bug. One file changes (`server.py`), no tool function signature changes.

---

### Comment 1: Exception Strategy in `resolve_work_items_dir`
The design proposes raising `ValueError`. This is fine, but the `call_tool()` handler must catch it consistently across all 4 tools that use it. Consider wrapping in a helper or catching at the top of `call_tool()` rather than in each individual branch.

### Comment 2: `gcp_status` Version-Only Mode
Currently `gcp_status` with no `work_item_id` returns just the version without resolving workspace. The design says to require `workspace_path` anyway for consistency. The handler currently has an early-return at L252-L255 before workspace resolution. Ensure the `workspace_path` validation happens after that early return, or accept that version-only calls also need `workspace_path`. The user story chose consistency — document this clearly in implementation.

### Comment 3: `gcp_bootstrap` and `gcp_capabilities` Handlers
These bypass `resolve_work_items_dir` entirely. The design says to add validation in their handlers. Good — but note that `gcp_bootstrap` already validates workspace via `_is_workspace()` internally, which returns a failure if the path doesn't exist. The change for bootstrap is mostly the schema `required` update + an explicit None check in the handler.

### Comment 4: MCP Schema Enforcement
Making `workspace_path` required in the JSON schema means MCP-compliant clients will reject the call before it even reaches the server. This is the correct approach — it's the first line of defense.

---

## Architect Notes

### Architectural Alignment: **Approved**
- Single file change (`server.py`), no new modules or contracts.
- Tool function signatures unchanged — the change is purely at the MCP routing layer.
- `ValueError` is appropriate for "missing required input" at the server layer.

### Security
- Removing `Path.cwd()` fallback eliminates the risk of accidental file creation in the user's home directory.

### Blast Radius
- Low. Only `server.py` changes. All tool functions are unaffected. Tests call functions directly.
