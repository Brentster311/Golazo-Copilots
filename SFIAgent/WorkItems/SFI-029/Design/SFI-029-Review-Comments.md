# SFI-029 — Review Comments

## Design Review

### Clarity: PASS
- Approach is clear: single `get_org_tree()` → flatten → match owners → N-level groups

### Feasibility: PASS
- `get_org_tree()` already works (validated live with muralic, alexhowells)
- `OrgTree` model has all needed fields

### Risk Coverage: PASS
- Name collision handled by tree scoping
- "Unknown Owner" retained for debugging

## Architect Notes

### Data Model Change
- Replace `OrgAncestry(level1, level2)` NamedTuple with `OrgAncestry` containing a `path: tuple[str, ...]` — variable-length tuple of manager display names
- `path[0]` = root manager (always present for found owners); `path[-1]` = owner's nearest manager ancestor
- Path is NEVER empty for found owners — root manager is always `path[0]`
- IC names NEVER appear in path — only managers (people with `direct_reports` in the tree)
- `("Unknown Owner",)` for owners not found in tree

### Path Examples (muralic as root)
| Owner | Role | Path |
|---|---|---|
| Murali (root, owns service) | manager | `("Murali Chintalapati",)` |
| Arjun Mukherjee (IC direct of root) | IC | `("Murali Chintalapati",)` |
| Brent Jensen (mgr direct) owns service | manager | `("Murali Chintalapati", "Brent Jensen")` |
| Wei Zou (IC under brentj) | IC | `("Murali Chintalapati", "Brent Jensen")` |
| Chavi Gupta (IC under ropandey) | IC | `("Murali Chintalapati", "Rohit Pandey")` |
| Not found | — | `("Unknown Owner",)` |

### Contracts
- `get_org_mapping()` input: `owner_names: list[str]`, `manager_alias: str`
- `get_org_mapping()` output: `dict[str, OrgAncestry]` where `OrgAncestry.path` is the manager chain
- `get_service_owners()` output: `dict[str, list[str]]` (service_id → owner names)
- `flatten_org_tree()`: new helper, `OrgTree → dict[str, list[str]]` (display_name.lower() → ancestry path)

### Security: No change
- Same Azure CLI auth, same Graph scopes, same S360 tokens

### Rollback
- Revert to SFI-028 branch — fully committed and pushed
