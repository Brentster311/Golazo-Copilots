**Status**: IMPLEMENTED

**User Story**
- Title: Proposal-gated git intent capture for workflow auditability
- As a: Project Owner and workflow auditor
- I want: every significant git action to be proposed and recorded in the active work item
- So that: we have a reviewable trail of intent before repository-changing operations occur
- Out of scope:
  - Direct execution of git actions
  - External approval UI/workflow systems
  - Remote provider policy enforcement
- Assumptions:
  - Assumption (explicit): Interface type is MCP tool interaction (not CLI/GUI/web), because the request is tool/workflow-centric and no separate interface requirement was provided.
  - Assumption (explicit): Target platform is cross-platform file-system behavior with Windows validation first, because workspace execution is on Windows and no platform restriction was provided.
  - Assumption (explicit): Data persistence is work-item file persistence in `state.json` (no external DB/cloud state), because the request centers on workflow-state auditability.
  - Assumption (explicit): This feature is implemented as MCP tool `golazo_git_propose` operating on active work item state.
  - Assumption (explicit): Proposal records are stored under `git_actions` and schema-default to an empty list for backward-compatible load/save round-trips.
- Acceptance Criteria (bulleted, testable):
  - Given a work item without `git_actions`, when `golazo_git_propose` is first called, then proposal history is initialized safely and state remains schema-valid.
  - Given an existing work item, when `golazo_git_propose(action="add")` is called with files, then one proposal record is persisted with action, status, timestamp, and files.
  - Given an existing work item, when `golazo_git_propose(action="commit")` is called without `message`, then the call fails with a deterministic parameter-required error.
  - Given an existing work item, when `golazo_git_propose(action="push")` or `golazo_git_propose(action="branch")` is called without `branch`, then the call fails with a deterministic parameter-required error.
  - Given either a non-existent work item or a successful proposal write, when state is loaded/saved by workflow tools, then failures return a clear not-found/create guidance and successful records persist in `git_actions` across round-trips.
- Non-functional requirements:
  - Proposal creation must be lightweight and return in interactive MCP latency bounds.
  - Error messages must be action-specific and deterministic.
  - State changes must be append-only for proposal history integrity.
- Telemetry / metrics expected:
  - Count of proposals by action type (`add`/`commit`/`push`/`branch`)
  - Proposal error rate by validation rule
  - Ratio of downstream git operations with prior proposal record
- Rollout / rollback notes:
  - Rollout behind normal package release; no migration blocker if `git_actions` defaults to empty list.
  - Rollback by disabling/removing tool registration while preserving existing state fields for backward compatibility.

## Closure

### Delivery summary
- Implemented `golazo_git_propose` MCP tool with deterministic validation and append-only proposal persistence.
- Added `git_actions` typed state field for schema-safe round-trips and backward compatibility.
- Added/updated tests for tool behavior and server dispatch coverage.
- Updated documentation to reflect supported tool contract.

### Acceptance criteria validation
- AC1 (initialize missing `git_actions` safely): **PASS**
- AC2 (`add` persists proposal record): **PASS**
- AC3 (`commit` without `message` fails deterministically): **PASS**
- AC4 (`push`/`branch` without `branch` fail deterministically): **PASS**
- AC5 (not-found guidance + persistence across round-trips): **PASS**

### Future work items
- Extract and modularize `golazo-copilot/src/golazo_copilot/server.py` to reduce coupling and improve maintainability (no behavior change).

### Final status
- Work item implemented and validated in complete profile closure flow.
