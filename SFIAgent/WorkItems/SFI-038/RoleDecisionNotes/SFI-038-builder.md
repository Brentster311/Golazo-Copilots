# SFI-038 — Builder Decision Notes

## Branch
- Branch: `SFI-039` (inherited from prior work — SFI-038 branch already existed from reverted work)

## Build Verification
- `pytest tests/ -q` → 370 passed, 3 pre-existing live test failures (unrelated), 1 skipped
- No build/compilation step needed (Python)
- No packaging changes required

## Commits
1. `SFI-038: Add KPI Score column to all tables` — kpi_lookup.py, services.py, app.py, test_sfi_038.py
2. `SFI-038: Add builder and remaining role notes` — all WorkItems/SFI-038/ artifacts
