# SFI-014 Retrospective Notes

## Work Item
- **ID**: SFI-014
- **Title**: Fix Unknown Owner Item and Drill-Down "No Items Found" Bugs
- **Date**: 2024

## What Went Well

1. **Root cause analysis** - Quickly identified both bugs through systematic data tracing with cache file analysis
2. **Surgical fixes** - Both bugs required minimal code changes (5 lines for Bug 1, 1 line for Bug 2)
3. **Test coverage** - All 88 existing tests pass, verifying no regression
4. **Fast workflow** - Bug fix work item moved efficiently through all roles

## What Didn't Go Well

1. **Bug should have been caught earlier** - The manager self-mapping edge case should have been considered during SFI-013 development
2. **Service ID inconsistency** - Using `S360_ServiceId` vs `serviceTreeId` inconsistently across codebase led to Bug 2

## Action Items

1. **Add unit test for manager self-mapping** - Create test case where owner alias equals manager alias
2. **Document service ID fields** - Add code comments explaining when to use `S360_ServiceId` vs `serviceTreeId`
3. **Consider unifying service ID handling** - Future work item to standardize on one ID field

## Lessons Learned

- When filtering by a field, verify the key used matches how the data was aggregated
- Edge cases where the user IS the target (e.g., manager viewing their own services) need explicit handling

## Metrics

- Time from bug identification to fix: ~30 minutes
- Code changes: 6 lines modified across 2 functions
- Test regression: 0 (all 88 tests pass)
