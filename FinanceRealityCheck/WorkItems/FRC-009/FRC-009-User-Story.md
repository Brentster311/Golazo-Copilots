**Status**: BACKLOG (Deferred until spend-safety MVP goals are met)

**User Story**
- Title: Add quarterly and retirement-oriented planning surfaces
- As a: personal finance user
- I want: quarterly planning and long-term retirement progress views
- So that: I can align near-term budgets with long-term goals
- Out of scope:
  - Financial advisor-grade optimization models
  - Tax filing calculations
  - Monte Carlo simulation engine
- Assumptions:
  - Assumption (explicit): Interface type is API-backed planning endpoints.
  - Assumption (explicit): Data model remains local-only.
  - Assumption (explicit): Retirement planning uses transparent rule-based projections.
- Acceptance Criteria (bulleted, testable):
  - Quarterly summary endpoint returns income, spending, savings trend for selected quarter.
  - Retirement progress endpoint returns target amount, projected contribution path, and gap.
  - Planning outputs are deterministic for unchanged underlying data.
  - Planning payload includes explicit assumptions used in projections.
  - Existing monthly budget and goal-drift behaviors remain unchanged.
- Non-functional requirements:
  - Query latency remains acceptable for multi-year local history.
  - Projection logic remains explainable in payload fields.
- Telemetry / metrics expected:
  - Quarterly planning query count.
  - Retirement gap trend over time.
- Rollout / rollback notes:
  - Rollout as additive planning module.
  - Rollback by hiding quarterly/retirement surfaces while keeping stored data.

## Reprioritization Note (2026-05-12)
- This work item is intentionally deferred until spend-safety MVP goals are shipped.
- Priority sequence ahead of this item: FRC-005, FRC-006, FRC-007, FRC-014, FRC-015.
- Scope remains valid and has been moved later in roadmap order.
