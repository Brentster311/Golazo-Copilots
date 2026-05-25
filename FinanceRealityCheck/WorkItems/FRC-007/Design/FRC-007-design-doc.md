# FRC-007 Design Doc

## Summary
Add direct provider connector classes for First Tech and Fidelity behind enable flags, while preserving existing fixture connectors and deterministic duplicate-safe sync behavior.

## Problem Statement
Current sync flow uses fixture-only connectors; story requires non-test direct integration path for target institutions.

## Functional Requirements
1. Add direct connector path for First Tech and Fidelity (non-test mode).
2. Direct path supports authentication and transaction fetch for 90-day sync window.
3. Error normalization remains connectivity/auth/provider with actionable retry guidance.
4. Retry after transient failure remains duplicate-safe.
5. Existing fixture connector behavior and tests remain green.

## Non-Functional Requirements
- Sync remains deterministic for duplicate prevention.
- Credential material never persisted in plaintext.

## Proposed Approach
- Introduce a connector protocol that both fixture and direct connectors satisfy.
- Add FirstTechDirectConnector and FidelityDirectConnector classes backed by provider adapter interfaces.
- Keep planner run_sync contract unchanged; inject connector implementations via existing constructor mapping.
- Add tests for direct connector success and error normalization.

## Risks and Mitigations
- Risk: direct connector network failures.
  - Mitigation: normalize to actionable connectivity/auth/provider errors.
- Risk: regressions to fixture flow.
  - Mitigation: keep fixture tests and add targeted direct-connector tests.

## Dependencies
- Existing planner service and connector abstractions.
- requests package (already available in Python std ecosystem assumptions for direct HTTP path).

## Test Strategy
- Unit tests for direct connector success/auth/connectivity/provider errors.
- Planner sync test using injected direct connector stubs for 90-day ingestion and duplicate safety.
- Existing fixture connector tests remain unchanged and green.
