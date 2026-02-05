# SFI-012: Test Cases

## Unit Tests

### Test Class: TestEmptyColumnDetection

#### TC1: test_get_empty_columns_none_value
**Description**: Column with None value is detected as empty
```python
item = {'col1': None, 'col2': 'value'}
empty = get_empty_columns(item)
assert 'col1' in empty
assert 'col2' not in empty
```

#### TC2: test_get_empty_columns_empty_string
**Description**: Column with empty string is detected as empty
```python
item = {'col1': '', 'col2': 'value'}
empty = get_empty_columns(item)
assert 'col1' in empty
```

#### TC3: test_get_empty_columns_whitespace_string
**Description**: Column with whitespace-only string is detected as empty
```python
item = {'col1': '   ', 'col2': 'value'}
empty = get_empty_columns(item)
assert 'col1' in empty
```

#### TC4: test_get_empty_columns_empty_list
**Description**: Column with empty list is detected as empty
```python
item = {'col1': [], 'col2': ['item']}
empty = get_empty_columns(item)
assert 'col1' in empty
assert 'col2' not in empty
```

#### TC5: test_get_empty_columns_zero_not_empty
**Description**: Column with zero is NOT detected as empty (0 is valid data)
```python
item = {'col1': 0, 'col2': 'value'}
empty = get_empty_columns(item)
assert 'col1' not in empty
```

#### TC6: test_get_empty_columns_false_not_empty
**Description**: Column with False is NOT detected as empty (False is valid data)
```python
item = {'col1': False, 'col2': 'value'}
empty = get_empty_columns(item)
assert 'col1' not in empty
```

#### TC7: test_get_empty_columns_string_none
**Description**: Column with string "None" is detected as empty
```python
item = {'col1': 'None', 'col2': 'value'}
empty = get_empty_columns(item)
assert 'col1' in empty
```

## Integration Tests

### TC8: test_column_selector_shows_empty_annotation
**Description**: ColumnSelectorDialog displays "(empty)" suffix for empty columns
```python
# Would require GUI testing - verify manually or mock
# Expected: checkbox text shows "Column Name (empty)" for empty columns
```

### TC9: test_column_selector_no_annotation_for_non_empty
**Description**: ColumnSelectorDialog does NOT show "(empty)" for non-empty columns
```python
# Would require GUI testing - verify manually
# Expected: checkbox text shows "Column Name" without suffix for non-empty columns
```

## Acceptance Criteria Coverage

| AC | Test Cases |
|----|------------|
| AC1: Visual annotation on empty columns | TC8 |
| AC2: "(empty)" indicator | TC1-TC7 |
| AC3: Empty columns toggleable | (inherent - no disable logic) |
| AC4: Non-empty columns unannotated | TC5, TC6, TC9 |
