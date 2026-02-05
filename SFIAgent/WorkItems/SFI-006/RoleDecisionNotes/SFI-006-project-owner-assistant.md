# SFI-006: Project Owner Assistant Notes

## Date: 2026-02-04

## Request Analysis
User requested double-click drill-down functionality for all three tables in the SFI Reporter.

## Clarifications Obtained
1. **Which rows?** All three: Services, Programs, Action Items
2. **What to show?** Filtered action items based on row context:
   - Service → Items for that service
   - Program → Items for that program  
   - Action Item → Details of that single item
3. **Form type?** Modal dialog (blocks main window)

## Scope Decisions
- Starting with modal vs separate window (user's preference)
- Using existing cached data (no new API calls needed)
- Standard detail fields from existing `detailed_items` data

## Data Available
From `detailed_items` cache, each item has:
- `title`, `id`, `serviceTreeId`
- `SlaType`, `DueDate`, `EtaDate`, `EtaStatus`
- `S360_AssignedTo`, `assignedTo`
- `S360_ProgramIds`, `_kpi_id`

## Next Steps
Transition to developer role for implementation.
