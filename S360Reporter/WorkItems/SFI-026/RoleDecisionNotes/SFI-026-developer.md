# SFI-026 Developer Decision Notes

## Summary

Implemented 2-level owner grouping in the services table per the approved design. TDD red-green cycle completed successfully: 26 new tests all pass, 233 existing tests pass with no regressions.

## Key Decisions

### 1. OrgAncestry NamedTuple
- Added `OrgAncestry(level1: str, level2: Optional[str])` as a lightweight NamedTuple
- Preserves backward compatibility: `aggregate_by_owner` transparently handles both OrgAncestry tuples and legacy strings via `_get_level1()` helper

### 2. Remaining-Based Depth Detection
- `get_org_mapping()` computes `remaining = len(managers) - 1 - manager_idx` to determine depth
  - `remaining == 0` → direct report → `OrgAncestry(self, None)`
  - `remaining == 1` → sub-report → `OrgAncestry(direct_name, owner_name)`
  - `remaining >= 2` → deep (capped at L2) → `OrgAncestry(direct_name, level2_name)`
- Name resolution via `_resolve_display_name()` helper performs search-by-alias with fallback to alias

### 3. Separate Level-2 Aggregation
- New `aggregate_by_level2()` produces `{(level1, level2): stats}` dict
- Filters out `level2=None` entries and "Unknown Owner" to keep the hierarchy clean
- Kept separate from `aggregate_by_owner()` to preserve existing API surface

### 4. Dual Drill-Down Maps
- `_owner_id_map` handles level-1 rows (backward compatible)
- `_owner_l2_map` handles level-2 sub-rows
- `_on_service_double_click()` checks `_owner_l2_map` first, then `_owner_id_map`
- `collect_services_for_owner()` handles subtree collection for both levels

### 5. Hierarchy Detection in _update_tables
- `has_level2` flag detects whether any OrgAncestry in org_mapping has non-None level2
- If true: renders 3-tier treeview (L1 parent → L2 sub-row → services)
- If false: renders existing 1-level treeview (backward compatible for 1-level managers)

## Test Results

| Suite | Passed | Failed | Notes |
|-------|--------|--------|-------|
| test_sfi_026.py (new) | 26 | 0 | All SFI-026 tests green |
| Full test suite | 233 | 4 | Pre-existing failures (accia_s360 missing, Tcl init) |
| Errors | — | 19 | Pre-existing fixture/import issues |

## Files Changed
- `src/sfi_reporter/tk_app.py` — OrgAncestry, get_org_mapping, aggregate_by_owner, aggregate_by_level2, collect_services_for_owner, _update_tables, _on_service_double_click, do_refresh
- `tests/test_sfi_026.py` — 26 new tests across 6 categories

## Risks & Mitigations
- **Risk**: Display name resolution adds API calls per owner → mitigated by existing ThreadPoolExecutor parallelism
- **Risk**: Legacy callers passing string org_mapping → mitigated by `_get_level1()` dual-format handler
- **Risk**: L2 drill-down ambiguity → mitigated by separate `_owner_l2_map` checked before `_owner_id_map`
