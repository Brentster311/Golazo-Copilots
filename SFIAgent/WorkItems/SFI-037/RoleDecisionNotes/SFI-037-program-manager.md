# SFI-037 — Program Manager Decision Notes

## Approach Selection

Chose the simplest possible approach: one API call during refresh, store as a flat dict, compute row totals in the UI layer. This avoids any N+1 patterns and fits neatly into the existing refresh → cache → display pipeline.

## Key Decisions

1. **Single fetch per refresh**: `query_kpi_costs(all_kpi_ids)` returns all costs in one call. No per-row or per-item fetching.
2. **Minutes as unit**: The API returns both `AverageCostInMin` (numeric) and `AverageCost` (label like "HalfDay"). We use the numeric value because it's summable and sortable.
3. **Column placement**: "Cost (min)" added as the last data column before any action columns, consistent with SLA Status and ETA Status placement.
4. **Graceful degradation over failure**: Cost is informational, not critical. If the API fails, the app continues normally with "—" in cost columns.

## Risk Assessment

Low risk feature — additive only, no existing behavior changes, no new dependencies. The cost API is a stable S360 endpoint already used by the S360 web portal.
