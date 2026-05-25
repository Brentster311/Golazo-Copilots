# FRC-005 Architect Notes

## Decision
Approve additive API runtime layer with strict separation from planner domain methods.

## Contract constraints
- Deterministic health and summary payloads.
- Localhost-safe default binding.
- Explicit app factory (`create_app`) for testability.
