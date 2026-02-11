# GCP-0033: Guard Against Incomplete Work Items

**Status**: IMPLEMENTED

## User Story

- **Title:** Track and Display Work Item Completion Status
- **As a:** Golazo Copilot workflow user
- **I want:** `gcp_status` to show which roles have been visited and whether the work item reached completion
- **So that:** I can detect work items that were abandoned mid-workflow and know what still needs to be done

## Out of Scope
- Auto-completing stalled work items
- Notifications or alerts
- Enforcing completion order (already handled by transition validation)

## Assumptions
- **Assumption (explicit):** Interface type is MCP server (Python library), cross-platform, file-based persistence, technical users
- **Assumption (explicit):** Role history in state.json already tracks which roles have been entered/exited
- **Assumption (explicit):** "Complete" means the retrospective role has been exited (all roles visited)

## Acceptance Criteria
1. [ ] `gcp_status` output includes a "Role Progress" section showing which roles have been completed
2. [ ] Roles that have been entered and exited show as complete
3. [ ] The current role shows as in-progress
4. [ ] Roles not yet visited show as pending
5. [ ] A summary line indicates overall completion percentage (e.g., "6/9 roles complete")

## Non-Functional Requirements
- Display only, no blocking behavior
- No new dependencies

## Telemetry / Metrics Expected
- N/A

## Rollout / Rollback Notes
- Additive change, no breaking impact
- Uses existing role_history data, no schema changes
