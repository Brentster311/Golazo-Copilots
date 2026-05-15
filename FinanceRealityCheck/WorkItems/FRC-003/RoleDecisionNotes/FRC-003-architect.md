# FRC-003 Architect Notes

## Decision
Architect gate approved with additive local-only portfolio-planning design.

## Contract constraints
- Explicit response contracts for:
  - position persistence
  - allocation dashboard summary
  - recommendation options with pros/cons
- Deterministic ordering required for reproducibility.

## Security/Privacy
- Keep all position and recommendation computations local.
- Avoid exposing sensitive account labels in unnecessary fields.
