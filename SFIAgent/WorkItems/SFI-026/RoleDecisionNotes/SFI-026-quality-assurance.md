# SFI-026 — Quality Assurance Decision Notes

## Work Item
**ID**: SFI-026
**Title**: Multi-Level Owner Grouping in Services Table

## Design Review Decisions

### 5 Issues Identified, 2 High/Medium Priority

1. **Drill-down needs org_mapping** (High) — The current drill-down code matches by raw owner name in `service_owners`. For Level-1 owners in 2-level mode, we must traverse `org_mapping` to find ALL owners in that subtree. This is a critical gap in the design that would cause incorrect drill-down behavior.

2. **Return type change** (Medium) — Changing `get_org_mapping()` from `{str: str}` to `{str: tuple}` is a breaking API change. Recommended Option A (explicit type) so callers fail at dev time, not silently.

3. **Manager's own services** (Medium) — Not addressed in design. Added handling rule: self-map to `(self, None)` at Level-1.

4. **Collapse redundant Level-2** (Low) — When a Level-1 direct has no distinct sub-reports, skip the Level-2 tier for that subtree.

5. **Sort order** (Low) — Document: count descending at all levels.

### Capability Coverage Check
Ran `gcp_capabilities(action="impact")` on affected files. 7 capabilities affected. Only `reporter-tk-app` requires code changes. Test cases cover the `reporter-tk-app` contract (treeview rendering, drill-down, aggregation).

## Test Strategy Decisions

### 26 Test Cases Across 6 Categories
- **get_org_mapping**: 8 tests covering 1-level, 2-level, 3+-level, Unknown Owner, empty, parallel
- **aggregate_by_owner**: 4 tests covering rollup, SLA/ETA, Unknown bucket, backward compat
- **_update_tables**: 5 tests covering 3-tier, 2-tier regression, IC flat, counts, sort order
- **_on_service_double_click**: 4 tests covering L1 drill, L2 drill, service drill, Unknown drill
- **SFI-014 regression**: 2 tests for manager-own and service-filter fixes
- **Edge cases**: 3 tests for mixed depth, empty directs, self-owning directs

### Coverage Matrix
All 7 acceptance criteria have ≥2 test cases. AC-1 and AC-7 have the most coverage (5 and 4 tests respectively) because they are the primary risk areas.

### Testing Approach
- All tests use mocked S360 API (no live calls)
- Treeview tests mock the Tk widget to inspect tree structure without GUI
- Drill-down tests verify the filter logic produces correct item sets
- Regression tests replicate SFI-013/SFI-014 test scenarios with the new code

## No Scope Changes
No new user stories needed. All issues are implementable within the existing user story scope.
