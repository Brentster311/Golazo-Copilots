# GCP-0043 — Enforce Work Item ID Format in `gcp_create_workitem` Tool

**Status**: IMPLEMENTED

**User Story**
- **Title**: Enforce Work Item ID Format in `gcp_create_workitem` Tool
- **As a**: Golazo Copilot user
- **I want**: the `gcp_create_workitem` tool to reject work item IDs that don't match the required naming pattern (`^[A-Za-z]{1,4}-\d{3,}$`)
- **So that**: ID format consistency is enforced at creation time by the tool itself, rather than relying on the AI agent to read and follow documentation conventions in the project-owner-assistant role file.

- **Out of scope**:
  - Retroactively validating or renaming existing work items that don't match the pattern.
  - Changing validation in any other tool (e.g., `gcp_status`, `gcp_transition`).
  - Auto-suggesting or auto-incrementing the next available ID.

- **Assumptions**:
  - **Assumption (explicit)**: The existing pattern `^[A-Za-z]{1,4}-\d{3,}$` (1–4 letters, dash, 3+ digits) is the correct and complete specification. No additional format constraints are needed. *(This is already documented in the POA role file and has been the convention throughout the project.)*
  - **Assumption (explicit)**: The `WIP-000` fallback ID referenced in the POA role file should still be valid since it matches the pattern. *(WIP matches 1–4 letters, 000 matches 3+ digits.)*
  - **Assumption (explicit)**: Existing tests that use free-form IDs like `"valid-id_123"` will need to be updated to use pattern-compliant IDs. *(Changing validation necessarily breaks tests that rely on the old, looser validation.)*

- **Acceptance Criteria (bulleted, testable)**:
  - Given a work item ID that does not match `^[A-Za-z]{1,4}-\d{3,}$`, when `gcp_create_workitem` is called, then it returns a clear error message stating the expected format with examples.
  - Given a work item ID that matches the pattern (e.g., `GCP-0001`, `AB-001`, `TEST-1234`), when `gcp_create_workitem` is called, then it succeeds as before.
  - The "Work Item ID Format Requirements" section (lines 11–14) is removed from `project-owner-assistant.md`, since the tool now enforces the format.
  - All existing and new unit tests pass, including tests for both valid and invalid ID formats.

- **Non-functional requirements**:
  - Error messages must include the expected pattern and at least two examples of valid IDs.
  - No breaking changes to the `WorkItemState` model or file persistence format.

- **Telemetry / metrics expected**:
  - None (internal tooling change).

- **Rollout / rollback notes**:
  - This is a breaking change for users who relied on free-form IDs. Since all existing work items already follow the pattern, risk is low.
  - Rollback: revert `validate_work_item_id()` to the previous regex and restore the POA documentation section.
