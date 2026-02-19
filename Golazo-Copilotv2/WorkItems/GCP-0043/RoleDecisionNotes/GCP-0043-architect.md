# GCP-0043 — Architect Decision Notes

## Decisions Made

### 1. Architecture Approved — Minimal Surface Change
The change is isolated to a single validation function (`validate_work_item_id`) and a single documentation file. No new modules, classes, or interfaces are introduced. This is the smallest possible architectural footprint.

### 2. Recommend `re.fullmatch()` Over `re.match()` with `$`
The current code uses `re.match(r'^...+$', ...)`. While functionally equivalent to `re.fullmatch()`, using `fullmatch()` makes the intent clearer: "the entire string must match." This is a style recommendation for the developer, not a blocker.

### 3. No Contract Breaking Changes
The `validate_work_item_id()` function signature and return type are unchanged. The `gcp_create_workitem()` return schema is unchanged. Only the acceptance domain of the `work_item_id` input narrows — which is the safe direction (rejects more, not less).

### 4. No Capability Registry Changes Needed
The `capabilities.yaml` entries for `tool-create-workitem` and `role-loader` don't need updating since no public interface contracts change. The description in `server.py` should be updated to mention the format — this is documentation, not a contract change.

### 5. Transitive Impact is Pass-Through Only
All 4 transitively affected capabilities (tool-transition, tool-status, tool-bootstrap, mcp-server) are unaffected in their contracts. They either read state (unchanged schema) or copy files (updated content passes through).
