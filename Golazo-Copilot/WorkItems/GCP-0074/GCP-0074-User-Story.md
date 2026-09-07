# GCP-0074 User Story

**Status**: BACKLOG

**User Story**
- Title: Align project-level finalization with POA closure semantics
- As a: Golazo Copilot workflow user
- I want: project-level work-item finalization to accept a work item that has completed retrospective and returned to Project Owner Assistant closure
- So that: I can finalize completed work through the documented workflow without a contradictory role-precondition failure
- Out of scope: Changing the role sequence before retrospective; removing POA acceptance review; bypassing required closure artifacts; changing work-item profiles.
- Assumptions:
  - **Assumption (explicit):** The interface remains the existing `golazo_transition_workitem` MCP tool.
  - **Assumption (explicit):** Behavior remains cross-platform and persists through existing work-item and global-state JSON files.
  - **Assumption (explicit):** POA closure remains required for complete, express, and spike profiles.
- Acceptance Criteria (bulleted, testable):
  - `golazo_transition_workitem` accepts a work item in POA closure mode after retrospective when all closure outputs and status requirements are complete.
  - Finalization still rejects work items that have not completed retrospective or lack required POA closure evidence.
  - Successful finalization updates project-level state exactly once and remains idempotent or returns a clear already-finalized result on retry.
  - Tool schema, role instructions, README guidance, and tests describe one consistent finalization precondition.
- Non-functional requirements: Preserve state integrity and append-only audit history; never require direct `state.json` edits; maintain backward compatibility for valid callers; provide actionable failure messages.
- Telemetry / metrics expected: No external telemetry. Tool results and state history record finalization outcome and reason for rejection.
- Rollout / rollback notes: Ship with migration-free state compatibility. Rollback restores the previous precondition without rewriting existing work-item state.