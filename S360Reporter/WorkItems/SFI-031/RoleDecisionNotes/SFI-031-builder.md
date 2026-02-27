# SFI-031 — Builder Decision Notes

## Git Operations
- Created feature branch: `SFI-031`
- Committed: `SFI-031: Cache org-tree in get_org_mapping (24hr TTL)` (14 files, 797 insertions)

## Build Verification
- `pytest GUI/tests/ -m "not live"`: **254 passed**, 19 pre-existing errors, 0 new failures
- No build/packaging step required (library code, not a standalone build)

## Files Changed
- `GUI/src/sfi_reporter/services.py` — production code (cache helpers + modified `get_org_mapping`)
- `GUI/tests/test_sfi_031.py` — 11 new tests
- `WorkItems/SFI-031/` — all workflow artifacts
