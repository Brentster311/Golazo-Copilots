**Status**: BACKLOG (Deferred until spend-safety MVP goals are met)

**User Story**
- Title: Add local telemetry and categorization quality tracking
- As a: personal finance user
- I want: local metrics for sync reliability and categorization correction quality
- So that: I can trust planner signals and detect degradation early
- Out of scope:
  - Remote telemetry export
  - Third-party analytics platforms
  - PII-heavy event payloads
- Assumptions:
  - Assumption (explicit): Interface type is API and local logs.
  - Assumption (explicit): Telemetry remains local-only by default.
  - Assumption (explicit): Metrics storage can be lightweight local persistence.
- Acceptance Criteria (bulleted, testable):
  - System records sync success/failure counts by institution.
  - System records categorization correction rate over time.
  - Metrics endpoint returns deterministic aggregates for unchanged data.
  - Telemetry payloads exclude sensitive account tokens and raw encrypted payload blobs.
  - Existing planner behavior remains unaffected when telemetry is enabled.
- Non-functional requirements:
  - Telemetry overhead is negligible for normal planner operations.
  - Metrics reads are fast for local dashboards.
- Telemetry / metrics expected:
  - Sync success rate by institution.
  - Categorization correction rate trend.
  - Budget alert lead-time metrics.
- Rollout / rollback notes:
  - Rollout as optional local observability module.
  - Rollback by disabling telemetry writes while preserving planner core operations.

## Reprioritization Note (2026-05-12)
- This work item is intentionally deferred until spend-safety MVP goals are shipped.
- Priority sequence ahead of this item: FRC-005, FRC-006, FRC-007, FRC-014, FRC-015.
- Scope remains valid and will be resumed after those items.
