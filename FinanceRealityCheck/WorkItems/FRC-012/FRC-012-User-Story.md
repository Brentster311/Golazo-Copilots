**Status**: BACKLOG (Deferred until spend-safety MVP goals are met)

**User Story**
- Title: Add backup and recovery workflow for local encrypted planner data
- As a: personal finance user
- I want: a reliable backup and restore workflow
- So that: I can recover planner data after device failure or corruption
- Out of scope:
  - Cloud sync replication
  - Multi-device conflict resolution
  - Enterprise key escrow
- Assumptions:
  - Assumption (explicit): Interface type is local CLI/API-triggered backup operations.
  - Assumption (explicit): Backup artifacts remain encrypted-at-rest.
  - Assumption (explicit): Restore requires explicit user action.
- Acceptance Criteria (bulleted, testable):
  - Backup command produces restorable archive containing DB and key material in encrypted form.
  - Restore command can recreate a working planner state from backup archive.
  - Backup and restore operations provide clear success/failure messages.
  - Restored state passes deterministic smoke checks for planner summaries and alerts.
  - Backup workflow is documented in README with verification steps.
- Non-functional requirements:
  - Backup operation completes within practical local runtime for typical dataset.
  - Recovery process is idempotent and auditable.
- Telemetry / metrics expected:
  - Last successful backup timestamp.
  - Backup/restore success and failure counts.
- Rollout / rollback notes:
  - Rollout as optional maintenance workflow.
  - Rollback by disabling backup command if regressions found.

## Reprioritization Note (2026-05-12)
- This work item is intentionally deferred until spend-safety MVP goals are shipped.
- Priority sequence ahead of this item: FRC-005, FRC-006, FRC-007, FRC-014, FRC-015.
- Scope remains valid and will be resumed after those items.
