# SFI-028 Retrospective

## What Went Well
- **Express profile was efficient**: Definition roles (PO, PM, QA, Architect) completed quickly with clear, focused artifacts
- **TDD red-green cycle was clean**: 12 tests written → 11 failed → implementation → all 12 pass. No rework needed.
- **Design doc accuracy**: Chain index math algorithm from design doc translated directly to working code
- **Backward compatibility preserved**: `owner_aliases` as keyword-only param with None default kept existing callers working
- **Regression stability**: 276/276 non-live tests pass; no regressions introduced

## What Didn't Go Well
- **SFI-026 test updates required**: AC-4 stated "All 30 existing SFI-026 unit tests pass without modification" — but `TestGetOrgMappingMultiLevel` (8 tests) needed rewriting to mock `get_manager_chain` instead of `search`. The acceptance criterion was overly optimistic.
- **Live test failures persist**: `test_sfi_026_live.py` shows 97% "Unknown Owner" — alias resolution via S360 search doesn't reliably find people. This predates SFI-028 but remains unfixed.
- **Terminal session pollution**: PyInstaller build attempts got tangled with test outputs in the shared terminal session.

## Action Items
1. **Write ACs more carefully for refactoring stories**: When rewriting internals, existing tests that mock the old implementation *will* need updates. AC should say "All 30 tests pass with necessary mock updates" not "without modification".
2. **Investigate live alias resolution**: The S360 search → alias flow in `resolve_alias` may need a Graph API-based approach (search by display name in AAD) rather than S360 search to be reliable. Candidate for a new work item.
3. **Capability registry was not consulted**: Should have run `gcp_capabilities(action="impact", files=[...])` during developer role for changed files.

## Metrics
- **Defect rate**: 0 regressions in 276 unit tests
- **Cycle time**: Express profile, all roles completed in single session
- **Test coverage delta**: +12 new tests (42 total for org mapping functionality)
