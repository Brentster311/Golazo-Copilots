# SFI-029 — Test Cases

## TC-01: Single `get_org_tree()` call (AC-1)
- Mock `client.get_org_tree(manager_alias)` → verify called once
- Verify NO `get_manager_chain()` calls made
- Verify NO S360 search calls for alias resolution

## TC-02: `get_service_owners()` returns simple dict (AC-2)
- Verify return type is `dict[str, list[str]]` not `tuple`
- Verify no `resolve_alias()` / S360 people search calls

## TC-03: No `owner_aliases` parameter (AC-3)
- Verify `get_org_mapping()` signature has no `owner_aliases` param
- Verify `do_refresh()` doesn't pass `owner_aliases`

## TC-04: ICs never shown in tree (AC-4)
- Org tree: manager with IC direct reports
- IC names never appear anywhere in the services tree — not as group headers, not as leaf rows
- Services owned by ICs appear under their nearest manager ancestor's group
- Specifically: Bhavya Gopal (IC under Karan Parkash) owns "ServiceX" → "ServiceX" appears under Karan's group

## TC-05: N-level nesting (AC-5)
- 4-level tree: alex(root) → muralic(mgr) → brentj(mgr) → Wei Zou(IC) owns "ServiceX"
- Verify 3 group levels created: Alex Howells → Murali Chintalapati → Brent Jensen
- Root (alex) IS a group (`path[0]`)
- path = `("Alex Howells", "Murali Chintalapati", "Brent Jensen")`
- "ServiceX" is a leaf row under Brent Jensen's group
- Wei Zou's name never appears in the tree

## TC-06: Expand/collapse defaults (AC-6)
- Root-level groups: `open=True`
- All child groups: `open=False`

## TC-07: Owner name disambiguation
- Two people named "Rohit Pandey" in different orgs
- Only one in manager's tree → correct match

## TC-08: Owner IS the root manager
- Service owned by the root manager (viewer) themselves
- Path = `("Murali Chintalapati",)` — service under root manager's own group
- Root manager group always exists for found owners

## TC-08b: IC direct report of root
- IC directly under root with no intermediate manager (e.g., Arjun Mukherjee under muralic)
- Arjun has no `direct_reports` → not a manager → no group header
- Service owned by Arjun: path = `("Murali Chintalapati",)` — under root's group directly

## TC-09: Owner not found in tree
- Owner name doesn't match any `display_name` in tree
- Maps to "Unknown Owner" group
- WARNING logged

## TC-10: `<Person's> Team` service
- Service named "Rohit Pandey's Team"
- Rohit Pandey should appear as manager-level group

## TC-11: Empty org tree
- Manager has zero direct reports (but IS a manager node)
- Root manager still appears as group header
- Services owned by the manager → path `("Manager Name",)`
- Services owned by unknown people → path `("Unknown Owner",)`

## TC-12: Regression — existing SFI-026/028 tests adapted
- All aggregation tests pass with new data model
- All tree population tests pass

## TC-13: Live validation (AC-8)
- brentj org tree → correct grouping for brentj's services
- muralic org tree → correct N-level grouping
- alexhowells org tree → correct 3+ level grouping

## TC-14: PyInstaller build (AC-9)
- `pyinstaller --clean SFIReporter.spec` succeeds
- Built exe launches successfully
