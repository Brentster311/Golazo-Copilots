# GCP-0060 Design Document — Proposal-Gated Git Intent Capture for Workflow Auditability

## Summary
This work item introduces a proposal-only MCP tool, `golazo_git_propose`, to capture intent for significant git actions (`add`, `commit`, `push`, `branch`) before repository-changing operations occur. Proposal records are persisted to the active work item state under `git_actions` as append-only history. The scope is auditability and deterministic validation only; no direct git execution or external approval systems are included.

## Problem Statement
- Significant git intents are not consistently captured in a structured, reviewable audit trail.
- Auditors and project owners need durable evidence that intent was recorded prior to downstream repository-changing operations.
- Without deterministic validation and persistence semantics, proposal data quality is inconsistent and difficult to govern.

## Business Case
### Why now
- Workflow governance requirements now require explicit, reviewable intent capture for significant git actions.
- This creates a prerequisite for stronger change-control posture without introducing a heavyweight approval platform.

### Impact
- Improves audit readiness by storing action proposals in work-item state.
- Increases reviewer confidence by making intent visible before downstream git actions.
- Reduces ambiguity through deterministic, action-specific parameter validation errors.

### KPIs
- Proposal volume by action type (`add`, `commit`, `push`, `branch`).
- Proposal validation error rate by rule (`missing message`, `missing branch`, etc.).
- Ratio of downstream git operations that have a prior proposal entry.
- Successful proposal persistence rate across load/save round-trips.

## Stakeholders
- Project Owner: needs policy-aligned intent visibility.
- Workflow auditors/compliance reviewers: require durable traceability.
- Developers and AI agents: create proposals through MCP tooling.
- On-call maintainers: troubleshoot proposal validation/persistence failures.

## Requirements
### Functional Requirements
1. Provide MCP tool `golazo_git_propose` that writes proposal records to the active work item.
2. Initialize `git_actions` safely to an empty list when absent, preserving schema-valid state.
3. For `action="add"`, persist one proposal record containing at least action, status, timestamp, and files.
4. For `action="commit"`, reject requests missing `message` with deterministic parameter-required error.
5. For `action="push"` and `action="branch"`, reject requests missing `branch` with deterministic parameter-required error.
6. Return clear not-found/create guidance when target work item does not exist.
7. Preserve proposal records across load/save round-trips.
8. Maintain append-only behavior for `git_actions` history.

### Non-Functional Requirements
1. Proposal creation remains lightweight and interactive for MCP usage.
2. Validation outcomes are deterministic and action-specific.
3. State persistence is backward compatible for work items created before `git_actions` existed.
4. File persistence behavior is cross-platform, validated on Windows-first workspace context.

## Proposed Approach
### High-Level Plan
1. Extend state schema/defaults to include `git_actions: []` for backward-compatible read/write operations.
2. Add `golazo_git_propose` MCP tool handler with action routing and parameter validation.
3. Create normalized proposal record shape (`action`, `status`, `timestamp`, contextual fields such as `files`, `message`, `branch`).
4. Append proposal record to `git_actions` and persist via existing work-item state save path.
5. Standardize error contracts for missing required parameters and missing work item.
6. Add tests covering initialization, action-specific validation failures, persistence round-trips, and missing-work-item behavior.

### Data Contract (State)
- `git_actions`: list of proposal records (default empty list).
- Proposal record fields (minimum):
  - `action`: one of `add|commit|push|branch`
  - `status`: proposal status value (for this scope, creation state)
  - `timestamp`: creation timestamp
  - Action-specific payload:
    - `files` for `add`
    - `message` for `commit`
    - `branch` for `push|branch`

## Alternatives Considered
1. Execute git operations directly from `golazo_git_propose`.
   - Rejected: out of scope; user story explicitly limits to intent capture.
2. Persist proposal records in external DB/cloud store.
   - Rejected: conflicts with assumption and existing workflow state model centered on `state.json`.
3. Capture free-form proposal text without action-specific validation.
   - Rejected: fails deterministic, testable acceptance criteria and weakens audit quality.

## Risks, Mitigations, Open Questions
### Risks
1. Developers bypass proposal tool and perform downstream git actions without prior intent capture.
2. Timestamp/record formatting inconsistency across environments may hinder audit analysis.
3. State write failures could drop proposal records during intermittent filesystem issues.
4. Backward-compatibility regressions if defaults are not consistently applied on load/save paths.

### Mitigations
1. Surface KPI for prior-proposal ratio and track compliance drift.
2. Use normalized record schema and deterministic serialization rules.
3. Fail fast with clear persistence errors; avoid partial/ambiguous success reporting.
4. Add regression tests for legacy work items missing `git_actions`.

### Open Questions
- Non-blocking: Should proposal status taxonomy expand beyond initial creation state in a future work item (e.g., approved/rejected/executed linkage)?

## Dependencies
- Work-item state load/save utilities and schema/default application.
- MCP server tool registration/dispatch infrastructure.
- Existing test framework for MCP tool behavior and state persistence.
- Documentation surfaces for tool contracts and error semantics.

## Migration / Rollout / Rollback Plan
### Migration
- No data migration required.
- Legacy work items gain `git_actions` lazily via defaults during first relevant load/save path.

### Rollout
1. Release state default/schema update and `golazo_git_propose` together.
2. Ship acceptance-test coverage for all required scenarios.
3. Announce contract: proposal capture only (no git execution).

### Rollback
1. Disable/remove MCP tool registration if severe issues arise.
2. Preserve existing `git_actions` data in `state.json` (no destructive rollback of stored history).
3. Revert handler/schema changes while retaining backward-readable state files.

## Observability Plan
- Emit structured events/log lines for proposal attempts with action type and outcome.
- Capture validation failure category metrics (`missing_message`, `missing_branch`, `workitem_not_found`).
- Track append success/failure counts for `git_actions` persistence.
- Operational view for on-call:
  - Error spike alerts for persistence failures.
  - Trend chart for proposal volume by action.
  - Compliance proxy metric for downstream operations with prior proposal records.

## Test Strategy Summary
1. Initialize `git_actions` on first propose call for legacy state lacking field.
2. Verify `add` proposal persistence includes required fields and files payload.
3. Verify `commit` without `message` returns deterministic parameter-required error.
4. Verify `push`/`branch` without `branch` returns deterministic parameter-required error.
5. Verify missing work item returns clear not-found/create guidance.
6. Verify persisted proposals survive load/save round-trips with append-only behavior.
7. Regression test state compatibility for unrelated workflow tools reading/writing `state.json`.
