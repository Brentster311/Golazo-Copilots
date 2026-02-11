# SFI-026 Design Document — Multi-Level Owner Grouping in Services Table

## Summary

Extend the SFI Reporter desktop app's Services table from 1-level owner grouping to 2-level hierarchical grouping. Today, when a skip-level manager (e.g., alexhowells) uses SFI Reporter, all services appear under "Unknown Owner" because the grouping algorithm only resolves owners to the viewer's *direct* reports. This change adds a second tier so the treeview displays: `viewer → direct reports → their reports → services`.

## Problem Statement

The current `get_org_mapping()` function (tk_app.py, lines 283-400) maps every service owner to their **direct-report ancestor** under the viewing manager. This produces correct grouping for 1-level managers (e.g., muralic sees their team's services grouped by direct reports). However, for 2-level managers (e.g., alexhowells, whose directs *also* have directs), every owner maps to `None` because the algorithm cannot find `alexhowells` in the management chain at the expected position — it only looks one level up.

**Result**: alexhowells sees all services under a single "Unknown Owner" row, losing all organizational context.

**Evidence**: User-provided screenshots show:
- **brentj** (IC): Flat list — correct
- **muralic** (1-level manager): Grouped by direct reports — correct
- **alexhowells** (2-level manager): All under "Unknown Owner" — broken

## Business Case

### Why Now
- alexhowells (and managers at similar levels) cannot use SFI Reporter effectively to triage SFI action items across their org
- This was the #1 requested enhancement after 1-level grouping shipped in SFI-013
- The longer it's deferred, the more manual triage skip-level managers must do

### Impact
- Estimated 5-10 skip-level managers in the target org will benefit immediately
- Reduces manual cross-referencing of service ownership from ~30 min/week to ~5 min/week per manager

### KPIs
- Successful rendering of 2-level hierarchy for skip-level managers (functional KPI)
- No increase in refresh time > 15% (performance KPI)
- Zero regressions in 1-level grouping or IC flat view (quality KPI)

## Stakeholders

| Role | Person | Interest |
|------|--------|----------|
| Developer / PO | brentj | Implements and owns SFI Reporter |
| 1-level manager | muralic | Must not regress |
| 2-level manager | alexhowells | Primary beneficiary |

## Functional Requirements

1. **2-Level Treeview**: Services table shows a 3-tier tree: Level-1 owner → Level-2 owner → service rows
2. **Aggregated Counts**: Both Level-1 and Level-2 parent rows display rolled-up counts (total items, SLA violations, invalid ETAs)
3. **Drill-Down**: Double-clicking a Level-1 or Level-2 owner row filters the Action Items table to that subtree's services
4. **Backward Compatibility**: 1-level managers and ICs see no change in behavior

## Non-Functional Requirements

1. **Performance**: Must not add sequential API calls. All management-chain lookups remain parallel (8+ workers). Acceptable refresh time increase: ≤15%.
2. **Responsiveness**: Hierarchy computation must not block the Tkinter event loop.
3. **Memory**: Negligible increase — one additional dict mapping level-2 ancestors.

## Proposed Approach (High Level)

### Phase 1: Extend `get_org_mapping()` to Return Multi-Level Mapping

**Current**: Returns `{owner_alias → direct_report_name}` (flat mapping to 1 ancestor)

**Proposed**: Returns `{owner_alias → (level1_name, level2_name)}` where:
- `level1_name` = viewer's direct report ancestor
- `level2_name` = that direct's sub-report ancestor (or `None` if the owner IS the level-1 direct)

**Algorithm change**: When traversing the management chain for each owner:
1. Find `manager_alias` (the viewer) in the chain
2. The person immediately after `manager_alias` = Level-1 ancestor
3. The person after the Level-1 ancestor = Level-2 ancestor (if the owner is further down)
4. If the owner IS the Level-1 direct, `level2_name = None`

This uses the **same API calls** already being made — just extracts one more level from the returned chain.

### Phase 2: Extend `aggregate_by_owner()` for Two-Tier Rollup

**Current**: Produces `{owner_name → stats}` keyed by the single mapped ancestor.

**Proposed**: Produces two dicts:
- `level1_stats: {level1_name → aggregated_stats}` (roll up everything under a direct)
- `level2_stats: {(level1_name, level2_name) → aggregated_stats}` (roll up per sub-report)

### Phase 3: Extend `_update_tables()` for 3-Tier Treeview

**Current** (manager branch, lines 2803-2857):
1. Build `owner_services` mapping
2. Insert parent rows (👤 owner)
3. Insert child service rows

**Proposed**:
1. Detect hierarchy depth (1-level vs 2-level) based on whether any `level2_name` values are non-None
2. If 1-level: use existing logic (no change)
3. If 2-level:
   - Insert Level-1 parent rows (👤 direct report) with aggregated counts
   - Under each Level-1, insert Level-2 sub-rows (👤 sub-report) with aggregated counts
   - Under each Level-2, insert service leaf rows

### Phase 4: Extend `_on_service_double_click()` for Multi-Level Drill-Down

**Current**: Distinguishes owner rows from service rows using `_owner_id_map`.

**Proposed**: Extend `_owner_id_map` to track both Level-1 and Level-2 owner rows. On double-click:
- Level-1 owner → filter Action Items to all services under that direct's entire subtree
- Level-2 owner → filter Action Items to services under that specific sub-report
- Service row → existing behavior (filter to that one service)

## Alternatives Considered

### 1. Recursive N-Level Grouping
**Description**: Support arbitrary nesting depth via recursive treeview insertion.
**Rejected because**: No current user is more than 2 levels deep. The added complexity (recursive aggregation, recursive drill-down, recursive treeview management) is not justified. Can be revisited if a 3+ level manager requests it.

### 2. Flat Table with "Manager" Column
**Description**: Add a "Direct Owner" column to the flat table instead of tree grouping.
**Rejected because**: Does not provide the collapsible, at-a-glance view that managers want. The whole point of the treeview is visual hierarchy.

### 3. Separate Tab per Direct Report
**Description**: Show a separate services tab for each of alexhowells' directs.
**Rejected because**: Fragments the view. Managers want to compare across their org in a single table.

## Risks, Mitigations, Open Questions

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Regression in 1-level grouping | Medium | High | Explicit AC-2; preserve existing code path when `level2_name` is all-None |
| "Unknown Owner" edge cases at 2 levels | Medium | Medium | Test with owners who report directly to the viewer (should appear as Level-1 with no Level-2 children) |
| Performance: more chain traversal computation | Low | Low | Same API data, just parsing one more element from the chain array |
| Treeview expand/collapse UX confusion | Low | Low | Use consistent 👤 prefix for all owner rows; indent levels differentiate |

### Open Questions
- None. All requirements are clear from user context and prior work items.

## Dependencies

| Dependency | Type | Status |
|-----------|------|--------|
| S360 management-chain API (`/api/v2/user/{alias}`) | External API | Available, already in use |
| SFI-013 (1-level grouping) | Prior work | Shipped |
| SFI-014 (grouping bug fixes) | Prior work | Shipped |
| accia-s360 client library | Internal | Available |

## Capability Impact

Per `gcp_capabilities(action="impact")`:
- **Directly affected**: `reporter-tk-app`, `reporter-data`
- **Transitively affected**: `reporter-build`, `reporter-tests`, `reporter-web-app`, `reporter-eta-logic`, `reporter-query-builder`

Only `reporter-tk-app` requires code changes. `reporter-data` data structures are consumed but not modified. Transitive impacts are build/test only.

## Migration / Rollout / Rollback Plan

- **Migration**: None. No data schema changes. No config file changes.
- **Rollout**: Ship in next PyInstaller build. The algorithm auto-detects hierarchy depth from the management chain data. No feature flag needed.
- **Rollback**: Revert to previous PyInstaller build. No data cleanup required.

## Observability Plan

- Existing `log.info` in `do_refresh()` already logs refresh duration. If 2-level grouping causes >15% slowdown, it will be visible in existing logs.
- No additional telemetry or monitoring required for a desktop app.

## Test Strategy Summary

| Test Type | Scope | Approach |
|-----------|-------|----------|
| Unit | `get_org_mapping()` with 1-level and 2-level chains | Mock S360 API responses with known chain structures; assert correct (level1, level2) tuples |
| Unit | `aggregate_by_owner()` two-tier rollup | Feed known service/owner data; assert correct stats at both levels |
| Integration | `_update_tables()` treeview rendering | Mock data layer; verify treeview has correct nesting structure for 1-level, 2-level, and IC views |
| Integration | `_on_service_double_click()` drill-down | Simulate double-click on Level-1 and Level-2 rows; verify Action Items filter |
| Regression | 1-level manager view | Run existing test scenarios from SFI-013/SFI-014; assert identical output |
| Regression | IC flat view | Verify no grouping rows appear |
| Manual | End-to-end with real S360 data | brentj tests as IC, muralic tests as 1-level manager, alexhowells tests as 2-level manager |
