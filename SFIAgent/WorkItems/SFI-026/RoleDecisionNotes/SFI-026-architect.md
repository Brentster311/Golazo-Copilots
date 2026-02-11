# SFI-026 — Architect Decision Notes

## Work Item
**ID**: SFI-026
**Title**: Multi-Level Owner Grouping in Services Table

## Architectural Decisions

### 1. NamedTuple for Org Mapping Values
**Decision**: Introduce `OrgAncestry(level1, level2)` NamedTuple instead of raw tuple.
**Rationale**: Self-documenting, zero runtime cost, backward-compatible with tuple unpacking. Prevents positional index bugs.

### 2. No New Modules or Classes
**Decision**: Keep all changes within `tk_app.py` (functions + method updates). Do not extract a new `org_hierarchy.py` module.
**Rationale**: The grouping logic is tightly coupled to the treeview rendering. Extracting it would create function-forwarding boilerplate without reducing complexity. If the feature grows beyond 2 levels in the future, extraction would make sense then.

### 3. Preserve Existing Fallback Branches
**Decision**: The three-branch display logic (manager grouped / IC flat / fallback flat) remains structurally intact. The 2-level change only modifies the first branch's inner rendering.
**Rationale**: Minimizes blast radius. Branches 2 and 3 are regression-safe if untouched.

### 4. Level-2 Treeview Expand State
**Decision**: Both Level-1 and Level-2 rows default to `open=True`.
**Rationale**: SFI Reporter is a "see everything at a glance" tool for managers. Collapsed rows would hide information that managers want visible immediately.

## Capability Contract Compatibility
Verified all 7 affected capabilities. Only `reporter-tk-app` requires code changes. All transitive dependents (build, tests, web-app, eta-logic, query-builder) have no contract-breaking impact.

## Security Review
- No new PII exposure (management chain data already displayed)
- No new API scopes or auth changes
- No new external dependencies
- No persistence changes (in-memory only)

## Risk Assessment
- **Index out of bounds on short chains**: Mitigated by defaulting level2 to None when chain has fewer entries than expected
- **Threading**: No change to thread-safety profile — lock-protected dict writes
- **Performance**: Same API calls, ~0% overhead for chain parsing

## TechBestPractices.md Review
Reviewed `.github/roles/TechBestPractices.md`. No applicable items for this change:
- No Azure Identity/credential changes
- No Kusto queries
- No new external library usage
