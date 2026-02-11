# SFI-024 — Developer Decision Notes

## Changes Made

### Story A: "Update ETAs for N selected" in DetailModal
- Added `selected_eta_btn` to `DetailModal._create_widgets` button bar — starts disabled
- Bound `<<TreeviewSelect>>` event in `_build_tree` → calls `_on_tree_select`
- `_on_tree_select`: Updates button text with selection count, enables/disables accordingly
- `_on_selected_eta_update`: Gets selected items from `_item_map`, opens `ManualEtaReviewDialog` with selected subset, wired to existing `_on_detail_eta_complete` refresh chain

### Story B: "View Details" in ManualEtaReviewDialog
- Added "🔍 View Details" button to `_show_current` button row (between Skip and Cancel)
- `_view_details`: Opens `ItemDetailsModal(self, current_item)` for the item currently being reviewed

## Files Changed
- `src/sfi_reporter/tk_app.py` — production changes
- `tests/test_sfi_024.py` — 7 new tests

## Test Results
```
218 passed in 0.83s (0 failures, 0 regressions)
```
