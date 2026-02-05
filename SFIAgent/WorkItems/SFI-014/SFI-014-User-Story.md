# SFI-014: Manager View - Owner Drill-Down Bugs

## Status: ✅ IMPLEMENTED

## User Story

**As a** manager using the SFI Reporter  
**I want** the owner grouping and drill-down to work correctly  
**So that** I can see which action items belong to each of my directs

## Acceptance Criteria

### Bug 1: Item incorrectly assigned to Unknown Owner
- [x] The 1 item currently showing under "Unknown Owner" actually belongs to Murali Chintalapati
- [x] Items owned by the manager themselves should show under their own name, not Unknown Owner
- [x] Verify the org_mapping logic handles the manager's own name correctly

### Bug 2: Drill-down shows "No items found" for some owners
- [x] Double-clicking "Rohit Pandey's Team" shows "No items found" but count shows 2
- [x] Double-clicking "Unknown Owner" likely has same issue
- [x] The drill-down modal filters items by the selected owner name
- [x] The filter logic must match how items were aggregated

## Technical Notes

### Bug 1 Analysis
- The org_mapping is looking up owner names and checking if `muralic` is in their management chain
- For Murali Chintalapati himself, his Managers chain ends at `alexhowells` (his manager), not himself
- Need to handle the case where the owner IS the manager - should map to themselves

### Bug 2 Analysis  
- The drill-down modal filters `detailed_items` by owner name
- But the aggregation maps owners to their "direct-report-level" ancestor
- So "Rohit Pandey's Team" (service name) has items, but those items' owners are mapped to "Rohit Pandey" (person)
- The drill-down is likely looking for items where the direct matches, but needs to also check the service name or use the same mapping logic

### Root Cause
The drill-down filter logic doesn't match the aggregation logic:
- Aggregation: item → service → owners → org_mapping → direct
- Drill-down: needs to reverse this to find items for a given direct

## Related Files
- `SFIReporter/src/sfi_reporter/tk_app.py`: `get_org_mapping()`, `aggregate_by_owner()`, drill-down modal

## Priority
Medium - Feature works but with data display bugs

## Created
2026-02-04
