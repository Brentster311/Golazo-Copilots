# SFI-037 Developer Decision Notes

## Implementation Summary

Added a "Cost (min)" column to all three table views (Services, Programs, Actions/KPIs) in SFI Reporter, sourced from the S360 `query_kpi_costs` API.

## TDD Cycle

### Red Phase
- Created `tests/test_sfi_037.py` with 15 tests across 3 test classes:
  - `TestFetchKpiCosts` (4 tests): API call, partial data, failure fallback, empty list
  - `TestComputeRowCost` (6 tests): service/kpi/program/owner row cost sums, item cost
  - `TestCostFormatting` (5 tests): dash for None, zero, thousands separator, rounding, missing KPI
- All 15 tests failed initially (red)

### Green Phase
- Implemented 3 functions in `data.py`: `fetch_kpi_costs()`, `compute_row_cost()`, `format_cost()`
- All 15 tests pass

## Files Changed

### `SFIReporter/src/sfi_reporter/data.py`
- Added `fetch_kpi_costs(kpi_ids) -> dict[str, float]`: Calls `client.query_kpi_costs()`, returns `{kpi_id: avg_cost_min}`, empty dict on failure
- Added `compute_row_cost(items, kpi_cost_map) -> float | None`: Sums per-item cost from map; returns None if no KPI has data
- Added `format_cost(value) -> str`: Rounds to int with thousands separator, or "—" for None

### `SFIReporter/src/sfi_reporter/services.py`
- `do_refresh()`: Added `fetch_kpi_costs` import and call after building kpi_names
- Stats dicts (`service_stats`, `kpi_stats`, `program_stats`) now initialize with `'cost': 0.0`
- Each item loop accumulates `item_cost = kpi_cost_map.get(kpi_id, 0.0)` into stats
- Added `kpi_cost_map` to returned data dict

### `SFIReporter/src/sfi_reporter/app.py`
- Added `from sfi_reporter.data import format_cost`
- Added "cost" column (heading "Cost (min)", width=80) to all 3 SortableTreeview definitions
- Updated `_compute_group_stats()` closure to accumulate `cost`
- Updated `root_stats` aggregation to include `cost`
- Updated all 8 `.insert()` calls to include `format_cost(stats.get('cost'))` as 5th value

## Test Results
- 15/15 SFI-037 tests pass
- 147/150 full suite pass (3 pre-existing failures in `test_sfi_026_live.py` unrelated to this change)

## Design Decisions
- **Graceful degradation**: If `query_kpi_costs` API fails, cost shows "—" rather than breaking the UI
- **Cost accumulation in services.py**: Cost is accumulated per-item alongside count/sla/invalid_eta, keeping the existing stats pattern
- **Float → int display**: Costs are rounded to nearest integer for readability since minutes are the unit
- **No new dependencies**: Used existing `S360Client.query_kpi_costs()` endpoint
