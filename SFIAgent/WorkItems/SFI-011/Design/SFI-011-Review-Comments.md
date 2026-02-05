# SFI-011: Design Review Comments

## Overall Assessment
✅ **APPROVED** - Design is clear and implementable.

## Strengths
1. Good UI mockup showing button placement and dialog layout
2. Required columns concept prevents user from hiding critical info
3. Session persistence via class variable is simple and effective
4. Aligns with S360 portal pattern users are familiar with

## Recommendations

### R1: Column Discovery from Data
**Issue**: Design references SFI-010 column cache, but drill-down modal should discover columns from actual data rows, not cache.
**Recommendation**: Build column list from `set(key for item in items for key in item.keys())`

### R2: Checkbox Scrolling
**Issue**: With 20+ columns, dialog may be too tall
**Recommendation**: Use scrollable frame for checkboxes

### R3: Apply Without OK
**Issue**: Design shows OK button, but immediate apply on checkbox change is more responsive
**Recommendation**: Consider immediate apply (no OK button needed)

## Edge Cases to Test

1. **No items in drill-down** → Column selector still works with available columns
2. **Different columns per item** → Union of all column keys shown
3. **User clears all then opens selector** → Required columns still checked
4. **Reopening modal** → Remembers column visibility from previous open

## Approved for Implementation
Design is sound. Proceed with R2 (scrollable frame) incorporated.

---

## Architect Notes

### Architectural Alignment
✅ **APPROVED** - Follows existing patterns in tk_app.py.

### API Contracts

**Constants**:
```python
REQUIRED_COLUMNS: list[str] = ['title', 'dueDate', 'SlaType']

COLUMN_DISPLAY_NAMES: dict[str, str] = {
    'title': 'Title',
    'dueDate': 'Due Date',
    'SlaType': 'SLA Type',
    'ActionOwnerName': 'Action Owner',
    'EtaDate': 'ETA Date',
    'EtaStatus': 'ETA Status',
    'S360_ServiceTreeServiceName': 'Service Name',
    ...
}
```

**Helper Functions**:
```python
def get_available_columns(items: list[dict]) -> list[str]:
    """Get union of all column keys from items."""

def filter_item_columns(item: dict, visible: list[str]) -> dict:
    """Filter item to only visible columns."""

def validate_visible_columns(visible: list[str]) -> list[str]:
    """Ensure required columns are always present."""

def select_all_columns(available: list[str]) -> list[str]:
    """Return all available columns."""

def clear_all_columns(available: list[str]) -> list[str]:
    """Return only required columns."""
```

**Class Methods on DrillDownModal**:
```python
@classmethod
def get_visible_columns(cls) -> Optional[list[str]]:
    """Get current visible columns (None = defaults)."""

@classmethod
def set_visible_columns(cls, columns: list[str]) -> None:
    """Set visible columns for session."""

@classmethod
def reset_visible_columns(cls) -> None:
    """Reset to defaults."""
```

### Security & Privacy
✅ No security concerns - UI-only feature, no data exposure

### Coupling Analysis
- **Low coupling**: Column selector is a new dialog, minimal changes to existing DrillDownModal
- **Blast radius**: Isolated to drill-down modal display

### Tkinter Considerations
- Use `ttk.Frame` with `Canvas` for scrollable checkbox list
- `Checkbutton` with `BooleanVar` for state management
- Modal dialog via `Toplevel` with `grab_set()`

### Recommendations
1. Sort columns alphabetically in selector (except required at top)
2. Use `format_field_label()` from existing code for display names

