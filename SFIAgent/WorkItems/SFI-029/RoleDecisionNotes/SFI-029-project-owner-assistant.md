# SFI-029 — Project Owner Assistant Decision Notes

## Context
SFI-028 replaced S360 search chain-walking with MS Graph `get_manager_chain()` per-owner. While correct, it still makes ~30+ API calls (N alias searches + N chain walks) and has bugs:
- ICs (e.g., Bhavya Gopal) appear as L1 group headers
- Alias resolution via S360 search is unreliable — many fall to "Unknown Owner"
- Ambiguous names (e.g., "Rohit Pandey") can't be disambiguated

## Key Decisions

### 1. Single `get_org_tree()` replaces all chain-walking
- `get_org_tree(manager_alias)` with `depth=None` fetches the full tree
- Owner names matched against `display_name` within the tree — inherent disambiguation
- No alias resolution phase needed

### 2. N-level manager grouping (not capped at 2)
- Previous `OrgAncestry(level1, level2)` NamedTuple capped at 2 levels
- New approach: every manager in the chain from root to owner is a group level
- Only people with `direct_reports` in the tree are managers → group headers

### 3. Collapse behavior changed
- Previous: all levels expanded (`open=True`)
- New: only root-level groups expanded; child groups collapsed by default

### 4. "Unknown Owner" means bug, not expected category
- Every service owner MUST exist in the manager's org tree
- "Unknown Owner" retained for debugging but is a signal to investigate

### 5. `<Person's> Team` naming convention
- Services named like "Rohit Pandey's Team" indicate that person is a manager in the org chart
- This is a data convention from S360, not something the app creates

## Scope Refinements from Discussion
- `depth=None` default already applied to `get_org_tree()` in accia-s360 (done pre-story)
- `get_service_owners()` simplifies to return just `dict[str, list[str]]`
- `OrgAncestry` NamedTuple will be replaced with a tree-path-based structure
- Live validation against brentj, muralic, alexhowells orgs required

## API Exploration Results
- `get_org_tree('muralic')`: 79 people, 8 managers (7 L1 directs + muralic), ~80 Graph sub-queries
- `get_org_tree('alexhowells', depth=3)`: Full 3-level tree, 39 queries
- `get_user_search_groups('muralic')`: 1,119 GUIDs, zero overlap with org tree — completely unrelated
- `query_people_hierarchy()`: S360 team/service hierarchy, not people org
