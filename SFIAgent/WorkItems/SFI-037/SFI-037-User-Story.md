# SFI-037 — Add KPI Cost Column to SFI Reporter Table Views

**Status**: IMPLEMENTED

## User Story

- **Title:** Add KPI remediation cost to all table views
- **As a:** SFI Reporter user (IC or manager)
- **I want:** each row in every table view (Services, KPIs, Programs, Owners) to show the total estimated remediation cost in minutes for the action items in that row
- **So that:** I can quickly prioritize which groups of action items represent the most engineering effort to remediate

- **Out of scope:**
  - Changing the S360 API or accia-s360 SDK (already has `query_kpi_costs`)
  - Adding new cost-related API endpoints
  - Editing or writing back cost data to S360
  - Cost in currency (dollars) — this is time-cost only (minutes)

- **Assumptions:**
  - **Assumption (explicit):** The cost per action item is derived from the KPI's `AverageCostInMin` value returned by `query_kpi_costs()`. Each action item inherits its KPI's average cost. A row's total cost = count of action items × KPI average cost in minutes.
  - **Assumption (explicit):** Cost data is fetched once during refresh (alongside action item data) and cached with the rest of the data.
  - **Assumption (explicit):** KPIs that return no cost data display 0 or "—" rather than blocking the UI.
  - **Assumption (explicit):** The column header is "Cost (min)" and displays integer minutes.

- **Acceptance Criteria (bulleted, testable):**
  - [ ] After refresh, the app calls `query_kpi_costs()` for all unique KPI IDs found in the action items
  - [ ] The Services table shows a "Cost (min)" column with the sum of `AverageCostInMin × item_count` for each service row
  - [ ] The KPIs table shows a "Cost (min)" column with `AverageCostInMin × item_count` for each KPI row
  - [ ] The Programs table shows a "Cost (min)" column summing costs of all items in each program row
  - [ ] The Owners table (manager view) shows a "Cost (min)" column summing costs of all items under each owner/group row
  - [ ] Drill-down detail views show individual item cost in the item list
  - [ ] When a KPI has no cost data, its items show "—" for cost and do not break summation

- **Non-functional requirements:**
  - Cost fetch should not add more than ~2 seconds to refresh time (single API call for all KPI IDs)
  - Cost data should be cached alongside the existing refresh cache

- **Telemetry / metrics expected:**
  - Log the number of KPIs queried and how many returned cost data
  - Log if the cost API call fails (warn level, non-blocking)

- **Rollout / rollback notes:**
  - Feature is additive — new column appears in all views
  - If cost API is unavailable, column shows "—" for all rows (graceful degradation)

## Closure

- Summary of delivery: Added KPI cost retrieval/aggregation and surfaced `Cost (min)` across Services, Programs, Action Items, and owner-grouped manager views with graceful fallback behavior.
- Acceptance criteria validation: PASS (all functional and non-functional criteria met in implementation and tests).
- Future work items:
  - Consider extracting large `app.py` table-update logic into smaller methods.
  - Consider marking live tests to allow faster default test runs.
- Final status confirmation: **IMPLEMENTED**
