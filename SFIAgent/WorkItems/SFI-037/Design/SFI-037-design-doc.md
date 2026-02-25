# SFI-037 — Design Doc: Add KPI Cost Column to SFI Reporter

## Summary

Add a "Cost (min)" column to every table view in SFI Reporter (Services, KPIs, Programs, Owners). Each row displays the total estimated remediation effort in minutes, computed as `AverageCostInMin × action_item_count` using data from the S360 `query_kpi_costs()` API.

## Problem Statement

Users currently see action-item counts and SLA status but have no visibility into the **engineering effort** required to remediate items. Managers cannot prioritize remediation work across services or owners by cost, and ICs cannot gauge the relative weight of their KPI backlog.

## Business Case

- **Why now:** The `query_kpi_costs()` endpoint is already wrapped in the SDK and returns per-KPI average remediation time. Surfacing this data is low-effort, high-value.
- **Impact:** Enables data-driven prioritization — managers can focus resources on the highest-cost KPIs/services first.
- **KPIs:** Adoption of the cost column in daily triage; reduction in time-to-decision for remediation planning.

## Stakeholders

| Role | Who | Interest |
|------|-----|----------|
| Product Owner | Brent | Defines scope, validates UX |
| Developer | Copilot | Implements feature |
| End Users | ICs & Managers | Consume cost data in table views |

## Functional Requirements

1. **Fetch costs on refresh:** During `do_refresh()`, call `query_kpi_costs(all_kpi_ids)` once for all unique KPI IDs discovered from the action items summary.
2. **Store as lookup:** Persist `kpi_cost_map: dict[str, float]` mapping `KpiId → AverageCostInMin` in the refresh data dict (and cache).
3. **Services view:** New "Cost (min)" column = sum of `kpi_cost_map[kpi_id] × item_count` for all KPIs in that service.
4. **KPIs view:** New "Cost (min)" column = `kpi_cost_map[kpi_id] × item_count` for that KPI row.
5. **Programs view:** New "Cost (min)" column = sum of item costs for all items in that program.
6. **Owners view (manager):** New "Cost (min)" column = sum of item costs for all items under that owner/group.
7. **Drill-down detail:** Individual items show their KPI's `AverageCostInMin` (per-item cost).
8. **Graceful degradation:** If cost API fails or KPI missing from response → show "—".

## Non-Functional Requirements

- Cost fetch adds ≤ 2s to refresh (single POST call).
- Cost data cached with existing JSON cache (same TTL).
- No new dependencies.

## Proposed Approach

### Phase 1: Data Layer (`data.py`)
- After fetching action items summary, extract all unique KPI IDs.
- Call `client.get_kpi_costs(kpi_ids)` → build `kpi_cost_map`.
- Include `kpi_cost_map` in the returned data dict.

### Phase 2: Cache (`cache.py`)
- `kpi_cost_map` is a plain dict — serializes naturally with existing JSON cache. No changes needed.

### Phase 3: UI (`tk_app.py`)
- Add "Cost (min)" as a new column in all four Treeview tables.
- During `_update_tables()`, compute row cost from `kpi_cost_map` and item counts.
- Format as integer (e.g., `1,054`) or "—" if unavailable.
- Include in column toggle feature (visible by default).

### Phase 4: Drill-down
- In detail modal item lists, add per-item cost column.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| Show `AverageCost` label (e.g., "HalfDay") | Less precise; can't sum across rows |
| Fetch costs per-item on demand | N+1 problem; slow |
| Compute costs client-side from heuristics | Inaccurate; S360 already provides this data |

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Cost API returns empty for some KPIs | Medium | Low | Show "—", don't break summation |
| Cost API is slow or times out | Low | Medium | Timeout at 15s; proceed without cost data |
| Cost values change over time | Low | Low | Refreshed each time user clicks Refresh |

## Open Questions

None — all requirements are clear from the user story and existing API behavior.

## Dependencies

- `accia-s360` SDK: `query_kpi_costs()` method (already exists).
- No new packages or external services.

## Migration / Rollout / Rollback

- **Rollout:** New column appears automatically after code update. No migration needed.
- **Rollback:** Revert code changes; column disappears. No data migration.
- **Cache compatibility:** Old caches without `kpi_cost_map` key → treated as "no cost data" (show "—" until next refresh).

## Observability Plan

- `logger.info("Fetched costs for %d/%d KPIs", found, total)` after cost fetch.
- `logger.warning("Cost API failed: %s", error)` on failure (non-blocking).

## Test Strategy Summary

- **Unit tests:** `test_sfi_037.py` — cost map building, row cost computation, missing data handling.
- **Integration:** Verify cost column appears in all four table views with mock data.
- **Edge cases:** Empty cost response, partial cost response, API timeout.
