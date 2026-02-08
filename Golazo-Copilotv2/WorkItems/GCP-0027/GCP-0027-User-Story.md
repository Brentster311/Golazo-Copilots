# GCP-0027: Remove gcp_mark_dor and gcp_mark_dod Tools

**Status**: IN PROGRESS

## User Story

**Title:** Remove DoR/DoD Marking Tools  
**As a:** Golazo Copilot user  
**I want:** The `gcp_mark_dor` and `gcp_mark_dod` tools removed from the MCP server  
**So that:** The workflow is simplified to use automatic output validation via role files instead of manual checklist marking

## Out of Scope
- Modifying the output validation logic (already implemented in GCP-0025)
- Changing role file format (already updated in GCP-0026)

## Assumptions
- **Assumption (explicit):** Existing work items with DoR/DoD state in state.json will continue to work - the state is preserved but the tools to update it are removed
- **Assumption (explicit):** The `gcp_status` output will be simplified to remove DoR/DoD checklist display

## Acceptance Criteria
1. [x] `gcp_mark_dor` tool is removed from the MCP server
2. [x] `gcp_mark_dod` tool is removed from the MCP server
3. [x] `gcp_mark.py` module is deleted
4. [x] Server.py no longer registers or handles these tools
5. [x] Tools __init__.py no longer exports these functions
6. [x] Tests for removed tools are deleted
7. [x] Bootstrap instructions updated to remove gcp_mark examples
8. [x] Version bumped to 2.100.0

## Non-Functional Requirements
- Breaking change: users upgrading from v2.x will lose access to these tools

## Telemetry / Metrics
- N/A

## Rollout / Rollback Notes
- Version 2.100.0 signals a significant change (removing 2 tools)
- No migration needed - state.json files remain valid, just the tools are gone
