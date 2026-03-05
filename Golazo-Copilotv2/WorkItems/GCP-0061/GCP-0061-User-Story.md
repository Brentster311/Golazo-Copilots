**Status**: IMPLEMENTED

**User Story**
- Title: Project-level work-item completion handoff with next-item sequencing
- As a: Program Manager
- I want: to mark a retrospective-complete work item as finished and set the next work item automatically
- So that: project flow continues with clear sequencing and minimal manual coordination
- Out of scope:
  - Auto-creation of the next work item
  - Priority-based scheduling logic beyond sequential next-ID suggestion
  - Integration with external portfolio planning systems
- Assumptions:
  - Assumption (explicit): This feature is implemented via MCP tool `golazo_transition_workitem`.
  - Assumption (explicit): Workspace-level project state is persisted in `global_state.json`.
- Acceptance Criteria (bulleted, testable):
  - Given a work item currently at `retrospective`, when `golazo_transition_workitem` is called, then it succeeds and returns completed ID plus computed next ID.
  - Given a work item not at `retrospective`, when the tool is called, then it fails with a role-precondition error.
  - Given missing `global_state.json`, when transition succeeds, then `global_state.json` is created with required schema metadata and `next_work_item`.
  - Given existing `global_state.json`, when transition succeeds, then the current item is marked `completed` and `next_work_item` is updated.
  - Given the computed next work item does not exist, when transition succeeds, then the response explicitly instructs creating it via work-item creation flow.
- Non-functional requirements:
  - Transition operation must be idempotent-safe for repeated calls on unchanged state.
  - Global state writes must be atomic enough to avoid partial JSON corruption in normal execution.
  - Message output must clearly distinguish success, precondition failure, and next-item existence status.
- Telemetry / metrics expected:
  - Count of successful project-level transitions
  - Rate of precondition failures (non-retrospective role)
  - Percentage of transitions where next work item already exists
- Rollout / rollback notes:
  - Rollout as additive tool; no breaking change to existing per-work-item flow.
  - Rollback by removing tool exposure while keeping `global_state.json` ignored by existing workflows.

## Closure
- Summary of what was delivered:
  - Implemented MCP tool `golazo_transition_workitem` for project-level completion handoff and next-item sequencing.
  - Added workspace-level persistence in `global_state.json` with atomic writes and schema-safe initialization.
  - Wired tool registration, dispatch, and output formatting; updated README and contract-parity tests.
- Acceptance criteria pass/fail status:
  - AC1 (retrospective success + computed next ID): PASS
  - AC2 (non-retrospective role precondition failure): PASS
  - AC3 (create missing `global_state.json` with metadata + next item): PASS
  - AC4 (update existing `global_state.json` with completion + next item): PASS
  - AC5 (guide create-work-item when next does not exist): PASS
- List of future work items (if any):
  - Optional: add explicit telemetry emission for transition success/failure categories.
  - Optional: add branch-level integration test coverage for global-state lifecycle under merged-history scenarios.
- Final status confirmation:
  - This user story is implemented and validated by focused regression tests.
