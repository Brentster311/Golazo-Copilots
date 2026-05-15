# FRC-002 Program Manager Notes

## Scope
Translate FRC-002 into a focused alerting increment:
- unusual transaction alerts
- savings goal drift alerts

## Sequencing
1. Persist alert settings and goals data model.
2. Implement unusual detection and goal drift logic.
3. Expose deterministic retrieval contracts.
4. Validate with targeted tests and regression coverage.

## Why this sequencing
- Minimizes blast radius by adding tables/methods before complex heuristics.
- Keeps behavior additive over FRC-001 baseline.

## Risks highlighted
- False positives for sparse merchant history.
- Drift interpretation ambiguity.

## Handoff guidance
- QA should demand explicit expected-values in drift alert payloads.
- Architect should validate deterministic ordering and local-only privacy posture.
