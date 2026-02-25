# SFI-037 — Project Owner Assistant Decision Notes

## Decisions Made

1. **Interface type:** Tkinter desktop app (SFI Reporter) — already established, no ambiguity.
2. **Target platform:** Windows (existing PyInstaller .exe distribution).
3. **Data persistence:** JSON file cache (existing pattern in `reporter-cache`).
4. **User type:** Technical (ICs and managers using SFI Reporter).

## Scope Rationale

This is a single vertical slice: fetch cost data and display it in existing table views. No new views, no new API endpoints needed. The `query_kpi_costs()` SDK method already exists in both `s360_client` and `accia-s360`.

## Key Design Decisions

- **Cost = AverageCostInMin × item count per row.** The S360 API returns per-KPI average cost, not per-action-item cost. We multiply by the number of items in each row to get total estimated effort.
- **Single fetch, then lookup.** One `query_kpi_costs(all_kpi_ids)` call during refresh, stored as a `{kpi_id: cost_in_min}` dict. Each view computes row totals from this lookup.
- **Graceful degradation.** If cost API fails or a KPI has no cost data, show "—" instead of blocking.
- **Column name:** "Cost (min)" — concise, unambiguous, fits in table header.

## Assumptions Logged

All assumptions are labeled in the user story. No fundamental decisions were assumed — interface, platform, persistence, and user type are all known from the existing application.
