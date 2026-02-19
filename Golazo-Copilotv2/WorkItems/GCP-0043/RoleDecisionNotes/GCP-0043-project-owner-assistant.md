# GCP-0043 — Project Owner Assistant Decision Notes

## Decisions Made

### 1. Single Story (No Decomposition Needed)
The request has one user-observable outcome: invalid work item IDs are rejected at creation time. The code change (enforce pattern in `validate_work_item_id`) and the doc change (remove redundant section from POA) are both part of delivering that single outcome. No decomposition required.

### 2. Must-Ask Checklist — Pre-answered by Context
All three must-ask items are already determined by the existing codebase:
- **Interface type**: MCP tool (Python library consumed by MCP server) — unchanged.
- **Target platform**: Cross-platform Python — unchanged.
- **Data persistence**: Files (state.json) — unchanged.

No user clarification was needed.

### 3. Pattern Chosen: `^[A-Za-z]{1,4}-\d{3,}$`
This is the exact pattern already documented in `project-owner-assistant.md`. It was chosen because:
- All 40+ existing work items already follow it.
- It balances flexibility (any 1–4 letter prefix) with structure (numeric suffix for ordering).
- `WIP-000` (the default fallback) is valid under this pattern.

### 4. Scope Boundary: Only `gcp_create_workitem`
Validation is only added to the create tool. Other tools (`gcp_status`, `gcp_transition`) that accept `work_item_id` are not changed because they need to work with any existing state, and those IDs were already validated at creation time.

### 5. Removing POA Documentation Section
The "Work Item ID Format Requirements" section (lines 11–14 of `project-owner-assistant.md`) becomes redundant once the tool enforces the pattern. Keeping it would create dual-maintenance risk. The error message from the tool will serve as the authoritative format reference.

## Open Questions
None.
