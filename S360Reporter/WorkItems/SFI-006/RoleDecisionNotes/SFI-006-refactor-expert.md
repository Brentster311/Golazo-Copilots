# SFI-006: Refactor Expert Notes

## Date: 2026-02-04

## Code Smell Identified

**Issue**: The DetailModal class used `ttk.Treeview` instead of our custom `SortableTreeview`

**Location**: [tk_app.py#L215](GUI/src/sfi_reporter/tk_app.py#L215)

**Before**:
```python
tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
```

**After**:
```python
tree = SortableTreeview(main_frame, columns=columns, show="headings", height=15)
```

## Root Cause Analysis

This was a **copy-paste oversight** during initial implementation. When creating the modal's treeview, I used the base Tkinter class instead of reusing our custom sortable component.

## DRY Principle Violation

We already had `SortableTreeview` class that:
1. Extends `ttk.Treeview`
2. Adds click-to-sort on column headers
3. Handles both numeric and alphabetic sorting
4. Tracks sort direction per column

By not reusing it, we:
- Lost functionality (sorting)
- Created inconsistent UX (main tables sort, modal doesn't)
- Missed an opportunity for code reuse

## Fix Applied

Single-line change: `ttk.Treeview` → `SortableTreeview`

## Verification

- ✅ All 25 tests pass
- ✅ No behavior change (same data displayed)
- ✅ Enhanced behavior (sorting now works in modal)

## Lessons Learned

When creating new UI components, always check for existing reusable widgets before using base classes.
