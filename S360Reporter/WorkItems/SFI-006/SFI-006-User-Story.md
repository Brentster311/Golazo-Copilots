# SFI-006: Double-Click Drill-Down Details

**Status**: IMPLEMENTED

## User Story

- **Title**: Double-Click Drill-Down Details Modal
- **As a**: S360Reporter user
- **I want**: to double-click any row in the Services, Programs, or Action Items tables
- **So that**: I can see detailed action item information filtered by the selected context

## Out of Scope
- Multiple drill-down windows open simultaneously (modal only)
- Editing action items from the detail view
- Deep linking/URL support
- Export from detail view

## Assumptions
- **Assumption (explicit)**: Action item details are already available in the cached `detailed_items` data
- **Assumption (explicit)**: The detail modal will show the same fields for all contexts (Title, Service, Due Date, ETA, Status, Assigned To, etc.)

## Acceptance Criteria

- [ ] Double-clicking a **Service** row opens a modal showing all action items for that service
- [ ] Double-clicking a **Program** row opens a modal showing all action items for that program
- [ ] Double-clicking an **Action Item** row opens a modal showing full details of that single item
- [ ] Modal displays: Title, Service, KPI, Due Date, ETA Date, ETA Status, Assigned To, SLA Type
- [ ] Modal can be closed via Close button or Escape key
- [ ] Modal title reflects the filter context (e.g., "Action Items for [Service Name]")

## Non-functional Requirements
- Modal should open within 100ms (data already cached)
- Modal should be resizable and scrollable for long lists

## Telemetry / Metrics Expected
- None for initial implementation

## Rollout / Rollback Notes
- Feature is additive, no rollback concerns
