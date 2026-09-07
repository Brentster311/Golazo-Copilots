# GCP-0073 Refactor Expert Decision Notes

## Decision

No behavior-preserving refactor was applied. The MCP 2.x adapter is already thin and delegates to the modular registry and dispatcher. Removing the remaining pre-existing legacy definitions from `server.py` would overlap the separate GCP-0074 cleanup work item and increase migration risk.

## Modularity Audit

| File | Lines | Top-level functions | Decision |
|---|---:|---:|---|
| `src/golazo_copilot/server.py` | 829 | 19 | Flagged. Pre-existing legacy compatibility body remains; MCP registration is canonical, and broader decomposition is deferred to GCP-0074. |
| `tests/test_gcp0073_mcp2_migration.py` | 95 | 6 | Focused and within targets. |
| `tests/gcp0073_wheel_smoke.py` | 58 | 1 | Focused installed-artifact harness. |
| `tests/test_gcp0061_server_modular_refactor.py` | 74 | 0 | Existing class-grouped tests; one assertion updated. |
| `tests/test_gcp044_workspace_path.py` | 100 | 0 | Existing class-grouped tests; one assertion updated. |
| `tests/test_gcp0072_skill_bootstrap.py` | 334 | 18 | Pre-existing test module; two assertion-only updates do not justify splitting it here. |
| `tests/test_gcp_bootstrap.py` | 496 | 2 | Pre-existing test module; one assertion-only update does not justify splitting it here. |

`pyproject.toml` contains configuration and metadata rather than executable responsibilities. Its MCP range and Python 3.10 test fallback are narrowly scoped.

## Validation

- Pre-refactor full suite: 528 passed, 3 skipped.
- Changed server module coverage: 91%.
- Scoped Ruff: no findings.
- No refactor was performed, so behavior and validation results remain unchanged.
- Capability analysis found no registered capability impact.

## Workflow

Created and switched to feature branch `brentj/GCP-0073`; no files were staged or committed.