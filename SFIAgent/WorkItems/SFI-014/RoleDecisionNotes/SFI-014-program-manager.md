# SFI-014 Program Manager Notes

## Work Item
- **ID**: SFI-014
- **Title**: Fix Unknown Owner Item and Drill-Down "No Items Found" Bugs
- **Date**: 2024

## Design Decisions

### Root Cause Analysis

1. **Bug 1 (Unknown Owner)**: The `lookup_owner()` function validates org membership by checking if `manager_alias` appears in a person's Managers chain. However, a manager's own chain doesn't include themselves - it ends at their manager. So "Murali Chintalapati" with alias `muralic` has chain ending at `alexhowells`, and checking `muralic in chain` returns False.

2. **Bug 2 (No items found)**: Service statistics are keyed by `S360_ServiceId` (e.g., `ropandey_team`) but `filter_items_by_service()` was looking for `serviceTreeId` (GUID format). Some items (especially team-created services) have empty `serviceTreeId` but valid `S360_ServiceId`.

### Solution Design

Both fixes are surgical - single-function changes with clear logic:

1. **Fix 1**: Add check before Managers chain validation - if result's alias equals manager_alias, they ARE the manager
2. **Fix 2**: Check both ID fields in filter function - covers all service ID formats

### Implementation Notes

- Code changes already implemented and tested
- All 88 unit tests pass
- Verified with muralic cache data

## Handoff to QA

Ready for testing. Key verification points:
1. Manager's own services should appear under their name, not "Unknown Owner"
2. Double-clicking any service row should show matching items
