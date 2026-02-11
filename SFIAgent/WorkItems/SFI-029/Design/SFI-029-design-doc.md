# SFI-029 Design Document

## Summary
Replace the bottom-up, per-owner `get_manager_chain()` + S360 alias resolution approach with a single top-down `get_org_tree(manager_alias)` call. Refactor the services table to use N-level manager grouping driven by the org tree structure.

## Problem Statement
SFI-028 improved org resolution but still:
- Makes ~30+ API calls (N alias searches + N chain walks)
- Allows ICs to appear as group headers (Bhavya Gopal bug)
- Caps grouping at 2 levels (`OrgAncestry.level1`, `level2`)
- Relies on unreliable S360 people search for alias resolution
- Cannot disambiguate common names (multiple "Rohit Pandey" in MS)

## Business Case
- **Performance**: 1 API call tree vs ~30+ sequential calls
- **Correctness**: Org tree inherently knows managers vs ICs
- **Disambiguation**: Only one person per name exists in a manager's tree
- **UX**: N-level grouping with smart expand/collapse is more navigable

## Stakeholders
- Brent Jensen (developer, user)
- Murali Chintalapati (primary test case manager)

## Proposed Approach

### Phase 1: Data Layer
1. **`get_org_mapping()`** — rewrite to:
   - Call `client.get_org_tree(manager_alias)` once
   - Flatten tree into `{display_name.lower(): list[OrgPerson]}` (path from root)
   - For each owner name, find in tree → return ancestry path (all managers)
   - Replace `OrgAncestry(level1, level2)` with variable-length path

2. **`get_service_owners()`** — simplify:
   - Remove `resolve_alias()` inner function (Phase 2 S360 people search)
   - Return `dict[str, list[str]]` instead of `tuple[dict, dict]`
   - Remove `owner_aliases` parameter from callers

3. **`do_refresh()`** — update:
   - Simple unpack: `service_owners = get_service_owners(...)`
   - Pass org tree data to `get_org_mapping()` (or let it fetch internally)

### Phase 2: UI Layer
4. **Tree population** — refactor grouping:
   - N-level nesting: walk ancestry path, create group nodes for each manager
   - Only people with `direct_reports` become group headers; IC names never appear
   - Services are the leaf rows in the treeview (not IC/person names)
   - Root (viewer) IS always `path[0]` — the first group level; path is never empty for found owners
   - Root groups `open=True`, all child groups `open=False`

5. **Aggregation functions** — update `aggregate_by_owner()` and `aggregate_by_level2()` for N-level paths

### Phase 3: Tests
6. Update SFI-026 and SFI-028 test mocks for new `get_org_tree` approach
7. Add tests for N-level grouping, IC filtering, expand/collapse defaults

## Alternatives Considered
- **Keep 2-level cap, just change data source**: Simpler but doesn't fix the nesting limitation
- **Parallel `get_manager_chain()` with better batching**: Still N calls, doesn't fix IC bug

## Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Large orgs = slow tree fetch | `depth=None` only fetches until leaf ICs; library handles internally |
| Name collision in tree | Case-insensitive `display_name` match; tree constrains to one match |
| Existing tests break | Update mocks to provide `OrgTree` instead of `get_manager_chain` responses |

## Dependencies
- accia-s360 `get_org_tree()` with `depth=None` (already done)
- `OrgTree` / `OrgPerson` models (already exist)

## Test Strategy
- Unit tests: mock `get_org_tree` return, verify grouping logic
- Live validation: brentj, muralic, alexhowells trees
- Regression: all existing SFI-026/028 tests adapted

## Rollback
- Revert to SFI-028 branch (committed, pushed)
