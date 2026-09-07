# GCP-0076 Refactor Expert Decision Notes

## Modularity Audit

| File | Lines | Functions | Decision |
|---|---:|---:|---|
| `tools/golazo_capabilities.py` | 251 | 9 | Above 200 but below thresholds; registry resolution and query actions form one cohesive lifecycle. |
| `tools/golazo_bootstrap.py` | 305 before cleanup | 3 | Existing broad bootstrap orchestrator; moved registry imports to module scope. Further splitting is unrelated. |
| `tools/golazo_create_workitem.py` | 96 | 2 | Focused; no split needed. |
| `tools/golazo_status.py` | 353 | 12 | Existing status aggregation module; this change is a two-line resolver substitution. No behavior-neutral extraction is warranted here. |
| `tests/test_gcp_bootstrap.py` | 500 | 37 | Existing behavior-grouped regression suite; only capability expectations changed. |
| `tests/test_gcp_create_workitem.py` | 396 | 39 | Existing suite; only two capability tests changed. |
| `tests/test_gcp_status.py` | 570 | 34 | Existing suite; registry-hint section remains logically grouped. |
| `tests/test_package_init_version.py` | 24 | 3 | Ruff-only import cleanup. |
| `tests/test_gcp0076_canonical_capability_registry.py` | 127 | 7 | Focused and below thresholds. |
| `WorkItems/capabilities.yaml` | 90 | 0 | Five cohesive capability cards. |

## Refactor Decision

Kept registry path helpers with capability operations because they own the same YAML lifecycle and remain below the function threshold. Extracting them would add a module boundary without reducing complexity. Moved bootstrap imports to module scope for clearer coupling.

## Validation

- Bootstrap plus focused policy tests: 42 passed.
- Repository-wide Ruff: passed.
- Full suite before refactor: 551 passed, 3 optional skips.
