# SFI-011: Column Toggle UI for Item Details View

**Status**: IMPLEMENTED

## User Story

**Title**: Column Toggle UI for Item Details View

**As a**: S360Reporter user

**I want**: To select which columns/fields are displayed in the drill-down modal and item details view

**So that**: 
- I can focus on the fields that matter to me
- I can hide fields that are not relevant to my workflow
- The display is less cluttered with only essential information

## Out of Scope
- Column reordering (drag to change order)
- Saving column preferences per-user
- Column width customization
- Filtering/searching within column values

## Assumptions
- **Assumption (explicit)**: UI will be a gear/settings button in the drill-down modal that opens a column selector
- **Assumption (explicit)**: Column visibility applies to current session only (not persisted)
- **Assumption (explicit)**: All columns visible by default
- **Assumption (explicit)**: Uses cached column metadata from SFI-010 for available columns

## Acceptance Criteria

- [x] **AC1**: Drill-down modal has a "Columns" button that opens column selector
- [x] **AC2**: Column selector shows checkboxes for each available column
- [x] **AC3**: Unchecking a column hides it from the drill-down table
- [x] **AC4**: Column visibility persists within the session (reopening modal keeps settings)
- [x] **AC5**: "Select All" / "Clear All" buttons for quick selection
- [x] **AC6**: Essential columns (Title, Due Date, SLA) cannot be hidden

## Non-Functional Requirements
- Column selector should open quickly (< 100ms)
- Should not require data refresh to apply changes

## Telemetry / Metrics Expected
- None (local desktop app)

## Rollout / Rollback Notes
- Feature is additive, no rollback concerns
- Default behavior unchanged (all columns visible)
