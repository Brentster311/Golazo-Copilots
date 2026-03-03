# GCP-0062 Design Document — Enforce Branch Naming Format `<useralias>/<workitemid>`

## Summary
This work item adds centralized enforcement in the Golazo workflow branch-creation path so newly created branches must follow `<useralias>/<workitemid>`. Enforcement blocks non-compliant names, provides actionable guidance, and emits telemetry to measure adoption and failure reasons.

## Problem Statement
- Branch names created through workflow tooling are currently not guaranteed to follow a single convention.
- Inconsistent naming reduces ownership clarity and weakens work-item traceability.
- Lack of deterministic validation messaging increases friction when users guess acceptable formats.

## Business Case
### Why now
- The user story defines a clear convention and acceptance criteria needed to improve workflow consistency immediately.
- Branch naming is a high-frequency action; small inconsistencies quickly create operational and governance overhead.

### Impact
- Improves branch-level traceability from branch name alone.
- Reduces review/admin overhead for maintainers by standardizing ownership and work-item association.
- Creates measurable compliance signals for continuous process improvement.

### KPIs
- Compliance rate: percentage of branch creation attempts that match `<useralias>/<workitemid>`.
- Validation failure distribution by reason: missing alias, invalid format, mismatched work item.
- Time-to-success after first validation error (proxy for message quality/actionability).
- Adoption trend over time for compliant branch creation.

## Stakeholders
- Developers creating branches via Golazo workflow tooling.
- Repo maintainers enforcing contribution hygiene and traceability.
- QA/release stakeholders relying on reliable work-item linkage.
- On-call/support owners for workflow tooling failures.

## Requirements
### Functional Requirements
1. Enforce branch naming in the supported workflow branch-creation path.
2. Accept branch names only when they exactly match `<useralias>/<workitemid>`.
3. For alias `brentj` and work item `GCP-0062`, resulting branch name must be `brentj/GCP-0062`.
4. Block branch creation when input does not match required pattern.
5. Return clear corrective error messages for invalid input including one valid example.
6. If user alias is missing/unresolved, fail with explicit guidance to configure/provide alias and include example format.
7. Permit successful creation when name is valid.

### Non-Functional Requirements
1. Validation executes within interactive command latency for CLI/API users.
2. Validation logic is centralized to avoid divergence across commands.
3. Error messages are deterministic and actionable.
4. Behavior is cross-platform and independent of OS-specific shell behavior.
5. No new persistent datastore is introduced for this story.

## Proposed Approach
### High-Level Plan
1. Add/extend a single branch-name validation component used by the workflow branch-creation path.
2. Resolve required runtime inputs: authenticated `useralias` and active/selected `workitemid`.
3. Compose expected branch value as `<useralias>/<workitemid>` and compare with proposed branch name.
4. On mismatch, block creation and return categorized, actionable validation output.
5. On match, allow normal branch-creation flow.
6. Emit telemetry events for attempts, outcomes, and categorized failure reasons.

### Validation Behavior Contract
- Pattern shape: one `/` separator with non-empty `useralias` and `workitemid` segments.
- Story-scoped work item format expectation: Golazo IDs such as `GCP-0062`.
- Enforcement scope: branch creation initiated through project workflow tooling.
- Out of scope: rewriting/renaming existing historical branches.

### Error Messaging Contract
- Invalid format: explain expected format and show example `brentj/GCP-0062`.
- Missing alias: explain alias could not be resolved and provide remediation guidance.
- Mismatched work item: indicate expected work item id and show corrected example.

## Alternatives Considered
1. Warning-only mode (allow invalid branch names).
   - Rejected: does not satisfy acceptance criteria requiring blocked creation for invalid input.
2. Decentralized per-command validation.
   - Rejected: violates non-functional requirement to centralize checks and risks inconsistency.
3. Git-hook-only enforcement outside tooling path.
   - Rejected: out of scope for this story and does not guarantee workflow-path consistency.

## Risks, Mitigations, Open Questions
### Risks
1. Alias-resolution failures can block valid users if identity sources are unavailable.
2. Multiple branch creation entry points may bypass centralized enforcement if not wired consistently.
3. User friction may increase briefly at rollout due to stricter blocking behavior.

### Mitigations
1. Provide explicit remediation guidance when alias is missing/unresolved.
2. Route all supported branch-creation flows through the same validation component.
3. Roll out with updated docs/examples and monitor early failure telemetry.

### Open Questions
- No blocking open questions for this scope; assumptions from the user story are sufficient for implementation planning.

## Dependencies
- Existing Golazo workflow branch-creation CLI/API entry path.
- Authenticated user identity source used to derive `useralias`.
- Work item context source for `workitemid`.
- Existing telemetry/logging pipeline for event emission.
- Documentation surface for branch naming guidance.

## Migration / Rollout / Rollback Plan
### Migration
- No data migration required.
- Existing historical branches remain unchanged (explicitly out of scope).

### Rollout
1. Implement centralized validation and integrate into supported branch-creation path.
2. Update user-facing guidance to show required format and examples.
3. Deploy with telemetry enabled and monitor initial failure categories.
4. Validate cross-platform behavior in Windows/macOS/Linux environments used by the team.

### Rollback
- Disable strict enforcement in the branch-creation path and optionally retain warning-mode telemetry to preserve observability while restoring prior behavior.

## Observability Plan
- Capture event: branch creation attempt (metadata: alias-resolved yes/no, work item id present yes/no).
- Capture event: validation outcome (valid/invalid) and failure category.
- Capture event: branch creation success/failure post-validation.
- Dashboard views:
  - compliant vs non-compliant attempt rate,
  - top failure reasons,
  - post-rollout trendline for adoption.
- Operational alerting trigger: sustained spike in missing-alias failures.

## Test Strategy Summary
1. Positive path: valid `<useralias>/<workitemid>` input succeeds.
2. Negative path: invalid format is blocked with actionable error and example.
3. Negative path: missing/unresolved alias blocks with explicit remediation guidance.
4. Negative path: mismatched work item id blocks with corrected expected value.
5. Centralization/regression: all supported branch-creation entry points enforce same validator.
6. Telemetry assertions: valid/invalid attempts and failure categories are emitted as expected.
