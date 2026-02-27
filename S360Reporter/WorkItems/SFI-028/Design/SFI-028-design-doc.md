# SFI-028 Design Doc — Replace S360 Chain-Walking with MS Graph in S360Reporter

## Summary
Replace the `get_org_mapping()` function in `tk_app.py` to use `client.get_manager_chain()` from SFI-027's Graph API instead of parallel `client.search()` calls with S360 Managers JSON parsing.

## Problem Statement
SFI-026 failed in production because S360 `search()` chain-walking produced incorrect results for multi-team managers. The root cause: extracting `manager_alias` from the first `TeamGroup` entry was unreliable. SFI-027 added a robust MS Graph-based hierarchy API to accia-s360. Now S360Reporter needs to consume it.

## Proposed Approach

### Current flow (to be replaced)
```
get_org_mapping(owner_names, manager_alias):
  for each owner_name (parallel):
    client.search(owner_name)          # S360 search
    parse Managers JSON from result     # fragile
    find manager_alias in chain         # can fail for multi-team
    resolve display names via search()  # more S360 calls
    return OrgAncestry(level1, level2)
```

### New flow
```
get_org_mapping(owner_names, manager_alias):
  for each owner_name (parallel):
    find owner_alias from search results (already fetched in get_service_owners)
    client.get_manager_chain(owner_alias)  # MS Graph API
    find manager_alias in chain            # reliable alias comparison
    use OrgPerson.display_name for names   # no extra search() calls
    return OrgAncestry(level1, level2)
```

### Key changes in `get_org_mapping()`:
1. **Replace `client.search(owner_name)` + Managers parsing** with `client.get_manager_chain(owner_alias)`
2. **Replace `_resolve_display_name(client, alias)`** with `OrgPerson.display_name` from the chain
3. **Owner alias resolution**: Use the S360 search result's `Id` field (which we already get in `get_service_owners`) to map owner display_name → alias. Pass alias map into `get_org_mapping`.
4. **Chain walking logic**: `get_manager_chain()` returns `[immediate_mgr, ..., CEO]`. Find `manager_alias` in this list. Everything below it maps to level1/level2.

### Detailed algorithm:
```python
chain = client.get_manager_chain(owner_alias)  # [imm_mgr, ..., CEO]
chain_aliases = [p.alias for p in chain]

if owner_alias == manager_alias:
    return OrgAncestry(owner_display_name, None)

if manager_alias not in chain_aliases:
    return OrgAncestry("Unknown Owner", None)

mgr_idx = chain_aliases.index(manager_alias)
# entries BEFORE manager_alias in chain = people between owner and manager
hops = mgr_idx  # number of managers between owner and the viewer

if hops == 0:
    # owner's immediate manager IS manager_alias → direct report
    return OrgAncestry(owner_display_name, None)
elif hops == 1:
    # 1 hop → owner reports to a direct report
    level1_name = chain[0].display_name  # immediate manager (viewer's direct)
    return OrgAncestry(level1_name, owner_display_name)
else:
    # 2+ hops → cap at 2 levels
    level1_name = chain[mgr_idx - 1].display_name  # viewer's direct
    level2_name = chain[mgr_idx - 2].display_name  # one below direct
    return OrgAncestry(level1_name, level2_name)
```

### Alias resolution approach:
Modify `get_service_owners()` to also return owner aliases (from S360 search `Id` field) alongside display names. This gives us the mapping needed to call `get_manager_chain(alias)`.

## Files Changed
- `GUI/src/sfi_reporter/tk_app.py`: Rewrite `get_org_mapping()`, update `get_service_owners()` to return aliases

## Test Strategy
- All 30 existing SFI-026 tests must pass (tests mock `get_client` so mocks need updating to provide `get_manager_chain` instead of `search`)
- Note: The existing tests mock `sfi_reporter.data.get_client` — the mock client will need `get_manager_chain` method
