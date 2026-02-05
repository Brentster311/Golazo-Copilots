# SFI-012: Annotate Empty Columns in Column Picker

**Status**: IMPLEMENTED

## User Story

**Title**: Annotate Empty Columns in Column Picker

**As a**: SFI Reporter user

**I want**: To see which columns have no data for any rows when I open the column picker

**So that**: 
- I can quickly identify columns that won't be useful for the current KPI
- I can make informed decisions about which columns to hide
- I don't waste time enabling columns that will show blank values

## Out of Scope
- Automatically hiding empty columns
- Persisting empty column state across sessions
- Column statistics beyond empty/non-empty

## Assumptions
- **Assumption (explicit)**: Annotation will be visual indicator next to column name (e.g., "(empty)" suffix or grayed out)
- **Assumption (explicit)**: Check is performed on current KPI's data only
- **Assumption (explicit)**: Column is considered "empty" if ALL rows have blank/null values

## Acceptance Criteria

- [x] **AC1**: When column picker opens, columns with no data are visually annotated
- [x] **AC2**: Annotation clearly indicates "no data" (e.g., "(empty)" or disabled/grayed text)
- [x] **AC3**: Empty columns can still be toggled on/off
- [x] **AC4**: Non-empty columns show normal (unannotated) display

## Non-Functional Requirements
- Column analysis should not noticeably delay dialog opening
- Should work with any number of columns

## Telemetry / Metrics Expected
- None (local desktop app)

## Rollout / Rollback Notes
- Feature is additive, no rollback concerns
