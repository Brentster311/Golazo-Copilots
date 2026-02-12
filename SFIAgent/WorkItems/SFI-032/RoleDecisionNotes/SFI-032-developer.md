# SFI-032 Developer Notes

## Summary

Moved org-tree caching from `SFIReporter/services.py` (application layer) into `accia-s360/endpoints/graph.py` (SDK layer) at the `_build_subtree` method level.

## Changes Made

### accia-s360/src/accia_s360/endpoints/graph.py
- Added imports: `json`, `os`, `tempfile`, `datetime`, `timedelta`
- Added constant: `_ORG_TREE_CACHE_TTL_HOURS = 24`
- Added instance methods: `_serialize_tree`, `_deserialize_tree`, `_read_subtree_cache`, `_write_subtree_cache`, `_cache_path`
- Modified `_build_subtree` to check cache on entry (when `config.cache_enabled`) and write cache after building the tree
- Cache file pattern: `org_tree_{alias}.json` in `config.get_cache_dir()`
- Atomic writes via `tempfile.mkstemp` + `os.replace`

### SFIReporter/src/sfi_reporter/services.py
- Removed: `ORG_TREE_CACHE_TTL_HOURS`, `_serialize_org_tree`, `_deserialize_org_tree`, `_read_org_tree_cache`, `_write_org_tree_cache`
- Removed unused imports: `os`, `tempfile`, `Path`, `timedelta`
- Simplified `get_org_mapping`: no longer checks/writes cache (SDK handles it)
- Updated `__all__` to remove cache exports

### accia-s360/tests/test_graph_endpoint.py
- Added `TestSubtreeCache` class with 6 tests: cache miss, cache hit, stale cache, corrupt cache, cache disabled, round-trip fidelity
- Added `cached_graph` and `nocache_graph` fixtures using `tmp_path`
- Fixed base `config` fixture to use `cache_enabled=False` to prevent cross-test contamination

### SFIReporter/tests/test_sfi_031.py
- Rewrote to 4 tests covering `get_org_mapping` responsibilities post-refactor: API failure, alias normalisation, empty owners, correct mapping result
- Removed all service-layer cache tests (now tested in SDK layer)

## TDD Cycle
- **Red**: 6 tests in `TestSubtreeCache` — 3 failed as expected
- **Green**: Implemented cache in `_build_subtree` — all 6 pass
- **Refactor**: Fixed base `config` fixture to isolate tests

## Test Results
- accia-s360: 76 passed, 1 warning
- SFIReporter (core): 21 passed, 5 errors (pre-existing Azure CLI issues in `test_data.py`)
