# Developer Decision Notes — SFI-029

## Summary

Implemented Top-Down Org Tree Grouping with N-Level Manager Hierarchy in `tk_app.py`, replacing the rigid 2-level (level1/level2) model with a variable-depth path-based model using `get_org_tree()`.

## Key Decisions

### 1. OrgAncestry Path Model
- **Changed**: `OrgAncestry(level1: str, level2: Optional[str])` → `OrgAncestry(path: tuple[str, ...])`
- **Rationale**: Variable-depth hierarchy can't be represented by 2 fixed fields. A tuple of manager names supports N levels naturally.
- **Semantics**: Root IS `path[0]`, path never empty, ICs never in path, `("Unknown Owner",)` for unresolved owners.

### 2. Single `get_org_tree()` Call
- **Changed**: Replaced N calls to `get_manager_chain()` (one per owner) with a single `get_org_tree(manager_alias)` call.
- **Rationale**: O(1) API calls vs O(n). The tree walk builds a `name_lookup` dict for case-insensitive matching.
- **Trade-off**: Owners not in the tree fall to "Unknown Owner" (same behavior as before, but now tree-driven).

### 3. Removed `aggregate_by_level2` Function
- **Changed**: Deleted ~50-line `aggregate_by_level2()` entirely.
- **Rationale**: Tree population now computes stats inline via recursive `_compute_group_stats`. No need for a separate aggregation pass.

### 4. `get_service_owners` Returns `dict` Not `tuple`
- **Changed**: Return type from `tuple[dict, dict]` → `dict[str, list[str]]`. Removed `resolve_alias()` inner function and S360 alias resolution phase.
- **Rationale**: Alias resolution was redundant with the tree-based approach. Simplifies all call sites.

### 5. Recursive Tree Population
- **Changed**: Manager-view treeview population uses recursive `_insert_group` + `_compute_group_stats` with `_group_path_map` replacing both `_owner_id_map` and `_owner_l2_map`.
- **Rationale**: N-level hierarchy requires recursive insertion. Only top-level groups auto-expand (`open=(depth == 0)`).

### 6. `collect_services_for_owner` Path-Prefix Matching
- **Changed**: Signature from `(owner_name, level, service_owners, org_mapping)` → `(path_prefix, service_owners, org_mapping)`.
- **Rationale**: Path-prefix tuple matching is cleaner and works at any depth without level parameters.

## Files Changed

| File | Changes |
|------|---------|
| `SFIReporter/src/sfi_reporter/tk_app.py` | OrgAncestry, serialization, get_org_mapping, get_service_owners, aggregate_by_owner, collect_services_for_owner, do_refresh, tree population, drill-down |
| `SFIReporter/tests/test_sfi_029.py` | 13 new tests (TDD) |
| `SFIReporter/tests/test_sfi_026.py` | Updated for path-based OrgAncestry (18 tests) |
| `SFIReporter/tests/test_sfi_028.py` | Simplified to dict-return test (1 test) |
| `SFIReporter/tests/test_sfi_026_live.py` | Updated live tests for path model (30 tests) |

## Test Results

```
SFI-029 tests: 13/13 passed
SFI-026 tests: 18/18 passed  
SFI-028 tests:  1/1  passed
Full suite (non-live): 241 passed, 1 pre-existing failure (Tcl/Tk), 19 pre-existing errors (pytest-mock)
```

## Risks & Mitigations

- **Live test `test_owner_stats_not_dominated_by_unknown`**: May fail if `get_org_tree` returns a shallow tree for alexhowells. Mitigated by the test being marked `@pytest.mark.live` (skipped in CI).
- **Cache backward compat**: Old caches with `level2_stats` key are gracefully handled (key dropped during deserialization). Old string-based org_mapping still works.
