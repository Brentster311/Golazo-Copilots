# SFI-006: Program Manager Notes

## Date: 2026-02-04

## Design Decisions

### Modal vs Separate Window
User explicitly requested modal dialog. This simplifies state management - only one detail view at a time.

### Data Source
Using existing `detailed_items` cache - no new API calls needed. This ensures fast (<100ms) modal opening.

### Filter Logic
- **Service**: Match `serviceTreeId` field
- **Program**: Match first element of `S360_ProgramIds` list (same logic as Program Summary)
- **Action Item**: Match `id` field for single item view

### UI Layout
Modal will contain:
- Title bar with context (e.g., "Action Items for Azure Core Platform")
- Scrollable list/table of items (or single item details)
- Close button at bottom

## Next Steps
Transition to developer for implementation.
