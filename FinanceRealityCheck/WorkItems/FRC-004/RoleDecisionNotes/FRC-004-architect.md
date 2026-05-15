# FRC-004 Architect Notes

## Decision
Architect gate approved with additive advisory tax planning design.

## Contract constraints
- Explicit method contracts for settings, surface, and threshold alerts.
- Deterministic ordering and consistent severity logic.

## Security constraints
- Keep tax configuration and income projections in local storage only.
- Avoid raw transaction payload disclosure in tax output contracts.
