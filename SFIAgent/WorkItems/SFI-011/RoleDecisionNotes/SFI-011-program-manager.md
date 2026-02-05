# SFI-011: Program Manager Notes

## Design Decisions

### 1. Modal Dialog for Column Selection
Chose modal dialog over dropdown or right-click menu because:
- Familiar pattern from S360 portal
- Can show all options at once
- Clear action (OK to apply)

### 2. Session-Only Persistence
Column visibility resets when app closes. Rationale:
- Simpler implementation
- Avoids managing user preferences
- Can add persistence in future (SFI-012)

### 3. Required Columns
Some columns cannot be hidden:
- `title` - Identity
- `dueDate` - Primary sort/filter
- `SlaType` - SLA status

This prevents users from accidentally hiding critical information.

### 4. Class Variable for State
Using class variable `_visible_columns` means:
- All DrillDownModal instances share the same visibility
- Setting persists when modal is closed and reopened
- Resets when app restarts

## Sequencing

1. **Phase 1**: Add Columns button to DrillDownModal
2. **Phase 2**: Create ColumnSelectorDialog
3. **Phase 3**: Implement column hiding in Treeview
4. **Phase 4**: Add tests

## Available Columns

From SFI-010 column cache, we know each KPI has 14-21 columns. The drill-down modal will use the union of all columns seen across items.
