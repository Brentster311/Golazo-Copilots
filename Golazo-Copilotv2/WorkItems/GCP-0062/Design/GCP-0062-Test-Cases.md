# GCP-0062 Test Cases

## Scope
Validate strict branch-name enforcement of `<useralias>/<workitemid>` in the supported Golazo workflow branch-creation path, including blocking behavior, deterministic errors, centralization, and telemetry integrity.

## Assumptions
- Enforcement scope is limited to branch creation initiated through supported Golazo workflow tooling.
- `useralias` is resolved from authenticated runtime identity context.
- `workitemid` is resolved from active/selected Golazo work item context.
- The existing design artifact path `WorkItems/GCP-0062/Design/GCP-0062-design-doc.md` is authoritative for this work item.

## Acceptance Criteria Mapping
- **AC1**: Given alias `brentj` and work item `GCP-0062`, creating through supported path yields `brentj/GCP-0062`.
  - Covered by: TC-01, TC-02
- **AC2**: Non-matching input is blocked with clear corrective error.
  - Covered by: TC-03, TC-04, TC-05
- **AC3**: Valid matching input succeeds.
  - Covered by: TC-02
- **AC4**: Missing/unresolved alias fails with explicit guidance and example format.
  - Covered by: TC-06

## Functional Tests

### TC-01 Default composition uses runtime alias/work-item
- Precondition: Runtime resolves alias=`brentj`, workitem=`GCP-0062`; supported branch-creation path invoked.
- Action: Trigger branch creation using standard workflow path that composes/uses expected name.
- Expected outcome:
  - Candidate and/or resulting branch name is exactly `brentj/GCP-0062`.
  - No validation error is emitted.
- Expected failure message:
  - "Expected composed branch name to be exactly brentj/GCP-0062 for alias=brentj and workitem=GCP-0062."

### TC-02 Explicit valid input is accepted and branch is created
- Precondition: Alias and work item resolve to `brentj` and `GCP-0062`; repository state allows branch creation.
- Action: Submit branch name `brentj/GCP-0062` via supported branch-creation command/API.
- Expected outcome:
  - Validation passes.
  - Branch creation succeeds for `brentj/GCP-0062`.
- Expected failure message:
  - "Expected valid branch name brentj/GCP-0062 to pass validation and create successfully."

### TC-03 Invalid separator/shape is blocked with corrective guidance
- Precondition: Alias/work item resolve to `brentj` / `GCP-0062`.
- Action: Attempt branch creation with malformed names (for example `brentj-GCP-0062`, `brentj//GCP-0062`, `/GCP-0062`, `brentj/`).
- Expected outcome:
  - Creation is blocked.
  - Error clearly states expected format `<useralias>/<workitemid>` and includes example `brentj/GCP-0062`.
- Expected failure message:
  - "Expected malformed branch input to be blocked with format guidance and example brentj/GCP-0062."

### TC-04 Mismatched work item is blocked with corrected expected value
- Precondition: Alias resolves to `brentj`; active work item is `GCP-0062`.
- Action: Attempt creation with `brentj/GCP-9999`.
- Expected outcome:
  - Creation is blocked.
  - Error identifies mismatch and shows corrected expected value `brentj/GCP-0062`.
- Expected failure message:
  - "Expected mismatched work item branch name to be rejected with corrected expected value brentj/GCP-0062."

### TC-05 Mismatched alias is blocked
- Precondition: Runtime alias resolves to `brentj`; active work item is `GCP-0062`.
- Action: Attempt creation with `otheruser/GCP-0062`.
- Expected outcome:
  - Creation is blocked.
  - Error indicates alias mismatch and includes a valid example with resolved alias.
- Expected failure message:
  - "Expected branch alias mismatch to be blocked and corrected to resolved alias format (e.g., brentj/GCP-0062)."

### TC-06 Missing/unresolved alias fails with explicit remediation
- Precondition: Alias resolution fails or returns empty; work item context is available (`GCP-0062`).
- Action: Attempt branch creation through supported path.
- Expected outcome:
  - Creation is blocked before git branch write.
  - Error explicitly instructs how to configure/provide alias and includes example format `brentj/GCP-0062`.
- Expected failure message:
  - "Expected missing alias failure to provide explicit remediation guidance and example format brentj/GCP-0062."

## Non-Functional / Reliability Tests

### TC-07 Centralized validator is enforced across supported entry points
- Precondition: All supported branch-creation commands/APIs are enumerated for this repository.
- Action: Execute equivalent invalid input through each supported entry point.
- Expected outcome:
  - Each path blocks invalid input with consistent reason taxonomy and message contract.
- Expected failure message:
  - "Expected all supported branch-creation entry points to enforce the centralized validator consistently."

### TC-08 Deterministic and actionable error messaging contract
- Precondition: Invalid cases exist for format, alias missing, and work-item mismatch.
- Action: Trigger each invalid class repeatedly.
- Expected outcome:
  - Message content remains deterministic per class.
  - Each message includes reason, corrective guidance, and one valid example.
- Expected failure message:
  - "Expected deterministic actionable error contract (reason + remediation + example) for each validation class."

### TC-09 Interactive-latency guard for validation path
- Precondition: Representative local environment for supported CLI/API usage.
- Action: Measure validation+response overhead across repeated runs (valid and invalid).
- Expected outcome:
  - Validation path remains within interactive command latency expectations defined by project standards.
- Expected failure message:
  - "Expected validation feedback within interactive latency budget; observed regression beyond acceptable threshold."

### TC-10 Telemetry reason integrity and outcome capture
- Precondition: Telemetry pipeline/stub capture is enabled for branch-creation attempts.
- Action: Execute one valid attempt and invalid attempts for each failure reason class.
- Expected outcome:
  - Attempt and outcome events are emitted.
  - Invalid attempts are labeled with exactly one expected failure reason (`missing alias`, `invalid format`, `mismatched work item`).
  - Success event emitted only for valid creation.
- Expected failure message:
  - "Expected telemetry to emit complete attempt/outcome events with one normalized failure reason per invalid attempt."
