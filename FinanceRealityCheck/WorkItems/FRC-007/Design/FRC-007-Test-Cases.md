# FRC-007 Test Cases

## AC coverage
- AC1: direct connectors authenticate one account each for First Tech and Fidelity in non-test mode.
- AC2: run_sync ingests last 90 days via direct connector path.
- AC3: connector errors classify as connectivity/auth/provider with actionable retry guidance.
- AC4: retry after transient failure is duplicate-safe.
- AC5: existing fixture connector tests remain green.

## Direct connector tests
1. FirstTechDirectConnector authentication + fetch success.
2. FidelityDirectConnector authentication + fetch success.
3. Connectivity failure maps to connectivity_error with retry guidance.
4. Auth failure maps to auth_error with retry guidance.
5. Provider failure maps to provider_error with retry guidance.

## Planner integration tests
6. Planner run_sync with direct connectors imports 90-day transactions.
7. Transient failure then retry does not duplicate transactions.
8. Existing fixture connector tests pass unchanged.

## Negative checks
- Invalid provider payload maps to provider_error.
- No plaintext credential material is returned in sync payloads.
