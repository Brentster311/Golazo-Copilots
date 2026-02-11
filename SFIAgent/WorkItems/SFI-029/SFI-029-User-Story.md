# SFI-029 — Top-Down Org Tree Grouping with N-Level Manager Hierarchy

**Status**: IMPLEMENTED

## User Story

- **Title**: Use `get_org_tree()` for Owner Resolution and N-Level Manager Grouping
- **As a**: SFIReporter user (manager view)
- **I want**: the org hierarchy and services table grouping to be driven by a single `get_org_tree(manager_alias)` call with N-level manager nesting
- **So that**:
  - 1 Graph API call replaces ~30+ (N alias searches + N chain walks)
  - ICs never appear as group headers — only managers (people with direct reports)
  - Every manager in the chain becomes a group level (not capped at 2)
  - Ambiguous owner names are resolved by matching within the org tree (only one "Rohit Pandey" exists under muralic)
  - Top-most groups are expanded; child groups are collapsed by default
  - Services named `<Person's> Team` correctly identify that person as a manager in the org chart

- **Out of scope**:
  - Changes to `get_org_tree()` API (already updated to `depth=None` default)
  - Changes to cache serialization format
  - Changes to `get_service_owners()` service-level S360 search (fetching which services exist remains)
  - Non-manager-view (IC view) changes

- **Assumptions**:
  - **Assumption (explicit)**: Tkinter desktop GUI, Windows, JSON cache, technical users (same as SFI-028)
  - **Assumption (explicit)**: `S360Client.get_org_tree(alias)` returns full `OrgTree` with `person: OrgPerson` and `direct_reports: list[OrgTree]`
  - **Assumption (explicit)**: Owner names from S360 can be matched to `OrgPerson.display_name` in the tree (case-insensitive) — the tree is the disambiguation filter
  - **Assumption (explicit)**: Every service owner MUST exist in the manager's org tree; "Unknown Owner" indicates a bug to investigate, not an expected category
  - **Assumption (explicit)**: `depth=None` (default) fetches the full tree; no artificial depth cap

## Grouping Rules

1. **Names are the only group header** in the services table
2. **Names shown (if at all) must be managers** — people with `direct_reports` in the org tree. IC names are never shown.
3. **Every manager in the chain** from root (inclusive) to the owner's nearest manager ancestor creates a new group level (N-level nesting). The root IS always `path[0]`.
4. **Only the top-most group is expanded** by default; child groups are collapsed
5. **Owner disambiguation**: match S360 owner names against `display_name` within the org tree — inherently picks the right person
6. **`<Person's> Team` services**: the person named is a manager in the org chart
7. **"Unknown Owner"**: means a bug — every service owner should exist in the tree
8. **Services are leaf rows**: the treeview leaf nodes are service names, never IC/person names

## Acceptance Criteria (bulleted, testable)

- [ ] **AC-1**: `get_org_mapping()` calls `client.get_org_tree(manager_alias)` once (no `depth` cap, no `get_manager_chain()` calls)
- [ ] **AC-2**: The `resolve_alias()` phase in `get_service_owners()` is removed; `get_service_owners()` returns `dict[str, list[str]]` (not tuple)
- [ ] **AC-3**: `owner_aliases` parameter is removed from `get_org_mapping()` and `do_refresh()`
- [ ] **AC-4**: Group headers in the services tree are managers only (have `direct_reports`); IC names never appear in the tree — services are the leaf rows
- [ ] **AC-5**: Group nesting follows the manager chain from root (inclusive) to owner's nearest manager ancestor (N-level, not capped at 2); root is always `path[0]`
- [ ] **AC-6**: Only root-level groups are expanded; child groups are collapsed by default
- [ ] **AC-7**: All unit tests pass (SFI-026 + SFI-028 tests updated for new approach)
- [ ] **AC-8**: Live validation: brentj, muralic, alexhowells org trees produce correct grouping
- [ ] **AC-9**: PyInstaller build succeeds

## Non-functional requirements
- Single Graph API call replaces ~30+ individual calls
- Status callback still reports progress during tree fetch
- Thread safety maintained

## Telemetry / metrics expected
- Logging at INFO for `get_org_tree` call (handled by accia-s360)
- All S360 `resolve_alias` searches eliminated
- Log WARNING for any owner name not found in org tree (bug investigation)
