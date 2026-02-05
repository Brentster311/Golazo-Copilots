# SFI-012: Design Document - Annotate Empty Columns in Column Picker

## Summary

Add visual annotations to the column picker dialog indicating which columns have no data for the current item, helping users make informed decisions about which columns to display.

## Problem Statement

When users open the column picker in the Item Details view, they see a list of all available columns. However, many columns may be empty for the current action item. Users currently have no way to know which columns will show useful data without trial and error.

## Business Case

**Why now**: Column toggle feature (SFI-011) is complete. This enhancement improves the user experience by reducing guesswork.

**Impact**: Better usability - users can quickly identify relevant columns.

**KPIs**: N/A (local desktop app, no telemetry)

## Stakeholders

- **End Users**: Primary beneficiaries of improved column visibility

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | Analyze item data when column picker opens |
| FR2 | Mark columns with "(empty)" suffix if value is null/blank |
| FR3 | Empty columns remain toggleable (not disabled) |
| FR4 | Non-empty columns display normally without annotation |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Column analysis completes in < 50ms |
| NFR2 | No visible delay when opening dialog |

## Proposed Approach

### Architecture

```
ItemDetailsModal
└── _open_column_selector()
    ├── Get all column names from item
    ├── Compute empty_columns = [col for col in item if item[col] is empty]
    └── Pass empty_columns to ColumnSelectorDialog

ColumnSelectorDialog
├── __init__(available_columns, empty_columns)
└── _create_widgets()
    └── For each column:
        ├── If col in empty_columns: display_name = f"{name} (empty)"
        └── Create checkbox with display_name
```

### Implementation Details

1. **Empty detection function**: Create `get_empty_columns(item: dict) -> set[str]`
   - Returns set of column names where value is None, empty string, empty list, or "None"

2. **Pass empty columns to dialog**: Update `ColumnSelectorDialog.__init__` to accept optional `empty_columns` parameter

3. **Display annotation**: In `_create_widgets`, append "(empty)" to display name for columns in empty set

### Column Empty Detection

```python
def get_empty_columns(item: dict) -> set[str]:
    """Get set of column names that have no data."""
    empty = set()
    for col, value in item.items():
        if value is None:
            empty.add(col)
        elif isinstance(value, str) and not value.strip():
            empty.add(col)
        elif isinstance(value, list) and len(value) == 0:
            empty.add(col)
    return empty
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Gray out empty columns | Visual distinction | May look disabled | Reject |
| Hide empty columns | Cleaner list | User can't see all options | Reject |
| "(empty)" suffix | Clear, simple | Slightly longer text | **Accept** |
| Separate "Empty" section | Organized | Complex UI | Reject |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Performance with many columns | Low | Low | Simple iteration, O(n) |
| False positives (value looks empty but isn't) | Low | Low | Check multiple empty types |

## Dependencies

- SFI-011 Column Toggle UI (complete)
- ColumnSelectorDialog class

## Migration / Rollout / Rollback

**Rollout**: Feature is additive, default behavior unchanged
**Rollback**: Remove empty_columns parameter, no data changes

## Observability Plan

- None needed (local desktop app)

## Test Strategy

1. **Unit Tests**: 
   - `get_empty_columns()` with various empty types
   - `get_empty_columns()` with non-empty values
2. **Integration Tests**: 
   - Dialog displays "(empty)" for empty columns
   - Dialog displays normal text for non-empty columns
