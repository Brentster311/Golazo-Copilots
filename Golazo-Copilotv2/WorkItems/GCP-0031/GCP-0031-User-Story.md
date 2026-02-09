# GCP-0031: Remove DoR/DoD Checklist System

**Status**: BACKLOG

## User Story

- **Title:** Remove the Legacy DoR/DoD Checklist System
- **As a:** Golazo Copilot workflow user
- **I want:** The dead DoR/DoD checklist items, gate checks, and status rendering removed from the codebase
- **So that:** The workflow uses only the output validation system (Required Outputs in role files) without zombie checklist confusion

## Out of Scope
- Changing the output validation system (parse_required_outputs, validate_all_outputs)
- Adding new gate mechanisms
- Removing state.json entirely (only remove dor/dod fields from it)

## Assumptions
- **Assumption (explicit):** Interface type is MCP server (Python library), cross-platform, file-based persistence, technical users
- **Assumption (explicit):** The output validation system (GCP-0025/0026/0027) is the replacement and is working correctly
- **Assumption (explicit):** The `check_dor_gate` at developer transition can be replaced by the existing output validation gate in `gcp_transition`
- **Assumption (explicit):** `checklists.py` module can be deleted — it's only used for DoR/DoD rendering in `gcp_status.py`

## Acceptance Criteria
1. [ ] `state.json` schema no longer contains `dor` or `dod` fields for newly created work items
2. [ ] `gcp_status` output no longer shows "DoR: [...]" or "DoD: [...]" lines
3. [ ] `check_dor_gate` function and `DOR_GATE_ROLE` constant are removed from `transitions.py`
4. [ ] `gcp_transition` no longer calls `check_dor_gate` — the output validation gate is the only gate
5. [ ] `checklists.py` is deleted (no production imports remain)
6. [ ] `gcp_create_workitem` no longer initializes dor/dod checklist items in state
7. [ ] All existing tests pass (minus intentionally removed checklist tests), new tests added where needed

## Non-Functional Requirements
- Backward compatibility: existing state.json files with dor/dod fields should still load without errors (ignore extra fields)
- No new dependencies

## Telemetry / Metrics Expected
- N/A (local MCP server)

## Rollout / Rollback Notes
- Breaking change: state.json schema changes. Old state files should be tolerated (Pydantic model can use `Optional` or `model_config = ConfigDict(extra="ignore")`)
- Git revert cleanly undoes all changes
