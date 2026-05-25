**Status**: IMPLEMENTED

**User Story**
- Title: Add direct institution connector integration for target providers
- As a: personal finance user
- I want: real account sync connectors for First Tech and Fidelity
- So that: I can ingest real transactions without fixture-only data
- Out of scope:
  - Universal provider marketplace
  - Manual file-import fallback workflows
  - Credential vault cloud sync
- Assumptions:
  - Assumption (explicit): Interface type is API-backed workflow triggered from local app.
  - Assumption (explicit): Target platform remains local desktop operation.
  - Assumption (explicit): Persistence remains local encrypted storage.
- Acceptance Criteria (bulleted, testable):
  - Connectors can authenticate one account each for First Tech and Fidelity in non-test mode.
  - `run_sync` ingests last 90 days using direct provider integration path.
  - Connector errors classify as connectivity/auth/provider and provide actionable retry guidance.
  - Retry after transient failure does not create duplicates.
  - Existing fixture connector tests remain green.
- Non-functional requirements:
  - Sync operation remains deterministic for duplicate prevention.
  - Credential material is never persisted in plaintext.
- Telemetry / metrics expected:
  - Sync success rate by institution.
  - Failure category distribution by institution.
- Rollout / rollback notes:
  - Rollout behind per-connector enable flags.
  - Rollback by disabling unstable connector while keeping local data intact.
