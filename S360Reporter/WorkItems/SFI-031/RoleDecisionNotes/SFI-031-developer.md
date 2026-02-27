# SFI-031 — Developer Decision Notes

## Implementation Summary
Added 24-hour file-based caching for the `client.get_org_tree()` call inside `get_org_mapping()`.

## Changes Made

### `services.py`
- Added imports: `os`, `tempfile`, `datetime`, `timedelta`, `Path`
- Added constant: `ORG_TREE_CACHE_TTL_HOURS = 24`
- Added `_serialize_org_tree(tree)` — recursive OrgTree → dict
- Added `_deserialize_org_tree(data)` — recursive dict → OrgTree
- Added `_read_org_tree_cache(manager_alias)` — reads & validates cache file
- Added `_write_org_tree_cache(manager_alias, tree)` — atomic write via temp file + os.replace
- Modified `get_org_mapping()`:
  - Normalizes `manager_alias` to lowercase for cache key
  - Checks cache first via `_read_org_tree_cache`
  - On miss: calls `client.get_org_tree(cache_key)` then `_write_org_tree_cache`
  - On hit: skips API call entirely
  - On API failure: no cache written (existing behavior preserved)

### `test_sfi_031.py` (11 tests)
- 3 serialization round-trip tests
- 8 integration tests: cache miss, hit, stale, corrupt, empty, API failure, case normalization, result equivalence

## TDD Compliance
- Tests written first (red phase: 8 failed, 3 passed)
- Production code written to make all pass (green phase: 11 passed)
- Full suite: 254 passed, 0 new failures, 19 pre-existing errors (unchanged)
