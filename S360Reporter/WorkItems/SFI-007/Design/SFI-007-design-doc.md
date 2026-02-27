# SFI-007: Design Document

## Summary
Add a full details view modal that opens when double-clicking a row in the drill-down modal (from SFI-006). This displays all cached information about a single action item.

## Problem Statement
Users can see a summary of action items in the drill-down modal but cannot see all available details without leaving the app. The cached data contains 30 fields but only 6 are shown in the drill-down view.

## Business Case
- **Why now**: Natural continuation of SFI-006 drill-down feature
- **Impact**: Complete visibility into action item data without external tools
- **KPIs**: User can access all item details within 2 clicks from main view

## Stakeholders
- S360Reporter users (engineering managers, service owners)

## Functional Requirements

1. Double-click on a row in DetailModal opens ItemDetailsModal
2. ItemDetailsModal displays all non-empty fields from the cached item
3. Fields are grouped logically:
   - **Identity**: title, id, _kpi_id
   - **Status**: SlaType, classificationType, ActionItemType, myExceptionStatus
   - **Dates**: dueDate, EtaDate, EtaStatus, OriginalPublishTime
   - **Ownership**: assignedTo, S360_AssignedTo, ActionOwnerAlias, ActionOwnerName
   - **Service/Program**: serviceTreeId, S360_ServiceId, S360_ProgramIds
   - **Other**: Remaining fields
4. Modal title shows action item title
5. Close via button or Escape key

## Non-functional Requirements
- Opens within 50ms (data in memory)
- Scrollable if content exceeds window
- Readable font and spacing

## Proposed Approach

### Implementation
1. Create `ItemDetailsModal` class extending `tk.Toplevel`
2. Add `<Double-1>` binding to the treeview in `DetailModal`
3. Store item data reference in each treeview row
4. Display fields in a scrollable Text or Canvas widget
5. Group and format fields for readability

### Data Flow
```
DetailModal Treeview (double-click)
    ↓
Handler retrieves full item dict from stored reference
    ↓
ItemDetailsModal displays all fields
```

### UI Layout
```
┌─────────────────────────────────────────┐
│ [Title of Action Item]              [X] │
├─────────────────────────────────────────┤
│ ─── Identity ───                        │
│ Title: GDPR Scan Compliance             │
│ ID: 92539de1a873...                     │
│ KPI ID: 09c3aade-339c...                │
│                                         │
│ ─── Status ───                          │
│ SLA Type: OutOfSla                      │
│ Classification: Critical                │
│ ...                                     │
│                                         │
│ ─── Dates ───                           │
│ Due Date: 2026-02-03                    │
│ ETA Date: (none)                        │
│ ...                                     │
│                                         │
│                            [Close]      │
└─────────────────────────────────────────┘
```

## Alternatives Considered

1. **Expand row in-place**: Would require significant treeview modifications
2. **Side panel instead of modal**: More complex layout management
3. **Show all fields always in drill-down**: Too cluttered

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Too many fields overwhelming | Group fields logically, hide empty ones |
| Long GUIDs hard to read | Truncate with ellipsis, full value in tooltip (future) |

## Open Questions
None - requirements clear from user story.

## Dependencies
- SFI-006 DetailModal must be complete (✅ done)
- Cached `detailed_items` structure (✅ available)

## Migration / Rollout / Rollback
- Additive feature
- No data migration needed
- Rollback: revert code

## Observability Plan
- None required for UI feature

## Test Strategy
- Unit test: ItemDetailsModal creation
- Unit test: Field grouping logic
- Unit test: Modal close behavior
- Manual test: Double-click in drill-down opens details
