# SFI-032 Design Doc — Move org-tree cache into `_build_subtree`

## Summary
Move the 24-hour org-tree file cache from `sfi_reporter.services.get_org_mapping()` down into `accia_s360.endpoints.graph.GraphEndpoint._build_subtree()`. This makes caching transparent to all SDK consumers and enables per-alias granular caching.

## Problem Statement
SFI-031 added org-tree caching in `services.py` — the wrong layer. The cache belongs in the SDK (`accia-s360`) so any consumer benefits. Additionally, the current approach caches the entire tree as one blob. Moving caching into `_build_subtree` caches each person's subtree individually, so later queries for sub-managers are instant.

## Proposed Approach

### In `graph.py` (add)
1. Add private helpers `_serialize_tree`, `_deserialize_tree`, `_read_subtree_cache(alias)`, `_write_subtree_cache(alias, tree)` as methods on `GraphEndpoint`.
2. Modify `_build_subtree(person, remaining_depth)`:
   - Check `self.config.cache_enabled`
   - If enabled, call `_read_subtree_cache(person.alias)` — on hit, return cached tree
   - If miss, proceed with existing logic (fetch reports, recurse)
   - After building the subtree, call `_write_subtree_cache(person.alias, tree)`
3. Cache file location: `self.config.get_cache_dir() / f"org_tree_{alias}.json"`
4. TTL: 24 hours (constant `_ORG_TREE_CACHE_TTL_HOURS = 24`)

### In `services.py` (remove)
1. Remove `_serialize_org_tree`, `_deserialize_org_tree`, `_read_org_tree_cache`, `_write_org_tree_cache`, `ORG_TREE_CACHE_TTL_HOURS`
2. Simplify `get_org_mapping()` — remove cache check/write, just call `client.get_org_tree(cache_key)` directly (SDK handles caching)
3. Remove unused imports (`os`, `tempfile`, `Path`, `timedelta`)

### Tests
1. Add cache tests to `accia-s360/tests/test_graph_endpoint.py` (cache hit/miss/stale/corrupt/disabled)
2. Update `SFIReporter/tests/test_sfi_031.py` — remove/adapt tests that mock services-layer cache functions
3. All existing tests must continue to pass

## Risks & Mitigations
| Risk | Mitigation |
|------|-----------|
| Existing SFI-031 tests break | Update mocks to reflect new architecture |
| Cache dir doesn't exist | `config.get_cache_dir()` already creates it |

## Rollback
Revert graph.py changes, restore services.py cache code. Cache files are harmless leftovers.
