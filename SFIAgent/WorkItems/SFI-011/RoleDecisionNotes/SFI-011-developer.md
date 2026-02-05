# SFI-011: Developer Role Notes

## Implementation Summary

Implemented Column Toggle UI for the drill-down modal in the SFI Reporter Tkinter application.

## TDD Approach

### Red Phase (Tests Written First)
Created 7 tests in `TestColumnToggle` class in `test_tk_app.py`:
1. `test_required_columns_defined` - Verifies REQUIRED_COLUMNS constant exists
2. `test_get_available_columns` - Tests extracting unique columns from items
3. `test_filter_item_columns` - Tests filtering item to visible columns only
4. `test_select_all_columns` - Tests select all returns all available columns
5. `test_clear_all_keeps_required` - Tests clear all preserves required columns
6. `test_validate_visible_columns` - Tests validation adds missing required columns
7. `test_column_display_names` - Verifies display names mapping exists

### Green Phase (Implementation)
Implemented the following in `tk_app.py`:

**Constants:**
- `REQUIRED_COLUMNS` - Columns that cannot be hidden: `['title', 'dueDate', 'SlaType']`
- `COLUMN_DISPLAY_NAMES` - Human-readable display names for 20+ API column names

**Helper Functions:**
- `get_available_columns(items)` - Extract unique column names from item list
- `filter_item_columns(item, visible)` - Filter item dict to visible columns only
- `select_all_columns(available)` - Return all available columns
- `clear_all_columns(available)` - Return only required columns
- `validate_visible_columns(visible)` - Ensure required columns are included

**UI Components:**
- `ColumnSelectorDialog` - Modal dialog with scrollable checkboxes for column selection
  - Class variable `_visible_columns` for session persistence
  - Select All / Clear All buttons
  - Required columns are disabled (always checked)
  - Apply/Cancel buttons
  - `get_visible_columns()` / `reset_visible_columns()` class methods

**DetailModal Modifications:**
- Added `_items` instance variable to store items for refresh
- Added `_tree_container` for dynamic tree rebuilding
- Added `_build_tree()` method - Builds/rebuilds treeview with current column settings
- Added "Columns" button in footer (left of Close button)
- Added `_open_column_selector()` method
- Added `_on_columns_changed()` callback to refresh tree when columns change

## Decisions Made

1. **Session-only persistence**: Column visibility is stored in class variable, resets on app restart
2. **Dynamic column mapping**: Tree column IDs are snake_case, mapped from API column names
3. **Graceful fallback**: If visible columns not set, shows all available columns
4. **Column filtering**: Only shows columns that exist in current data + required columns

## Test Results

```
62 passed in 4.04s
```

All tests pass including the 7 new column toggle tests and 55 existing tests.

## Files Modified

- `SFIReporter/src/sfi_reporter/tk_app.py` - Added constants, helper functions, ColumnSelectorDialog, modified DetailModal
- `SFIReporter/tests/test_tk_app.py` - Added TestColumnToggle class with 7 tests (done in prior session)

## Acceptance Criteria Status

| AC | Description | Status |
|----|-------------|--------|
| AC1 | Columns button in modal | ✅ Added in footer |
| AC2 | Checkboxes for each column | ✅ ColumnSelectorDialog |
| AC3 | Unchecking hides column | ✅ _build_tree() rebuilds |
| AC4 | Visibility persists in session | ✅ Class variable |
| AC5 | Select All / Clear All buttons | ✅ Implemented |
| AC6 | Required columns can't be hidden | ✅ Disabled checkboxes |
