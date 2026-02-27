# Retrospective — SFI-029

## What Went Well

1. **TDD discipline**: Writing 13 tests first (in prior session) made the implementation phase clean and confident. Every production change was immediately verifiable.
2. **Design doc accuracy**: The 3-phase implementation plan in the design doc mapped directly to the actual implementation steps. No surprises.
3. **Net code reduction**: 21 files changed, 1174 insertions vs 1379 deletions — net -205 lines despite adding N-level capability. Simpler is better.
4. **Test isolation**: SFI-029/026/028 unit tests pass independently of API, environment, or Tcl/Tk availability.
5. **PyInstaller build**: Passed on first attempt with no new issues.

## What Didn't Go Well

1. **Missed test_sfi_026_live.py**: The live integration test file was not identified during the design/QA phase as needing updates. It referencing old `level1`/`level2` attributes caused 8 failures in the full regression. Caught and fixed during developer phase.
2. **Terminal buffer saturation**: The full 292-test regression run (~131s) produced so much output that subsequent terminal commands couldn't display new results. Had to use subagent workarounds to get clean test summaries.
3. **Pre-existing test failures**: 19 errors from missing `pytest-mock` and 1 Tcl/Tk failure obscure the signal. These should be fixed or skipped.

## Action Items

| # | Proposal | Priority |
|---|----------|----------|
| 1 | **Add `test_sfi_026_live.py` to impact analysis** — when changing `OrgAncestry` or related functions, the QA/architect phases should list ALL test files that import affected symbols | Medium |
| 2 | **Install `pytest-mock`** — would eliminate 19 fixture errors in test_data.py, test_llm_client.py, test_tk_app.py | High |
| 3 | **Use `--tb=no -q` for regression runs** — reduces output to summary line only, preventing terminal buffer issues | Low |

## Metrics

- **Test pass rate (non-live, non-infrastructure)**: 241/241 (100%) — no regressions
- **Implementation sessions**: 1 session for all production code + test updates
- **Golazo roles completed**: 9/9
