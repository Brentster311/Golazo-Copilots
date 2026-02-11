# SFI-026 Refactor Expert Decision Notes

## Assessment

Reviewed all new and modified code in `tk_app.py` for SFI-026. The implementation is already well-structured — no significant refactoring opportunities identified.

## Code Quality Observations

| Area | Status | Notes |
|------|--------|-------|
| `OrgAncestry` NamedTuple | Clean | Lightweight, idiomatic Python |
| `get_org_mapping()` | Acceptable | `_resolve_display_name` helper is appropriately scoped inside the function |
| `aggregate_by_owner()` | Clean | `_get_level1()` local helper handles dual-format mapping cleanly |
| `aggregate_by_level2()` | Clean | Similar loop pattern to aggregate_by_owner but distinct output structure — not worth abstracting |
| `collect_services_for_owner()` | Clean | Clear intent, handles both formats |
| `_update_tables()` manager branch | Acceptable complexity | Builds hierarchy dict then renders — could extract hierarchy-building into a helper but the section is cohesive and well-commented |
| `_on_service_double_click()` | Clean | Dual map lookup (L2 first, then L1) is clear |

## Considered but Declined

1. **Extract hierarchy builder from `_update_tables`**: The hierarchy dict construction (~20 lines) could be extracted to a standalone function for testability. Declined because it's tightly coupled to the treeview rendering logic and extracting it would complicate the data flow without meaningful benefit.

2. **Unify `aggregate_by_owner` and `aggregate_by_level2`**: Both iterate items and accumulate stats. Declined because they produce fundamentally different key structures (`str` vs `tuple[str, str]`) and have different filtering logic.

3. **Module-level `get_level1()` utility**: Currently a nested function in `aggregate_by_owner`. Declined because it's only used in one place — promoting it adds clutter.

## Conclusion

No refactoring applied. All 26 tests remain green. Code follows existing repo patterns and is clean enough for a first iteration.
