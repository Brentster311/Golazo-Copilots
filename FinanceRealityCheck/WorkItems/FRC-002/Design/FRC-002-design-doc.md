# FRC-002 Design Doc

## Summary
Add two proactive alert capabilities to the existing local planner service:
- Unusual transaction alerts for suspicious/outlier debit activity.
- Savings goal drift alerts when contribution progress falls behind expected pace.

## Problem Statement
FRC-001 provides ingestion and budget drift alerts, but users still lack proactive signals for abnormal spending events and progress slippage on savings goals.

## Business Case (Why Now, Impact, KPIs)
Why now:
- Alerts build directly on established ingestion/categorization baseline.
- Early anomaly and drift detection increases trust and planning responsiveness.

KPIs:
- Unusual alert generation latency within normal query response window.
- Stable/deterministic alert count across repeated reads on unchanged data.
- Goal drift alerts available for all active goals with contribution history.

## Stakeholders
- Primary: single-user planner (Brent).

## Functional Requirements
1. Detection settings
- Persist unusual-detection controls: minimum amount and sensitivity factor.

2. Unusual transaction detection
- Evaluate debit transactions against merchant-level recent history.
- Emit unusual alert when amount exceeds configured threshold based on baseline behavior.
- Include actionable fields: reason, severity, transaction id, recommendation.

3. Savings goals and contributions
- Create savings goals with target amount, target date, and planned monthly contribution.
- Record goal contributions with contribution date and amount.

4. Goal drift detection
- Compute expected progress by elapsed time versus target date and planned contribution.
- Emit drift alert when actual progress is behind expected progress by threshold.
- Include actionable fields: goal id, expected vs actual progress, suggested action.

5. Deterministic alert retrieval
- Repeated retrieval without data changes returns stable alert payloads/order.

## Non-Functional Requirements
- Local-only execution; no cloud dependency.
- Deterministic, bounded-cost alert calculations for current data scale.
- Compatibility with existing encrypted local persistence model.

## Proposed Approach (High Level)
- Extend planner persistence schema with:
  - alert_settings
  - savings_goals
  - goal_contributions
- Add planner service methods:
  - update_unusual_settings(...)
  - get_unusual_transaction_alerts(...)
  - create_savings_goal(...)
  - add_goal_contribution(...)
  - get_goal_drift_alerts(...)
- Unusual logic:
  - baseline by normalized merchant over recent debits (mean amount + sensitivity factor * spread proxy)
  - require minimum amount filter
- Goal drift logic:
  - expected contribution based on elapsed months and planned monthly contribution
  - alert if actual contribution < expected contribution

## Alternatives Considered
1. Rule-only unusual detection by hard category caps
- Rejected because this duplicates budget alerts and misses merchant-specific anomalies.

2. External anomaly detection service
- Rejected due local-only constraint.

## Risks, Mitigations, Open Questions
Risks:
- Over-alerting for sparse merchant history.
- User confusion if drift formula is opaque.

Mitigations:
- Require baseline sample floor and configurable sensitivity.
- Include reason fields with expected vs actual values.

Open questions:
- Future user feedback loop for dismissing/learning from unusual alerts.

## Dependencies
- Existing planner service schema and transaction corpus.
- Existing pytest test infrastructure.

## Migration / Rollout / Rollback Plan
Rollout:
- Additive schema migration with backward-compatible defaults.

Rollback:
- Disable alert methods while preserving new tables for safe forward migration.

## Observability Plan
- Count unusual alerts per retrieval window.
- Count goal drift alerts and average deficit amount.
- Track settings values applied for unusual detection.

## Test Strategy Summary
- Unit/integration tests for settings persistence, unusual alert detection, goals, contribution tracking, and deterministic alert outputs.
- Negative tests for invalid settings and invalid goal definitions.
- Regression tests to ensure existing FRC-001 behaviors remain green.
