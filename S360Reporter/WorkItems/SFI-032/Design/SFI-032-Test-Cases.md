# SFI-032 — Test Cases

## TC-1: Cache miss — no file → API called, cache written
- Build GraphEndpoint with `cache_enabled=True` and a tmp cache dir
- Call `_build_subtree` for a person
- Assert: Graph API called, cache file `org_tree_{alias}.json` created

## TC-2: Cache hit — fresh file → no API call
- Pre-write a valid cache file (< 24 hr)
- Call `_build_subtree` for the same alias
- Assert: Graph API NOT called, returns correct tree

## TC-3: Stale cache — file > 24 hr → API called, file overwritten
- Pre-write cache file with timestamp 25 hours ago
- Call `_build_subtree`
- Assert: Graph API called, cache file updated

## TC-4: Corrupt cache → fallback to API
- Write invalid JSON to cache file
- Call `_build_subtree`
- Assert: Graph API called, cache file overwritten with valid data

## TC-5: cache_enabled=False → no caching
- Build GraphEndpoint with `cache_enabled=False`
- Call `_build_subtree`
- Assert: Graph API called, NO cache file written

## TC-6: services.py cache code removed
- Assert: `_serialize_org_tree`, `_read_org_tree_cache`, etc. no longer importable from `sfi_reporter.services`

## TC-7: get_org_mapping still works (integration)
- Mock `client.get_org_tree` → returns tree
- Call `get_org_mapping`
- Assert: correct OrgAncestry mappings (same as before)

## TC-8: Existing tests pass
- `pytest accia-s360/tests/ -m "not live"` — no regressions
- `pytest GUI/tests/ -m "not live"` — no regressions
