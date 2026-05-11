# FRC-002 Project Owner Assistant Notes

## Scope Selection
Focused on one vertical slice: proactive alerts beyond category-cap budgets.

Included:
- Unusual transaction detection controls and output.
- Savings goal tracking and drift detection alerts.

Excluded:
- Fraud workflows, portfolio features, and tax-planning surfaces.

## Why This Scope
- Directly follows FRC-001 baseline and provides immediate behavioral value.
- Keeps risk constrained to additive domain logic in existing local planner service.

## Assumptions
- Existing interface/platform/persistence decisions from FRC-001 continue unchanged.
- Alerts are consumed by UI/API layers; this story delivers backend behavior and deterministic contracts.

## Risks
- Unusual detection may generate false positives if heuristics are too sensitive.
- Goal drift semantics require clear expected-progress formula to avoid user confusion.

## Follow-on Candidates
- FRC-003 remains allocation dashboard and recommendation options.
- FRC-004 remains tax-aware planning thresholds.
