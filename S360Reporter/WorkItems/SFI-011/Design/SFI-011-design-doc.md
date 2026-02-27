# SFI-011: Design Document - Column Toggle UI

## Summary

Add a column selector UI to the drill-down modal, allowing users to show/hide columns in the action items table.

## Problem Statement

The drill-down modal currently shows a fixed set of columns. Users may want to:
- Hide columns they don't need (reduce clutter)
- Focus on specific fields relevant to their workflow
- See more data in less horizontal space

## Business Case

**Why now**: SFI-010 established column metadata caching, providing the foundation for knowing which columns are available per-KPI. This feature completes the column management story.

**Impact**: Improved user experience with customizable views.

## Stakeholders

- **End Users**: Primary beneficiaries of column customization

## Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | "Columns" button in drill-down modal header |
| FR2 | Column selector dialog with checkboxes for each column |
| FR3 | Toggling checkbox immediately updates table visibility |
| FR4 | "Select All" and "Clear All" buttons |
| FR5 | Essential columns cannot be unchecked (Title, Due Date, SLA Type) |
| FR6 | Column visibility persists within session |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | Column selector opens in < 100ms |
| NFR2 | Column visibility changes don't require data refresh |
| NFR3 | UI remains responsive with many columns |

## Proposed Approach

### UI Design

```
┌──────────────────────────────────────────────────────────┐
│ Action Items for: [Service Name]     [Columns] [Close]   │
├──────────────────────────────────────────────────────────┤
│ Title | Due Date | SLA | Action Owner | ETA Status | ... │
│ ────────────────────────────────────────────────────────│
│ Item 1 ...                                               │
│ Item 2 ...                                               │
└──────────────────────────────────────────────────────────┘

Clicking [Columns] opens:
┌─────────────────────────────────┐
│ Select Columns                  │
├─────────────────────────────────┤
│ [Select All] [Clear All]        │
│                                 │
│ ☑ Title (required)              │
│ ☑ Due Date (required)           │
│ ☑ SLA Type (required)           │
│ ☑ Action Owner                  │
│ ☐ ETA Date                      │
│ ☐ ETA Status                    │
│ ☑ Service Name                  │
│ ...                             │
│                                 │
│              [OK]               │
└─────────────────────────────────┘
```

### Architecture

```
DrillDownModal
├── columns_button (opens selector)
├── visible_columns: list[str]  # Session state
├── ColumnSelectorDialog (Toplevel)
│   ├── checkboxes: dict[str, BooleanVar]
│   ├── select_all_button
│   └── clear_all_button
└── update_columns() -> rebuilds Treeview columns
```

### Column Configuration

```python
# Essential columns that cannot be hidden
REQUIRED_COLUMNS = ['title', 'dueDate', 'SlaType']

# Default visible columns
DEFAULT_VISIBLE_COLUMNS = [
    'title', 'dueDate', 'SlaType', 'ActionOwnerName', 
    'EtaDate', 'EtaStatus', 'S360_ServiceTreeServiceName'
]

# Human-readable display names
COLUMN_DISPLAY_NAMES = {
    'title': 'Title',
    'dueDate': 'Due Date',
    'SlaType': 'SLA Type',
    'ActionOwnerName': 'Action Owner',
    ...
}
```

### Session Persistence

Store visible columns in class variable:
```python
class DrillDownModal:
    # Class variable - shared across all instances in session
    _visible_columns: list[str] = None  # None = use defaults
```

## Alternatives Considered

| Alternative | Pros | Cons | Decision |
|-------------|------|------|----------|
| Dropdown menu | Compact | Hard to see all options | Reject |
| Right-click header | Discoverable | Non-standard in Tkinter | Reject |
| Modal dialog | Clear, familiar | Extra click | **Accept** |
| Sidebar panel | Always visible | Takes screen space | Reject |

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Too many columns to display | Medium | Low | Scrollable checkbox list |
| User hides all columns | Low | Low | Required columns can't be hidden |
| Confusion about persistence | Medium | Low | Tooltip: "Changes apply to this session" |

## Dependencies

- SFI-010 column metadata cache (for knowing available columns)
- Existing DrillDownModal class

## Migration / Rollout / Rollback

**Rollout**: Feature is additive, default behavior unchanged
**Rollback**: Remove button, no data changes

## Observability Plan

- None needed (local desktop app)

## Test Strategy

1. **Unit Tests**: Column visibility logic, required column protection
2. **Integration Tests**: Modal opens, checkboxes work
3. **Manual Tests**: Visual verification of column hiding/showing
