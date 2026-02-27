# SFI-014 Design Document: Fix Unknown Owner and Drill-Down Bugs

## Summary

Fix two bugs in the Manager View introduced in SFI-013:
1. Items from "Murali Chintalapati's Team" incorrectly grouped under "Unknown Owner"
2. Double-clicking on service rows shows "No items found" when items exist

## Problem Statement

After implementing the Service Summary Grouped by Owner feature (SFI-013), two edge case bugs were discovered:

### Bug 1: Manager's Own Items Map to Unknown Owner
When a manager (e.g., Murali Chintalapati) owns a service directly, their items get grouped under "Unknown Owner" instead of their own name. This occurs because:
- The `lookup_owner()` function checks if `manager_alias` is in the person's Managers chain
- A manager's Managers chain doesn't include themselves (ends at their manager)
- Example: Murali's chain is `['satyan', 'scottgu', 'girishb', 'timmall', 'alexhowells']` - no `muralic`

### Bug 2: Service Drill-Down Returns Empty Results
When double-clicking on a service row in Manager View, the detail modal shows "No items found" even when items exist. This occurs because:
- `filter_items_by_service()` uses `item.get('serviceTreeId')` to filter
- Service stats are keyed by `S360_ServiceId` (e.g., `ropandey_team`), not `serviceTreeId` (GUIDs)
- Some items have empty `serviceTreeId` but valid `S360_ServiceId`

## Business Case

- **Impact**: Managers cannot see accurate counts for their own services; cannot drill into service details
- **Urgency**: Blocks effective use of the Manager View feature
- **KPI**: 100% of items should be correctly attributed; 100% of drill-downs should return expected items

## Proposed Approach

### Fix 1: Handle Manager's Own Items
In `lookup_owner()`, add an early check: if the search result's `Id` (alias) matches `manager_alias`, the owner IS the manager and should map to themselves.

```python
# After confirming result matches owner_name
result_alias = r.get('Id', '')
if result_alias.lower() == manager_alias.lower():
    # The owner is the manager - map to themselves
    return owner_name, owner_name
```

### Fix 2: Support Both Service ID Formats
Modify `filter_items_by_service()` to check both `S360_ServiceId` and `serviceTreeId`:

```python
def filter_items_by_service(items: list, service_id: str) -> list:
    """Filter items by service ID (S360_ServiceId or serviceTreeId)."""
    return [item for item in items if item.get('S360_ServiceId') == service_id or item.get('serviceTreeId') == service_id]
```

## Alternatives Considered

1. **Change service_stats keys to serviceTreeId**: Would break IC view which expects service GUIDs
2. **Store both IDs in service_stats**: More complex, requires tracking mapping
3. **Populate owner's chain with themselves**: Would require modifying data from S360 API

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Breaking existing service filtering | Both ID types checked, falls through if neither matches |
| Performance overhead | Negligible - single additional dict lookup per item |

## Test Strategy

- Unit tests for `filter_items_by_service` with both ID types
- Manual verification with muralic cache data
- Verify no regression in existing owner attribution

## Rollback Plan

Revert changes to `lookup_owner()` and `filter_items_by_service()` - both are single-function changes.

## Files Changed

- `GUI/src/sfi_reporter/tk_app.py`:
  - `lookup_owner()` (lines ~270-275): Add manager self-check
  - `filter_items_by_service()` (lines ~716-718): Support both ID formats
