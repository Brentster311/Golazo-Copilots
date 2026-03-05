# GCP-0060 Test Cases

## Test Strategy (TDD-First)
- Define and approve these tests before production changes for `golazo_git_propose`.
- Use deterministic assertions on response contracts and persisted state shape.
- Treat state persistence as authoritative evidence for proposal history integrity.

## Coverage Matrix (Acceptance Criteria -> Tests)
- AC1 (initialize missing `git_actions`) -> TC-001, TC-002
- AC2 (`add` proposal persists required fields) -> TC-003, TC-004
- AC3 (`commit` without `message` fails deterministically) -> TC-005
- AC4 (`push`/`branch` without `branch` fails deterministically) -> TC-006, TC-007
- AC5 (missing work item guidance + round-trip persistence) -> TC-008, TC-009, TC-010

## Test Cases

### TC-001 Legacy State Initialization on First Propose
- **Type**: Functional / Backward Compatibility
- **Preconditions**:
  - Existing work item state lacks `git_actions` field.
- **Steps**:
  1. Call `golazo_git_propose(action="add", files=["a.txt"])`.
  2. Reload state from disk.
- **Expected Outcome**:
  - Call succeeds.
  - `git_actions` is created as a list.
  - Exactly one proposal record is present.
- **Explicit Failure Message**:
  - `Expected legacy state to initialize 'git_actions' as list on first proposal.`

### TC-002 Schema-Valid Round-Trip After Initialization
- **Type**: Reliability / Persistence
- **Preconditions**:
  - State initially missing `git_actions`.
- **Steps**:
  1. Execute successful proposal call.
  2. Save and reload using standard workflow load/save utility path.
  3. Validate required state keys and `git_actions` type.
- **Expected Outcome**:
  - Reloaded state remains schema-valid.
  - No data loss in newly created proposal record.
- **Explicit Failure Message**:
  - `Expected schema-valid state after load/save round-trip with initialized 'git_actions'.`

### TC-003 Add Proposal Persists Required Record Fields
- **Type**: Functional
- **Preconditions**:
  - Existing work item with valid state.
- **Steps**:
  1. Call `golazo_git_propose(action="add", files=["src/a.py", "README.md"])`.
  2. Reload state and inspect last `git_actions` entry.
- **Expected Outcome**:
  - One new entry appended.
  - Entry includes `action`, `status`, `timestamp`, and `files`.
  - `action` equals `add`; `files` reflects input.
- **Explicit Failure Message**:
  - `Expected appended add proposal with action/status/timestamp/files.`

### TC-004 Timestamp Normalization for Proposal Records
- **Type**: Non-Functional / Cross-Platform Consistency
- **Preconditions**:
  - Proposal record created successfully.
- **Steps**:
  1. Parse persisted `timestamp` value from appended entry.
  2. Validate normalized UTC ISO-8601 format with trailing `Z`.
- **Expected Outcome**:
  - Timestamp is parseable UTC ISO-8601 and ends with `Z`.
- **Explicit Failure Message**:
  - `Expected proposal timestamp in UTC ISO-8601 format with trailing 'Z'.`

### TC-005 Commit Without Message Returns Deterministic Parameter-Required Error
- **Type**: Negative / Validation
- **Preconditions**:
  - Existing work item with valid state.
- **Steps**:
  1. Call `golazo_git_propose(action="commit")` without `message`.
- **Expected Outcome**:
  - Call fails deterministically.
  - Error clearly indicates required parameter `message`.
  - No new proposal entry appended.
- **Explicit Failure Message**:
  - `Expected deterministic parameter-required error for missing 'message' on commit.`

### TC-006 Push Without Branch Returns Deterministic Parameter-Required Error
- **Type**: Negative / Validation
- **Preconditions**:
  - Existing work item with valid state.
- **Steps**:
  1. Call `golazo_git_propose(action="push")` without `branch`.
- **Expected Outcome**:
  - Call fails deterministically.
  - Error clearly indicates required parameter `branch`.
  - No new proposal entry appended.
- **Explicit Failure Message**:
  - `Expected deterministic parameter-required error for missing 'branch' on push.`

### TC-007 Branch Without Branch Name Returns Deterministic Parameter-Required Error
- **Type**: Negative / Validation
- **Preconditions**:
  - Existing work item with valid state.
- **Steps**:
  1. Call `golazo_git_propose(action="branch")` without `branch`.
- **Expected Outcome**:
  - Call fails deterministically.
  - Error clearly indicates required parameter `branch`.
  - No new proposal entry appended.
- **Explicit Failure Message**:
  - `Expected deterministic parameter-required error for missing 'branch' on branch action.`

### TC-008 Missing Work Item Returns Clear Create Guidance
- **Type**: Negative / Usability
- **Preconditions**:
  - Work item ID does not exist.
- **Steps**:
  1. Call `golazo_git_propose` targeting non-existent work item.
- **Expected Outcome**:
  - Call fails with clear not-found guidance and creation direction.
- **Explicit Failure Message**:
  - `Expected not-found error with explicit create-work-item guidance.`

### TC-009 Append-Only History Integrity
- **Type**: Reliability / Audit Integrity
- **Preconditions**:
  - Existing work item with one or more `git_actions` entries.
- **Steps**:
  1. Capture snapshot of existing entries.
  2. Submit a new valid proposal.
  3. Reload state and compare pre-existing entries.
- **Expected Outcome**:
  - Existing entries remain unchanged.
  - New entry appears only at list tail.
- **Explicit Failure Message**:
  - `Expected append-only behavior: prior proposal entries must not be mutated or reordered.`

### TC-010 Persistence Round-Trip Across Workflow Tools
- **Type**: Integration / Regression
- **Preconditions**:
  - At least one proposal exists in `git_actions`.
- **Steps**:
  1. Run non-proposal workflow state load/save path.
  2. Reload state.
  3. Verify proposal history remains intact.
- **Expected Outcome**:
  - Proposal entries persist unchanged across tool round-trips.
- **Explicit Failure Message**:
  - `Expected 'git_actions' history to persist unchanged across workflow load/save round-trips.`

## Security, Reliability, and Performance-Sensitive Checks
- **Security-oriented validation**: malformed or empty required fields are rejected deterministically without mutating state.
- **Reliability**: persistence failure must return hard failure and must not report success.
- **Performance-sensitive**: proposal creation should complete within interactive MCP latency targets under normal local filesystem conditions.

## Suggested Automated Test Naming
- `test_git_propose_initializes_git_actions_for_legacy_state`
- `test_git_propose_add_persists_required_fields`
- `test_git_propose_commit_requires_message`
- `test_git_propose_push_requires_branch`
- `test_git_propose_branch_requires_branch`
- `test_git_propose_missing_workitem_returns_create_guidance`
- `test_git_propose_append_only_history`
- `test_git_propose_persists_across_roundtrip`
- `test_git_propose_timestamp_utc_iso8601_z`
