# SFI-037 — Architect Decision Notes

## Architecture Review

Feature approved. Clean vertical slice through the existing 3-layer architecture (data → services → app). No new dependencies, no coupling changes, no blast radius concerns.

## Key Architectural Decisions

1. **New function in `data.py`** (`fetch_kpi_costs`): Keeps the data layer responsible for all S360 API calls. Returns a simple `dict[str, float]` — no new model classes needed.

2. **Cost computed during stats loop in `services.py`**: The `do_refresh()` function already iterates all items to build `service_stats`, `kpi_stats`, `program_stats`. Adding a `cost` accumulator to each stats dict is minimal and avoids a second pass.

3. **Column added to existing Treeview definitions**: All three trees (`services_tree`, `program_tree`, `action_tree`) get a `"cost"` column. The tuple of values grows from 4 elements to 5. This is the same pattern used when SLA Status was added.

4. **No new model class**: `kpi_cost_map` is a plain `dict[str, float]`. The API response is simple enough that a dataclass would be over-engineering.

## Contract Changes

| Layer | Change | Backward Compatible? |
|-------|--------|---------------------|
| `data.py` | New `fetch_kpi_costs(kpi_ids) → dict[str, float]` | Yes (new function) |
| `services.py` | `do_refresh()` returns `kpi_cost_map` in data dict | Yes (new key) |
| `services.py` | Stats dicts gain `'cost'` key | Yes (new key) |
| `app.py` | Treeview columns grow from 4 to 5 | Yes (additive) |
| `cache` | Data dict has new `kpi_cost_map` key | Yes (`dict.get()` default) |

## Risks Addressed

- **Cache format change**: Handled by `dict.get('kpi_cost_map', {})` — old caches degrade gracefully.
- **API failure**: `fetch_kpi_costs` returns `{}` — all downstream code handles empty map.
