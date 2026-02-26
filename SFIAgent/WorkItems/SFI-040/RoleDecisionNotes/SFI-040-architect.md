# SFI-040 Architect Notes

## Architectural Assessment
- UI-only enhancement with low blast radius.
- No changes to API interfaces, cache schema, or service-layer contracts.
- Existing stats payloads already include required inputs (`score`, `cost`).

## Constraints for Implementation
1. Keep computation in presentation layer only.
2. Use a single helper for `Score/Min` string formatting to avoid branch drift.
3. Preserve existing behavior and sorting contracts except requested column order.

## Risk Mitigation
- Add explicit tests for tuple ordering in each table branch.
- Add explicit tests for zero-cost fallback (`28,800`) rendering and ratio behavior.

## Decision
Approved for Developer implementation.
