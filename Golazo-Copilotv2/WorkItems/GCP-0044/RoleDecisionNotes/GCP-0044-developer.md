# GCP-0044 — Developer Decision Notes

## Implementation Summary

### Changes Made

#### 1. `server.py` — `resolve_work_items_dir()` (L30-44)
- Removed `Path.cwd()` fallback when `workspace_path` is None/empty
- Now raises `ValueError("workspace_path is required — MCP servers cannot rely on cwd")` 

#### 2. `server.py` — `list_tools()` schema changes
- Added `"workspace_path"` to `required` array for all 6 tool schemas:
  - `gcp_create_workitem`: `["work_item_id", "workspace_path"]`
  - `gcp_transition`: `["work_item_id", "role", "workspace_path"]`
  - `gcp_status`: `["workspace_path"]`
  - `gcp_bootstrap`: `["workspace_path"]`
  - `gcp_consent`: `["work_item_id", "action", "reason", "workspace_path"]`
  - `gcp_capabilities`: `["action", "workspace_path"]`

#### 3. `server.py` — `call_tool()` / `_dispatch_tool()` refactoring
- Extracted tool dispatch logic into `_dispatch_tool()` (private)
- `call_tool()` wraps it in `try/except ValueError` for uniform error handling
- Added explicit `workspace_path` guards in `gcp_bootstrap` and `gcp_capabilities` handlers (they bypass `resolve_work_items_dir`)

### New Tests — `test_gcp044_workspace_path.py` (7 tests)
- TC1.1: Schema validation — all 6 tools require workspace_path
- TC2.1-2.3: Runtime validation — create_workitem, transition, bootstrap return error when workspace_path missing
- TC3.1-3.3: resolve_work_items_dir unit tests — None raises, empty raises, valid resolves correctly

### Test Results
- 7/7 new tests passing
- 136 unrelated tests passing (all tests excluding pre-existing GCP-0043 format failures)
- 48+ pre-existing failures in test_gcp_transition.py, test_gcp_status.py, test_gcp_consent.py, test_gcp012_backward.py (caused by GCP-0043 work item ID format enforcement — not related to this change)

### Design Decisions During Implementation
- Used `try/except ValueError` wrapper in `call_tool()` rather than per-handler guards for the 4 `resolve_work_items_dir` callers — DRY, catches any future ValueError-raising validators
- Kept explicit guards in bootstrap/capabilities handlers since they don't use `resolve_work_items_dir`
