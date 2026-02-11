# SFI-028 Developer Decision Notes

## Summary
Replaced S360 `search()` chain-walking in `get_org_mapping()` with MS Graph `get_manager_chain()` API from accia-s360 (SFI-027). Updated `get_service_owners()` to return alias mapping alongside service owners. Updated `do_refresh()` to wire the two together.

## TDD Cycle

### Red Phase
- Created `test_sfi_028.py` with 12 tests (10 for `get_org_mapping` Graph API, 2 for `get_service_owners` tuple return)
- Verified 11/12 fail (1 backward-compat test already passes) before writing production code

### Green Phase
- Rewrote `get_org_mapping()` — uses `client.get_manager_chain(alias)` instead of `client.search(name)`
- Rewrote `get_service_owners()` — returns `tuple[dict, dict]` with alias resolution phase
- Updated `do_refresh()` — unpacks tuple, passes `owner_aliases` to `get_org_mapping()`
- All 12 new tests pass; 42/42 total (30 SFI-026 + 12 SFI-028)

## Key Design Decisions

### 1. `owner_aliases` as keyword-only parameter
`get_org_mapping()` accepts `owner_aliases: Optional[dict[str, str]] = None` after `*` separator. This preserves backward compatibility — callers without alias data get "Unknown Owner" fallback rather than crashing.

### 2. Alias resolution in `get_service_owners()`
Added a second phase after collecting service owners: parallel S360 search per unique owner display name to extract `Id` field as alias. Matches on `Owners` or `Name` field (case-insensitive).

### 3. Chain index math
Per design doc: `chain = [immediate_mgr, ..., CEO]`, find `manager_alias` at `mgr_idx`. `hops = mgr_idx`. If hops==0 → direct report. If hops==1 → `chain[0]` is L1, owner is L2. If hops>=2 → `chain[mgr_idx-1]` is L1, `chain[mgr_idx-2]` is L2.

### 4. Removed `_resolve_display_name()` inner function
No longer needed — `OrgPerson.display_name` from Graph API replaces the S360 search-based name resolution.

### 5. Preserved ThreadPoolExecutor patterns
Both `get_org_mapping()` (max_workers=8) and `get_service_owners()` (max_workers=10) maintain existing concurrency approach.

## Files Changed
| File | Change |
|------|--------|
| `SFIReporter/src/sfi_reporter/tk_app.py` | Rewrote `get_org_mapping()`, `get_service_owners()`, updated `do_refresh()` |
| `SFIReporter/tests/test_sfi_028.py` | New: 12 tests for Graph API integration |
| `SFIReporter/tests/test_sfi_026.py` | Updated `TestGetOrgMappingMultiLevel` to use Graph API mocks |

## Test Results
- **Unit tests**: 42/42 pass (SFI-026 + SFI-028)
- **Full regression**: 276/276 non-live, non-infra tests pass
- **Pre-existing failures**: 6 failed (1 tkinter TCL env, 5 live integration), 19 errors (missing pytest-mock)
- **PyInstaller build**: `SFIReporter.exe` builds successfully

## Known Issues
- `test_sfi_026_live.py` shows 97% "Unknown Owner" — alias resolution via S360 search may not reliably find Org results for all names against the real API. This is a pre-existing SFI-026 issue (BACKLOG status) and does not block SFI-028.
