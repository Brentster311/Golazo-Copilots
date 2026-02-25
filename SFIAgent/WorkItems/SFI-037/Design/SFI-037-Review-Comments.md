# SFI-037 — Review Comments

## Design Review

### Strengths
- Simple, additive change — no existing behavior modified.
- Single API call avoids performance concerns.
- Graceful degradation is well-planned.
- Reuses existing cache infrastructure.

### Issues / Recommendations

#### [RC-1] Column Sorting (Minor)
The design doesn't mention whether "Cost (min)" is sortable. All other numeric columns in SFI Reporter are sortable. **Recommendation:** Make the column sortable by integer value (not string), with "—" entries sorting to bottom.

#### [RC-2] Format Clarification (Minor)
Design says "integer (e.g., 1,054)" — confirm this means locale-aware thousands separator. **Recommendation:** Use `f"{cost:,.0f}"` for display, store raw int for sorting.

#### [RC-3] Cost When Item Count is Zero (Edge Case)
A service could appear in the summary with 0 action items (all resolved). Cost should be 0, not "—". "—" should only appear when the KPI has no cost data. **Recommendation:** Distinguish "no cost data" (`None`) from "zero cost" (`0`).

#### [RC-4] Capability Impact Coverage
Impact analysis shows 7 capabilities affected. The `reporter-query-builder` is transitively affected — if "Cost (min)" becomes a filterable field in the future, that's a separate work item. For now, the column should appear in the column toggle but not in the filter builder. **Recommendation:** Document this explicitly.

## Domain Expert Guidance

No domain expertise was required (documented in domain-expert decision notes). No additional guidance needed.

---

## Architect Notes

### Architecture Alignment — Approved

The feature fits cleanly into the existing layered architecture:

```
app.py (_update_tables)  →  reads kpi_cost_map from data dict
services.py (do_refresh)  →  calls fetch_kpi_costs(), stores in data dict
data.py (fetch_kpi_costs)  →  new function, calls client.query_kpi_costs()
```

### Contract Review

**New contract in `data.py`:**
```python
def fetch_kpi_costs(kpi_ids: list[str]) -> dict[str, float]:
    """Fetch KPI cost map. Returns {kpi_id: average_cost_in_min}.
    Returns empty dict on failure (never raises)."""
```

**Data dict additions (services.py → cache):**
- `kpi_cost_map: dict[str, float]` — added to the data dict returned by `do_refresh()` and written to cache.

**UI changes (app.py):**
- New column `"cost"` added to `services_tree`, `action_tree`, and `program_tree` Treeview definitions.
- Row values include cost as the 5th tuple element.
- Stats dicts (`service_stats`, `kpi_stats`, `program_stats`, `owner_stats`) gain a `'cost'` key during computation.

### Security & Privacy
- No new credentials, tokens, or PII. Cost data is organizational metadata.
- Cache file already stores service/KPI data; cost is additive.

### Failure Isolation
- `fetch_kpi_costs()` wraps the API call in try/except and returns `{}` on failure.
- All cost formatting handles `None`/missing with "—".
- No existing functionality is affected if cost fetch fails.

### Cache Backward Compatibility
- Old caches without `kpi_cost_map` key → `data.get('kpi_cost_map', {})` returns empty dict → all costs show "—" until next refresh. No migration needed.

### Performance
- Single POST call with all KPI IDs (typically 10-20). Observed latency: ~1-2s.
- No additional API calls per row or per view.

### Capability Impact Verified
All 7 affected capabilities reviewed:
- **reporter-data**: New `fetch_kpi_costs()` function — contract-compatible
- **reporter-tk-app** (now `app.py`): Column additions — backward-compatible
- **reporter-cache**: No changes needed (plain dict serialization)
- **reporter-tests**: New test file required
- Others (eta-logic, query-builder, build): No impact
