# SFI-011: Test Cases

## Test Coverage Matrix

| Acceptance Criteria | Test Case(s) |
|---------------------|--------------|
| AC1: Columns button in modal | TC01 |
| AC2: Checkboxes for each column | TC02, TC03 |
| AC3: Unchecking hides column | TC04 |
| AC4: Visibility persists in session | TC05 |
| AC5: Select All / Clear All | TC06, TC07 |
| AC6: Required columns can't be hidden | TC08 |

---

## Unit Tests

### TC01: Columns Button Exists
**File**: `test_tk_app.py`
**Function**: `test_drilldown_has_columns_button`
```python
def test_drilldown_has_columns_button():
    """Drill-down modal has a Columns button in header"""
    # Verify DrillDownModal has columns_button attribute
    # Verify button text is "Columns" or has gear icon
```

### TC02: Column List From Data
**File**: `test_tk_app.py`
**Function**: `test_get_available_columns`
```python
def test_get_available_columns():
    """Available columns are derived from data items"""
    from sfi_reporter.tk_app import get_available_columns
    
    items = [
        {'title': 'A', 'dueDate': '2026-01-01', 'custom1': 'val'},
        {'title': 'B', 'dueDate': '2026-01-02', 'custom2': 'val'},
    ]
    columns = get_available_columns(items)
    
    assert 'title' in columns
    assert 'dueDate' in columns
    assert 'custom1' in columns
    assert 'custom2' in columns
```

### TC03: Required Columns Constant
**File**: `test_tk_app.py`
**Function**: `test_required_columns_defined`
```python
def test_required_columns_defined():
    """Required columns list exists and contains essential fields"""
    from sfi_reporter.tk_app import REQUIRED_COLUMNS
    
    assert 'title' in REQUIRED_COLUMNS
    assert 'dueDate' in REQUIRED_COLUMNS
    assert 'SlaType' in REQUIRED_COLUMNS
```

### TC04: Filter Columns
**File**: `test_tk_app.py`
**Function**: `test_filter_visible_columns`
```python
def test_filter_visible_columns():
    """Items are filtered to only visible columns"""
    from sfi_reporter.tk_app import filter_item_columns
    
    item = {'title': 'Test', 'dueDate': '2026-01-01', 'extra': 'hidden'}
    visible = ['title', 'dueDate']
    
    result = filter_item_columns(item, visible)
    
    assert result == {'title': 'Test', 'dueDate': '2026-01-01'}
```

### TC05: Session Persistence
**File**: `test_tk_app.py`
**Function**: `test_column_visibility_persists`
```python
def test_column_visibility_persists():
    """Column visibility persists across modal instances"""
    from sfi_reporter.tk_app import DrillDownModal
    
    # Set visibility on class
    DrillDownModal.set_visible_columns(['title', 'dueDate'])
    
    # Verify it persists
    assert DrillDownModal.get_visible_columns() == ['title', 'dueDate']
    
    # Reset for other tests
    DrillDownModal.reset_visible_columns()
```

### TC06: Select All
**File**: `test_tk_app.py`
**Function**: `test_select_all_columns`
```python
def test_select_all_columns():
    """Select All enables all columns"""
    from sfi_reporter.tk_app import select_all_columns
    
    available = ['title', 'dueDate', 'SlaType', 'extra1', 'extra2']
    result = select_all_columns(available)
    
    assert result == available
```

### TC07: Clear All Keeps Required
**File**: `test_tk_app.py`
**Function**: `test_clear_all_keeps_required`
```python
def test_clear_all_keeps_required():
    """Clear All keeps required columns checked"""
    from sfi_reporter.tk_app import clear_all_columns, REQUIRED_COLUMNS
    
    available = ['title', 'dueDate', 'SlaType', 'extra1', 'extra2']
    result = clear_all_columns(available)
    
    # Only required columns remain
    for col in REQUIRED_COLUMNS:
        assert col in result
    assert 'extra1' not in result
    assert 'extra2' not in result
```

### TC08: Required Cannot Be Unchecked
**File**: `test_tk_app.py`
**Function**: `test_required_columns_cannot_be_hidden`
```python
def test_required_columns_cannot_be_hidden():
    """Required columns cannot be removed from visible list"""
    from sfi_reporter.tk_app import validate_visible_columns, REQUIRED_COLUMNS
    
    # Try to hide all columns
    visible = []
    result = validate_visible_columns(visible)
    
    # Required columns are always present
    for col in REQUIRED_COLUMNS:
        assert col in result
```

---

## Manual Test Checklist

- [ ] Open drill-down modal, click "Columns" button
- [ ] Verify all available columns shown with checkboxes
- [ ] Uncheck a column, verify it disappears from table
- [ ] Close and reopen modal, verify column still hidden
- [ ] Click "Clear All", verify only Title/Due Date/SLA visible
- [ ] Click "Select All", verify all columns visible
- [ ] Try to uncheck "Title" - should not allow
