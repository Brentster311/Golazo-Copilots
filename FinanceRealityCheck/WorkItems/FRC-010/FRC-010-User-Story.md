**Status**: BACKLOG (Deferred until spend-safety MVP goals are met)

**User Story**
- Title: Add allocation visibility by account and asset class
- As a: personal finance user
- I want: allocation views grouped by account and by asset class
- So that: I can understand concentration at both portfolio and account level
- Out of scope:
  - Automated rebalancing trades
  - Tax-lot level accounting
  - External market data feeds
- Assumptions:
  - Assumption (explicit): Interface type is API payload consumed by local UI.
  - Assumption (explicit): Position values are user-supplied and locally persisted.
  - Assumption (explicit): Summary calculations are deterministic.
- Acceptance Criteria (bulleted, testable):
  - Allocation endpoint returns totals grouped by asset class.
  - Allocation endpoint also returns nested breakdown by account label.
  - Percentages and totals are internally consistent and deterministic.
  - Overweight/underweight recommendation options can reference account-level context.
  - Invalid or missing position records are handled with clear validation errors.
- Non-functional requirements:
  - Supports at least 1,000 positions without timeout.
  - Stable ordering of response objects across repeated reads.
- Telemetry / metrics expected:
  - Count of tracked accounts with positions.
  - Max asset-class concentration percentage.
- Rollout / rollback notes:
  - Rollout as enhancement to existing allocation contracts.
  - Rollback by disabling account-level view while retaining class-level summary.

## Reprioritization Note (2026-05-12)
- This work item is intentionally deferred until spend-safety MVP goals are shipped.
- Priority sequence ahead of this item: FRC-005, FRC-006, FRC-007, FRC-014, FRC-015.
- Scope remains valid and will be resumed after those items.
