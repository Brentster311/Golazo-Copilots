# SFI-011: Project Owner Assistant Notes

## Request Analysis

User requested ability to toggle columns on/off, similar to the S360 portal's AllColumns filter.

## Context from Prior Work Items

- **SFI-010**: Implemented column metadata cache - each KPI's available columns are cached
- **SFI-008**: Full S360 data parity - item details view shows all fields
- **SFI-007**: Added ItemDetailsModal for showing all action item fields

## Scope Decision

Focused on **drill-down modal columns** only, not item details view fields. The drill-down modal has a table with columns that can be shown/hidden. Item details view is a different feature (grouped fields, not tabular).

## Questions Already Answered (from prior context)

- **Interface type**: Tkinter desktop app (GUI)
- **Target platform**: Windows
- **Data persistence**: Session-only (no persistence for column prefs)
- **User type**: Technical (developers viewing SFI action items)

## Design Considerations

1. **Column selector UI**: Modal dialog with checkboxes, opened from gear button
2. **Essential columns**: Some columns must always be visible (Title, Due Date, SLA)
3. **Session persistence**: Column visibility stored in app memory, not file

## Future Work (explicitly out of scope)

- SFI-012: Persist column preferences across sessions
- SFI-013: Column reordering
