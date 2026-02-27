# SFI-031 — Test Cases

## TC-1: Cache miss — no cache file exists
**Maps to**: AC-1 (no cache file → calls API, writes cache)
- Mock `get_cache_dir()` to return a temp directory
- Ensure no `{alias}_org_tree.json` exists
- Call `get_org_mapping(owner_names, manager_alias)`
- **Assert**: `client.get_org_tree()` called exactly once
- **Assert**: Cache file now exists with valid JSON containing `timestamp` and `tree` keys
- **Failure message**: "Expected org-tree cache file to be written on first call"

## TC-2: Cache hit — valid cache (< 24 hrs)
**Maps to**: AC-2 (valid cache → no API call)
- Pre-write a cache file with `timestamp` = 1 hour ago and a valid serialized tree
- Call `get_org_mapping(owner_names, manager_alias)`
- **Assert**: `client.get_org_tree()` NOT called
- **Assert**: Returned mapping matches the cached tree data
- **Failure message**: "Expected cache hit to skip get_org_tree call"

## TC-3: Stale cache — cache older than 24 hours
**Maps to**: AC-3 (stale cache → calls API, overwrites)
- Pre-write a cache file with `timestamp` = 25 hours ago
- Call `get_org_mapping(owner_names, manager_alias)`
- **Assert**: `client.get_org_tree()` called exactly once
- **Assert**: Cache file updated with new timestamp
- **Failure message**: "Expected stale cache to trigger fresh get_org_tree call"

## TC-4: Corrupt/empty cache file
**Maps to**: AC-4 (invalid cache → falls back to API)
- Pre-write a cache file with empty content / invalid JSON
- Call `get_org_mapping(owner_names, manager_alias)`
- **Assert**: `client.get_org_tree()` called exactly once
- **Assert**: Cache file overwritten with valid data
- **Failure message**: "Expected corrupt cache to trigger fallback to get_org_tree"

## TC-5: API exception — no corrupt cache written
**Maps to**: AC-5 (API failure → Unknown Owner, no cache written)
- Ensure no cache file exists
- Mock `client.get_org_tree()` to raise `Exception`
- Call `get_org_mapping(owner_names, manager_alias)`
- **Assert**: All owners mapped to `OrgAncestry(path=("Unknown Owner",))`
- **Assert**: No cache file written
- **Failure message**: "Expected API failure to skip cache write and map all to Unknown Owner"

## TC-6: Existing tests unchanged
**Maps to**: AC-6 (no regressions)
- Run full `pytest GUI/tests/ -m "not live"`
- **Assert**: Same pass/fail count as baseline (241 passed)

## TC-7: Cache key normalization
**Maps to**: Review comment (case normalization)
- Call with `manager_alias="BrentJ"` — cache file should use lowercase key
- **Assert**: File named `brentj_org_tree.json`
- **Failure message**: "Expected cache key to be lowercased"

## TC-8: Round-trip serialization fidelity
- Build an `OrgTree` with 3 levels of nesting
- Serialize → write → read → deserialize
- **Assert**: Reconstructed tree equals original (same structure, names, aliases)
- **Failure message**: "OrgTree round-trip serialization lost data"
