# GCP-0044 — Program Manager Decision Notes

## Decisions Made

### 1. `ValueError` in `resolve_work_items_dir`
Chose to raise a `ValueError` rather than return a tuple. The function currently returns a `Path` — making it return an error tuple would change the contract for all callers. The `call_tool()` handler catches the exception and converts it to a user-friendly error response.

### 2. Schema-Level Enforcement
Adding `workspace_path` to the `required` array means MCP-compliant clients will enforce it before the call reaches the server. This is defense-in-depth: schema validation + runtime validation.

### 3. No Changes to Tool Functions
The tool functions (`gcp_create_workitem`, `gcp_transition`, etc.) already accept explicit `work_items_dir: Path` parameters. The server layer is the only place where `workspace_path` string → `Path` resolution happens. This means the fix is entirely in `server.py`.

### 4. `gcp_bootstrap` and `gcp_capabilities` Special Handling
These two tools don't use `resolve_work_items_dir` — they pass `workspace_path` directly to their functions. The fix for these is simpler: validate that `workspace_path` is not None/empty in the handler before calling the function.
