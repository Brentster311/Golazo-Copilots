# GCP-0074 Design Document

## Summary

Align `golazo_transition_workitem` with the workflow's POA closure model. A work item is eligible for project-level finalization when it has returned from Retrospective to Project Owner Assistant, `closure_pending` is true, and required closure evidence is present.

## Problem Statement

The role workflow sets `closure_pending=true` when Retrospective transitions to POA, but project-level finalization accepts only work items whose current role is `retrospective`. Following the documented workflow therefore makes finalization fail.

## Business Case

This blocks reliable completion tracking and next-item sequencing. Correcting the precondition removes manual state edits and keeps workflow guidance consistent with runtime behavior. Success is measured by valid closure finalization passing, premature finalization remaining blocked, and retries not duplicating completed-item entries.

## Stakeholders

- Golazo Copilot workflow users
- Maintainers of workflow state and MCP tool contracts
- Contributors relying on project-level sequencing

## Functional Requirements

- Accept POA closure state only when `closure_pending` is true and retrospective was completed.
- Require the User Story status to be `IMPLEMENTED` and required POA closure artifacts to exist.
- Reject initial POA, incomplete retrospective, missing closure evidence, and other roles with actionable errors.
- Preserve exactly-once membership in `completed_work_items` and deterministic next-item calculation.
- Align MCP schema descriptions, role guidance, README, and tests with the same precondition.

## Non-Functional Requirements

- Preserve existing JSON schemas and atomic global-state writes.
- Do not require direct edits to work-item state.
- Maintain existing successful behavior where it remains compatible; return structured error codes for invalid states.
- Keep validation deterministic and cross-platform.

## Proposed Approach

1. Add a focused eligibility helper in `golazo_transition_workitem.py` that validates closure state, retrospective history, User Story status, and closure files.
2. Replace the retrospective-only role check with that helper.
3. Preserve global-state update and next-ID behavior after eligibility succeeds.
4. Update the MCP registry description and documentation to describe POA closure finalization.
5. Add focused tests for success, premature states, missing evidence, idempotency, and contract text.

## Alternatives Considered

- Finalize directly from Retrospective: rejected because it bypasses mandatory POA acceptance closure.
- Remove project-level finalization: rejected because global completion and next-item sequencing remain required.
- Add a new state schema field: rejected because `closure_pending` and role history already express the necessary lifecycle.

## Risks And Mitigations

- Forged `closure_pending` state could bypass Retrospective: require a completed retrospective role-history entry.
- Stale closure files could permit invalid completion: require current closure mode plus `IMPLEMENTED` status and both POA closure artifacts.
- Retry could mutate state repeatedly: preserve set-like completed-item behavior and return a clear already-completed result.
- Documentation drift could recur: add policy assertions for schema and README wording.

## Dependencies

- Existing work-item persistence and `WorkItemState.role_history`
- Existing POA closure artifacts and User Story status
- Existing atomic `global_state.json` persistence

## Migration, Rollout, And Rollback

No state migration is required. Existing properly closed work items become eligible immediately. Rollback restores the old precondition without rewriting work-item or global state, though it reintroduces the documented contradiction.

## Observability

Tool results expose success or a stable error code and actionable reason. Existing state history and `global_state.json` provide the audit trail. No external telemetry is added.

## Test Strategy

Use temporary work-item trees and focused async tests to cover valid POA closure, initial POA, missing retrospective history, missing closure artifact, non-implemented status, idempotent retries, and unchanged next-item behavior. Run the focused suite with coverage, then the full test suite and Ruff.
