# SFI-023 — Developer Decision Notes

## TDD Approach
- **Red phase**: 22 tests written covering all 18 test cases from SFI-023-Test-Cases.md (some grouped). All 13 new-feature tests failed as expected; 9 existing-behavior tests passed.
- **Green phase**: Production code implemented in `tk_app.py`. All 22 tests pass.
- **Regression**: Full suite 211 tests pass, 0 failures.

## Implementation Decisions

### Story C: SLA Status Fix + ETA Status Column
- **Root cause**: `DetailModal._create_widgets` used `sla_map = {0: ..., 1: ..., 2: ...}` (int keys) but the S360 API returns string values like `"OutOfSla"`, `"InSla"`, `"Approaching"`.
- **Fix**: Created `_resolve_sla_display()` function using `_SLA_DISPLAY_MAP` that handles int keys, string-numeric keys (`"0"`, `"1"`, `"2"`), and API string variants (`"InSla"`, `"OutOfSla"`, `"Approaching"`). Returns `""` for `None`.
- **ETA Status column**: Added `"eta_status"` to `DetailModal.COLUMNS` class attribute. Created `_resolve_eta_status()` helper. Column shows `item.get('EtaStatus')` value.
- **No new dependencies**.

### Story A: Expand Home ETA Button
- **`_on_update_etas`**: Removed early-return when no invalid items. Now always opens `EtaModeDialog` when items exist.
- **`EtaModeDialog`**: Changed signature from `(parent, invalid_count, on_choice)` to `(parent, total_count, invalid_count, on_choice)`. Header shows both counts. Bulk button disabled when `invalid_count == 0`.
- **Manual path**: Receives all items sorted invalid-first using `sorted(items, key=lambda it: 0 if is_invalid_eta(...) else 1)`.
- **Bulk path**: Still receives only `get_items_needing_eta_update(items)` result (invalid only).

### Story B: Drill-Down ETA Button
- **`DetailModal`**: Added `on_eta_complete` callback parameter. Added `eta_btn` ("📋 Update ETAs") to button bar.
- **`_on_detail_update_etas`**: Opens `ManualEtaReviewDialog` with the drill-down's item list.
- **`_on_detail_eta_complete`**: Mutates items in-memory, calls `_refresh_items()` to repopulate tree, then invokes `on_eta_complete` callback so home screen refreshes.
- **`_refresh_items`**: New method that clears and repopulates the tree from `self._items`.
- All 4 existing `DetailModal` call sites in `tk_app.py` now pass `on_eta_complete=self._on_eta_update_complete`. The query_builder.py call site remains unchanged (uses default `None`).

### Refactoring: `_build_tree` extracted
- The treeview creation logic was extracted from `_create_widgets` into `_build_tree` to enable reuse by `_refresh_items`.

## Files Changed
- `src/sfi_reporter/tk_app.py` — all production changes
- `tests/test_sfi_023.py` — new test file (22 tests)

## Test Results
```
211 passed in 0.83s
```
