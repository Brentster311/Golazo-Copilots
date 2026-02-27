# SFI-006: Design Document

## Summary
Add double-click drill-down functionality to all three tables in S360Reporter (Services, Programs, Action Items) that opens a modal dialog showing filtered action item details.

## Problem Statement
Users can see summary counts in the tables but cannot easily drill into the details of which specific action items make up those counts. They must mentally correlate between the summary tables and the action items list.

## Business Case
- **Why now**: Core usability feature requested by primary user
- **Impact**: Reduces time to investigate specific action items
- **KPIs**: User can identify specific items within 2 clicks

## Stakeholders
- S360Reporter users (brentj and team)

## Functional Requirements
1. Double-click on Service row → Modal with action items filtered by that service
2. Double-click on Program row → Modal with action items filtered by that program
3. Double-click on Action Item row → Modal with full details of that single item
4. Modal displays: Title, Service, KPI, Due Date, ETA Date, ETA Status, Assigned To, SLA Type
5. Modal can be closed via Close button or Escape key
6. Modal title shows filter context

## Non-functional Requirements
- Modal opens within 100ms (data already cached)
- Modal is resizable and scrollable
- Modal is modal (blocks parent window)

## Proposed Approach

### Implementation
1. Create `DetailModal` class extending `tk.Toplevel`
2. Add `<Double-1>` event binding to all three treeviews
3. Each handler filters `detailed_items` by context:
   - Service: filter by `serviceTreeId`
   - Program: filter by first item in `S360_ProgramIds`
   - Action Item: show single item by `id`
4. Modal displays filtered items in a Treeview or Text widget
5. Close button and Escape key binding to dismiss

### Data Flow
```
User double-clicks row
    ↓
Handler extracts filter key (service ID, program ID, or item ID)
    ↓
Filter detailed_items from cache
    ↓
Open modal with filtered data
```

## Alternatives Considered
1. **Separate window (non-modal)**: Allows multiple views but more complex; deferred to future
2. **Inline expansion**: Would require significant UI rework; rejected

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Performance with many items | Data already cached; limit display to 100 rows initially |
| Program ID mismatch | Use same lookup logic as Program Summary |

## Open Questions
None - requirements are clear.

## Dependencies
- Existing `detailed_items` cache structure
- Existing `service_stats` and `program_stats` for name lookups

## Migration / Rollout / Rollback
- Additive feature, no migration needed
- Rollback: revert code changes

## Observability Plan
- None required for UI feature

## Test Strategy
- Unit test: Modal creation and closing
- Unit test: Filter logic for each context type
- Manual test: Double-click behavior in running app
