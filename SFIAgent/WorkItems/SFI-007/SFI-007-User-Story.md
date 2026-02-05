# SFI-007: Action Item Full Details View

**Status**: IN PROGRESS

## User Story

- **Title**: Action Item Full Details View
- **As a**: SFI Reporter user
- **I want**: to double-click a row in the drill-down modal to see all available details for that action item
- **So that**: I can see the complete information about a specific action item without navigating elsewhere

## Out of Scope
- Editing action item data
- Deep linking to S360 portal (future enhancement)
- Fetching additional data not already cached
- Copy to clipboard functionality

## Assumptions
- **Assumption (explicit)**: All relevant data is already in the `detailed_items` cache (30 fields available)
- **Assumption (explicit)**: Details view will be a second modal on top of the drill-down modal
- **Assumption (explicit)**: Using existing Tkinter modal pattern from SFI-006

## Acceptance Criteria

- [ ] Double-clicking a row in the drill-down modal opens a details modal
- [ ] Details modal shows all non-empty fields from the cached item
- [ ] Fields are displayed in a readable format (label: value pairs)
- [ ] Modal title includes the action item title
- [ ] Modal can be closed via Close button or Escape key
- [ ] GUIDs are labeled but shown (service ID, KPI ID, etc.)

## Non-functional Requirements
- Details modal opens within 50ms (data already in memory)
- Modal should be scrollable if content exceeds window height
- Fields displayed in logical grouping order

## Telemetry / Metrics Expected
- None for initial implementation

## Rollout / Rollback Notes
- Additive feature, no rollback concerns
