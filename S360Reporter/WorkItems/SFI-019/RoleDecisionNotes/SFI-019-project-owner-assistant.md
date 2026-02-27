# SFI-019 Project Owner Assistant Notes

## Scope Decision

The user's request has two distinct user-observable outcomes:
1. Bulk ETA update from the main screen (Manual or Bulk mode)
2. Individual ETA update from the detail view

These are kept in a **single story** because:
- They share the same API call (`SaveETAsByIds`), same payload model, and same ETA-proposal logic
- The individual update is a strict subset of the bulk workflow (single item vs. many)
- Splitting would force duplicate implementation of the save/refresh flow

Total acceptance criteria: 6 (within the 3–7 limit).

## Reference Analysis

Studied `C:\Users\Brent\source\repos\Compute-Insights-Sauron\src\Tools\SFI_Agent`:
- `eta_processor.py` — `ETAProcessor` with `propose_eta_date()` (end-of-month, ≥2 weeks)
- `api_client.py` — `save_eta()` posts to `/ActionItems/SaveETAsByIds`
- `main.py` — `S360ETAUpdater.bulk_update_unified_workflow()` with manual/automated modes
- `config.py` — `DEFAULT_SLA_TYPE = "InSla"`, Kusto query for filtering

**Key payload difference**: Sauron uses `{ ETADate, UserStatus, KpiId, ActionItems: [...] }`, while `accia-s360` uses `{ items: [{ KpiId, Eta, ... }] }`. The accia-s360 format may not match the real API. This is flagged as an assumption and will be validated by the architect.

## Must-Ask Checklist

All resolved from prior SFI work items:
- [x] Interface type: tkinter GUI (S360Reporter)
- [x] Target platform: Windows
- [x] Data persistence: S360 cloud API (write) + local cache (read)
- [x] User type: Technical (engineers managing SFI action items)
