# FRC-002 Review Comments

## Domain Expert Guidance
- Use minimum baseline sample floor for unusual detection (avoid sparse-history false positives).
- Persist and expose unusual detection settings in alert payload context.
- Include transparent goal drift fields: expected, actual, deficit, and recommended next action.
- Keep alert ordering deterministic and local-only.

## Quality Assurance Review
- Design scope is clear and additive over FRC-001.
- Unusual alert contract should include threshold inputs and baseline sample count for explainability.
- Goal drift contract should include expected contribution to date, actual contribution to date, deficit, and severity.
- Negative-path requirements to test: invalid settings, invalid goal definitions, and empty contribution histories.
- Deterministic ordering is required for repeated reads.

## Architect Notes
- Keep alert logic in planner service domain layer; avoid coupling to transport/UI concerns.
- Persist settings and goal data in dedicated tables with explicit defaults for backward compatibility.
- Require stable sort keys in alert retrieval methods to guarantee deterministic output.
- Security: goal metadata and contribution records should follow existing encrypted/local privacy posture where sensitive values are persisted.
- Default-behavior checks: date arithmetic must use explicit date boundaries to avoid timezone drift in expected-progress computations.
- Capability impact check currently reports no affected registered capabilities.
