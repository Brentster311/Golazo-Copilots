# FRC-002 Architect Notes

## Architectural Decision
Approved additive design with explicit contracts for unusual transaction alerts and goal drift alerts.

## Required contract behaviors
- Unusual alerts include transaction id, reason, severity, and recommendation.
- Goal drift alerts include goal id, expected contribution, actual contribution, deficit, and recommendation.
- Alert retrieval methods must be deterministic by design (stable sort keys).

## Security and privacy constraints
- Maintain local-only computation and storage model.
- Avoid exposing sensitive payload internals in alert reason text.

## Reliability constraints
- Sparse-history handling must not over-alert; enforce baseline sample floor.
- Explicit date arithmetic and boundary handling for drift calculations.

## Capability check
- Impact analysis over design artifacts reports no currently affected registered capabilities.

## Decision
Architect gate approved; proceed to developer implementation.
