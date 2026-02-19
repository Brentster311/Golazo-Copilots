# GCP-0044 — Quality Assurance Decision Notes

## Decisions

### 1. Design Approved
Clean, focused fix. Single file change addresses the root cause.

### 2. Test Strategy
Tests focus on the server layer (`resolve_work_items_dir` + `call_tool` handlers). Existing tool-function-level tests are unaffected because they pass `work_items_dir` directly — they never go through the server's resolution path.

### 3. Schema Test Added
TC1.1 programmatically verifies all 6 tool schemas. This prevents future tools from accidentally omitting `workspace_path` from `required`.
