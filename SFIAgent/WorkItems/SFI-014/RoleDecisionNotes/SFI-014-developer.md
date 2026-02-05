# SFI-014 Developer Notes

## Work Item
- **ID**: SFI-014
- **Title**: Fix Unknown Owner Item and Drill-Down "No Items Found" Bugs
- **Date**: 2024

## Implementation Summary

### Bug 1 Fix: Manager Self-Mapping

**File**: `SFIReporter/src/sfi_reporter/tk_app.py`
**Function**: `lookup_owner()` (lines ~270-285)

**Change**: Added early check after matching owner name - if the result's alias (`r.get('Id')`) equals `manager_alias`, return immediately with owner mapping to themselves.

```python
# Check if this owner IS the manager (their chain won't include themselves)
result_alias = r.get('Id', '')
if result_alias.lower() == manager_alias.lower():
    # The owner is the manager - map to themselves
    return owner_name, owner_name
```

**Rationale**: A manager's Managers chain doesn't include themselves - it ends at their own manager. So checking `manager_alias in chain` fails for the manager's own services.

### Bug 2 Fix: Dual Service ID Check

**File**: `SFIReporter/src/sfi_reporter/tk_app.py`
**Function**: `filter_items_by_service()` (lines ~716-718)

**Change**: Check both `S360_ServiceId` and `serviceTreeId` fields.

```python
def filter_items_by_service(items: list, service_id: str) -> list:
    """Filter items by service ID (S360_ServiceId or serviceTreeId)."""
    return [item for item in items if item.get('S360_ServiceId') == service_id or item.get('serviceTreeId') == service_id]
```

**Rationale**: Service stats are keyed by `S360_ServiceId` (e.g., `ropandey_team`) but some items have empty `serviceTreeId`. Checking both fields covers all cases.

## Test Results

All 88 unit tests pass:
```
============================= 88 passed in 1.07s ==============================
```

## Verification

Manually verified:
1. `filter_items_by_service()` works with both `S360_ServiceId` and `serviceTreeId`
2. Logic for manager self-check is correct based on muralic cache data analysis
