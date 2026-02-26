# SFI-038 — Developer Decision Notes

## Implementation Summary
- Created `kpi_lookup.py` with `load_kpi_scores()`, `compute_kpi_score()`, `enrich_stats_with_scores()`, `compute_service_scores()`, `compute_program_scores()`, and `format_score()`.
- Integrated score computation directly into `do_refresh()` item loop in `services.py` — each item contributes its KPI score to `kpi_stats`, `service_stats`, and `program_stats` in a single pass.
- Added `"score"` column to all 3 Treeview tables in `app.py`, including manager tree hierarchy rollup via `_compute_group_stats`.
- Dual-key lookup (name + KPIID) for resilience against name mismatches.

## TDD Cycle
- 14 tests written first (all failed - red phase)
- Implementation created (all passed - green phase)
- Full test suite: 370 passed, 3 pre-existing live test failures (unrelated), 1 skipped

## Key Decisions
- Scores computed inline in the existing `do_refresh` loop rather than as a post-processing step — avoids a second pass over items.
- `_kpi_name` injected onto each item row for potential downstream use.
- Uses `encoding="utf-8-sig"` for BOM handling.
