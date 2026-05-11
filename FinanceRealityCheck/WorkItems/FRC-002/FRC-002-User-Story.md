**Status**: BACKLOG

**User Story**
- Title: Add unusual transaction and goal drift alerts
- As a: single-user personal finance planner
- I want: the planner to detect unusual spending events and savings-goal drift from my local financial data
- So that: I can react early to suspicious or off-track behavior before month-end surprises
- Out of scope:
  - Fraud dispute workflows or bank-side charge actions
  - Trade recommendations or tax filing behavior
  - Multi-user goal collaboration
- Assumptions:
  - Assumption (explicit): Interface remains desktop-first web app.
  - Assumption (explicit): Target platform remains Windows-first with cross-platform-compatible implementation.
  - Assumption (explicit): Data persistence remains local encrypted storage.
  - Assumption (explicit): User is non-technical end user consuming alerts from app UI/API responses.
- Acceptance Criteria (bulleted, testable):
  - User can configure unusual-transaction detection settings (minimum amount and sensitivity factor) and those settings persist locally.
  - After sync/import, the system identifies unusual debit transactions by comparing recent amount behavior against merchant/category history and returns structured unusual-transaction alerts.
  - User can create savings goals with target amount, target date, and planned monthly contribution, persisted locally.
  - User can record goal contributions, and the system returns goal-drift alerts when current progress falls behind expected progress based on time elapsed and planned contribution.
  - Alert payloads include actionable fields (reason, severity, related transaction or goal id, recommended next step) and are deterministic across repeated reads.
- Non-functional requirements:
  - Alert computations remain local-only and do not require cloud services.
  - Unusual detection and goal-drift evaluation should remain responsive on datasets of 10,000 transactions.
  - Alert generation must be deterministic for the same underlying dataset and settings.
- Telemetry / metrics expected:
  - Count of unusual alerts per sync run.
  - False-positive override rate for unusual alerts (future UX instrumentation).
  - Goal drift alert frequency and average days-behind progression.
- Rollout / rollback notes:
  - Rollout as additive alerting features over existing baseline ingestion/categorization workflow.
  - If alert quality is poor, disable unusual detection and goal-drift modules via settings while preserving stored goal and transaction data.

## Decomposition Rationale
FRC-001 established ingestion, categorization, and budget baseline. This story adds only two new alerting capabilities (unusual transactions and goal drift) without expanding into portfolio allocation or tax-threshold surfaces.