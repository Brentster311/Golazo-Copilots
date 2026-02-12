# SFI-034 Retrospective

## What Went Well
- **Clean module design**: `kpi_analyzer.py` was easy to test in isolation — 15 tests covering all public functions, zero mocking of external services needed for unit tests
- **TDD approach paid off**: Writing tests first caught edge cases (empty items, no URLs, truncation boundaries) before they became bugs  
- **Stdlib-only implementation**: No new dependencies — `urllib.request`, `html.parser`, `concurrent.futures` are all stdlib, keeping the dep footprint small
- **Thread-safe integration**: `send_analysis_prompt()` correctly marshals to the Tk main thread, avoiding cross-thread UI access
- **Existing patterns reused**: `root._sfi_app` pattern is minimal and effective for app discovery without circular imports

## What Didn't Go Well
- **MCP workspace path issue**: `gcp_create_workitem` created `state.json` at `C:\Users\Brent\WorkItems\SFI-034` instead of the workspace path. Required manual copy and explicit `workspace_path` parameter on all subsequent calls. This caused confusion early in the workflow.
- **test_sfi_033 regression**: Replacing the stub broke an existing test that asserted stub behavior. Should have identified and updated `test_sfi_033` as part of the developer checklist before running the full suite.

## Action Items
1. **Always pass `workspace_path` to `gcp_*` MCP calls** — don't rely on auto-detection
2. **When replacing stubs, grep for tests that assert stub behavior** — update them as part of the same change, not as a follow-up fix

## Metrics
- **Tests**: 15 new (all pass), 1 updated (was failing, now passes)
- **Files changed**: 4 modified, 2 new production files, 1 new test file
- **Lines**: +1,292 / -26
- **Workflow time**: ~1 session, all roles completed sequentially
