# FRC-005 Design Doc

## Summary
Add a runnable local web API entrypoint to expose Finance Planner health and capability summary endpoints.

## Problem Statement
Current codebase ships planner service logic but no executable app command, preventing straightforward local runtime use.

## Business Case
- Unblocks practical usage and future UI integration.
- Establishes stable API contract for subsequent frontend stories.

## Stakeholders
- Primary: end user operating planner locally.
- Secondary: future frontend integration work.

## Functional Requirements
1. Add Python module entrypoint: `python -m finance_planner.api`.
2. Expose `GET /health` returning deterministic status/version payload.
3. Expose `GET /planner/summary` returning deterministic capability summary.
4. Document startup and verification commands in README.

## Non-Functional Requirements
- Local startup in under 3 seconds.
- No external network dependency for startup.

## Proposed Approach
- Add FastAPI-based API module with `create_app` and CLI runner via uvicorn.
- Use static deterministic summary payload backed by implemented service capabilities.
- Add API tests with FastAPI TestClient.

## Alternatives Considered
- Pure CLI only: rejected because web API contract is needed for planned UI integration.
- Flask: rejected to keep typed OpenAPI support and concise async-friendly defaults.

## Risks and Mitigations
- Risk: dependency bloat from API runtime packages.
  - Mitigation: add minimal dependencies only (`fastapi`, `uvicorn`) and keep module thin.
- Risk: payload drift from actual capabilities.
  - Mitigation: align summary fields with capability registry and test assertions.

## Dependencies
- Existing `finance_planner` service package.
- Added runtime dependencies: FastAPI, uvicorn.

## Migration / Rollout / Rollback
- Additive rollout with new module and docs.
- Rollback by removing API module without impacting core service logic.

## Observability Plan
- Log startup host/port and startup timestamp.
- In-memory health hit counter included in health payload.

## Test Strategy Summary
- Red/green tests for startup importability and endpoints.
- Deterministic response contract assertions.
- Existing regression suite remains green.
