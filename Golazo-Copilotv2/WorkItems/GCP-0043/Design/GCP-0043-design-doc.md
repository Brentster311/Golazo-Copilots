# GCP-0043 — Design Doc: Enforce Work Item ID Format in `gcp_create_workitem`

## Summary
Move the work item ID format validation from documentation in `project-owner-assistant.md` into the `validate_work_item_id()` function in `core/state.py`, and remove the now-redundant documentation section from the role file.

## Problem Statement
The work item ID format `^[A-Za-z]{1,4}-\d{3,}$` is currently documented in the Project Owner Assistant role file but not enforced by the `gcp_create_workitem` tool. The tool's current validation (`^[a-zA-Z0-9_-]+$`) accepts any alphanumeric string with hyphens/underscores, meaning IDs like `feature-x`, `my_task_1`, or `valid-id_123` are accepted despite violating the convention. Enforcement relies entirely on the AI agent reading and following documentation.

## Business Case
- **Why now**: As the number of work items grows (40+), inconsistent naming creates confusion and makes tooling harder to build on top of. Enforcing at the tool level provides a single source of truth.
- **Impact**: Low-risk improvement — all 40+ existing work items already follow the pattern.
- **KPIs**: Zero invalid-format work item IDs created after deployment.

## Stakeholders
- Golazo Copilot users (affected by stricter validation)
- Golazo Copilot maintainers (code change)

## Functional Requirements
1. `validate_work_item_id()` must reject IDs not matching `^[A-Za-z]{1,4}-\d{3,}$`.
2. Error messages must include the expected pattern and examples (e.g., `GCP-0001`, `AB-001`).
3. Existing safety checks (empty, `.`, `..`, too long) must remain.
4. The "Work Item ID Format Requirements" section must be removed from `project-owner-assistant.md`.

## Non-Functional Requirements
- Error messages must be actionable: include both pattern and examples.
- No changes to `WorkItemState` model or persistence format.
- All existing tests must be updated to use pattern-compliant IDs.

## Proposed Approach (High Level)

### Step 1: Update `validate_work_item_id()` in `core/state.py`
- Replace the generic regex `^[a-zA-Z0-9_-]+$` with `^[A-Za-z]{1,4}-\d{3,}$`.
- Keep the existing checks for empty, `.`/`..`, and length > 100 (though the new pattern implicitly prevents most of those, the explicit checks provide clearer error messages).
- Return a descriptive error: `"Invalid work item ID '<id>'. Must match pattern: 1-4 letters, dash, 3+ digits (e.g., GCP-0001, AB-001)."`

### Step 2: Update `server.py` tool description
- Update the `work_item_id` parameter description to mention the required format.

### Step 3: Remove format documentation from `project-owner-assistant.md`
- Delete the "Work Item ID Format Requirements" subsection (lines 11–14 and the heading).

### Step 4: Update tests in `test_gcp_create_workitem.py`
- Change test IDs from free-form (`valid-id_123`) to pattern-compliant (`VAL-123`).
- Add new test cases for format-specific rejections (e.g., `feature-x`, `ABCDE-001`, `GCP-12`).
- Add new test cases for format-specific acceptances (e.g., `A-000`, `TEST-9999`).

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|---|---|---|---|
| Keep validation in docs only | No code change | Relies on AI compliance; inconsistent | Rejected |
| Validate in both docs and code | Defense in depth | Dual maintenance burden | Rejected |
| Validate only in code (chosen) | Single source of truth, enforced | Slightly less visible to users | **Chosen** — error message compensates for visibility |

## Risks, Mitigations, Open Questions

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Existing tests break | Certain | Low | Update test IDs as part of this change |
| Users accustomed to free-form IDs | Low | Low | All existing IDs already follow pattern; error message guides correction |
| Other tools (gcp_status, gcp_transition) accept old IDs | N/A | N/A | Out of scope — those tools read existing state, don't create new IDs |

**Open Questions**: None.

## Dependencies
- None. This is a self-contained change in the `golazo-copilot` package.

## Affected Capabilities (from registry)
- **Directly**: `tool-create-workitem`, `role-loader`
- **Transitively**: `tool-transition`, `tool-status`, `tool-bootstrap`, `mcp-server`

## Migration / Rollout / Rollback Plan
- **Migration**: None needed — all existing work items already comply.
- **Rollout**: Deploy as part of next version bump.
- **Rollback**: Revert `validate_work_item_id()` regex to `^[a-zA-Z0-9_-]+$` and restore the POA doc section.

## Observability Plan
- No telemetry changes. Validation errors are returned directly to the caller.

## Test Strategy Summary
- **Unit tests**: Update existing tests + add new cases for format validation (valid and invalid).
- **Integration test**: Verify end-to-end that `gcp_create_workitem` rejects bad IDs and accepts good ones.
- **Regression**: Ensure all other tool tests still pass (gcp_status, gcp_transition, etc.).
