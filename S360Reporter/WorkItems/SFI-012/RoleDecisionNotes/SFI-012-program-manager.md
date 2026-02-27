# SFI-012: Program Manager Role Notes

## Design Decisions

### Approach Selection
Chose "(empty)" text suffix over alternatives:
- Gray text could look disabled
- Hiding columns removes user visibility
- Separate section adds UI complexity

### Empty Detection Logic
Defined "empty" as:
- None
- Empty string (after strip)
- Empty list

Did NOT include:
- Zero (0 is valid data)
- False (boolean False is valid data)
- String "None" (could be intentional)

### Performance
- Single pass through item dict (O(n))
- No caching needed - computed fresh each open
- Typical items have ~30 columns - negligible time

## Files to Modify
1. `tk_app.py` - Add `get_empty_columns()` function
2. `tk_app.py` - Update `ColumnSelectorDialog.__init__` signature
3. `tk_app.py` - Update `ItemDetailsModal._open_column_selector()` to pass empty columns
4. `tk_app.py` - Update `ColumnSelectorDialog._create_widgets()` to show annotation
