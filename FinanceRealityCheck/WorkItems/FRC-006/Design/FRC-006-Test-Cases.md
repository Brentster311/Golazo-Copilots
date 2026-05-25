# FRC-006 Test Cases

## AC coverage
- AC1: frontend startup command works and app loads.
- AC2: landing page renders status/version from /health.
- AC3: planner summary page renders capability list from /planner/summary.
- AC4: API unavailable shows deterministic error state.
- AC5: deterministic output for unchanged API payloads.

## Test set
1. App shell renders navigation and default landing section.
2. Health page shows status and version for successful /health response.
3. Planner summary page shows interface and capabilities for successful /planner/summary response.
4. Health fetch failure shows deterministic error text and retry control.
5. Summary fetch failure shows deterministic error text and retry control.
6. Snapshot/strict-text assertions verify deterministic rendering for fixed mocked payloads.

## Negative checks
- API payload missing required fields should show contract error state, not crash.
- No sensitive credential or token fields displayed in UI.
