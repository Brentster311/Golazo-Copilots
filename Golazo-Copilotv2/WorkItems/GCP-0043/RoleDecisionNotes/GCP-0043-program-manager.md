# GCP-0043 — Program Manager Decision Notes

## Design Decisions

### 1. Keep Pre-existing Safety Checks
Even though the new regex `^[A-Za-z]{1,4}-\d{3,}$` implicitly prevents empty strings, `.`, `..`, and overly long IDs, the explicit checks are retained because they provide more specific error messages. A user passing an empty string gets "Must not be empty" rather than the full format explanation.

### 2. Error Message Strategy
Error messages include both the pattern description in plain English and concrete examples. This eliminates the need for documentation — the error itself teaches the user the correct format.

### 3. Scope Limited to `gcp_create_workitem` Only
Other tools (`gcp_status`, `gcp_transition`) accept `work_item_id` but they read existing state. Validation at creation time is sufficient — you can't have an invalid ID in state if creation blocks it.

### 4. No Version Bump Needed for File Format
`state.json` and `WorkItemState` are not changing. Only the validation gate changes.

## Trade-offs
- Strictness vs. flexibility: We chose strict enforcement. The pattern is well-established across 40+ items and the error message makes recovery easy.
- Docs vs. code: We chose code-only enforcement. Dual-maintaining docs and code leads to drift.
