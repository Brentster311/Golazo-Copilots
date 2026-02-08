# GCP-0025: Replace DoR/DoD Marking with Role-Based Output Validation

**Status**: IMPLEMENTED

## User Story

- **Title**: Replace DoR/DoD Marking with Role-Based Output Validation
- **As a**: Golazo Copilot user (AI agent)
- **I want**: Role transitions to automatically validate required outputs instead of manually marking DoR/DoD items
- **So that**: The workflow has less friction, fewer infinite loops, and validation is based on actual file/artifact existence rather than agent claims

## Out of Scope

- Removing role notes requirement (still required before transition)
- Changing the role sequence
- Adding new roles
- Real-time file watching or hooks

## Assumptions

- **Assumption (explicit)**: Role files will define required outputs in a parseable format (markdown section with specific syntax)
- **Assumption (explicit)**: All required outputs can be validated by checking file existence, git state, or simple command execution
- **Assumption (explicit)**: Backward compatibility with existing state.json files is not required (breaking change acceptable for v3.0.0)

## Acceptance Criteria

1. [ ] `gcp_mark_dor` tool is removed from the MCP server (deferred to Phase 3)
2. [ ] `gcp_mark_dod` tool is removed from the MCP server (deferred to Phase 3)
3. [x] `gcp_transition` validates required outputs defined in the CURRENT role file before allowing transition
4. [x] `gcp_status` shows current role's required outputs and their validation status (exists ✓ / missing ✗)
5. [x] Role files have a `## Required Outputs` section with parseable format for validation rules
6. [x] Transition is blocked with clear error message when required outputs are missing
7. [x] `gcp_consent` can force bypass missing outputs (with deviation recorded)

## Non-Functional Requirements

- Transition validation should complete in < 2 seconds
- Error messages must clearly indicate which outputs are missing and expected path/format
- Must maintain 100+ tests passing

## Telemetry / Metrics Expected

- None (local MCP server)

## Rollout / Rollback Notes

- This is a **breaking change** to the MCP API (v3.0.0)
- Existing workspaces will need to update copilot-instructions.md
- State.json files will no longer have dor/dod fields (migration: ignore old fields)
