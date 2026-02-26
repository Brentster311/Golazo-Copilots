# SFI-039 — Quality Assurance Role Decision Notes

## Role: Quality Assurance
## Work Item: SFI-039 — Achieve 70% Code Coverage on All Source Files

---

## Decisions Made

### 1. Test case granularity — one ID per function/path, not per assertion
**Decision**: Each test case corresponds to one test function testing one specific behavior or code path, not a single assertion.
**Rationale**: Keeps tests focused and debuggable. If a test fails, the developer knows exactly which behavior broke.

### 2. Coverage estimation acknowledges dialogs.py and app.py need dev-time expansion
**Decision**: The test cases document provides 24 tests for `dialogs.py` and 32 for `app.py`, but honestly notes these may need expansion during implementation.
**Rationale**: These files have 790 and 681 statements respectively with very low baselines (14% and 0%). Prescribing 50+ tests each without seeing coverage output would be speculative. The developer should iterate using `--cov-report=term-missing` and add tests for uncovered lines.

### 3. Shared Tk root fixture at module scope
**Decision**: `tk_root` fixture uses `scope="module"` rather than `scope="session"` or `scope="function"`.
**Rationale**: Module scope balances startup cost (creating Tk root is ~50ms) against isolation. Session scope risks Tk state leaking between unrelated test modules. Function scope would be too slow for 100+ GUI tests.

### 4. Copilot SDK mock via `sys.modules` injection in conftest
**Decision**: Mock the `copilot` package via `sys.modules.setdefault("copilot", mock)` in conftest.py, loaded before any test module imports `copilot_tools` or `copilot_panel`.
**Rationale**: These modules import `from copilot import Tool, define_tool` at the top level. Without `sys.modules` injection, importing the module under test would fail if the `copilot` SDK isn't installed. This is the standard pattern for mocking optional dependencies.

### 5. Added async handler test cases for `_make_tool`
**Decision**: Included TC-CT-26 and TC-CT-27 to test the async wrapper inside `_make_tool`.
**Rationale**: The review identified that `_make_tool` creates an `async def _async_handler` with try/except and truncation logic. This is 15+ statements that wouldn't be covered by only testing the synchronous `handler` closures. Using `asyncio.run()` in these tests covers the async wrapper path.

### 6. Parameterized approach recommended for fetch cascade tests
**Decision**: Recommended (in test cases) that `test_fetch_url_content_*` tests use `@pytest.mark.parametrize` with different mock configurations for the 5 cascade paths.
**Rationale**: The `fetch_url_content` function has 5 distinct code paths (CDP success, auth→bearer success, auth→edge success, auth→all fail, fallback urllib). Parameterization reduces boilerplate while covering all paths.

### 7. Security test case for path-traversal in read_fetched_doc
**Decision**: Added TC-CT-22 specifically for the path-traversal guard in `_build_read_fetched_doc`.
**Rationale**: This is a security-relevant code path — the handler rejects filenames containing `../`, `/`, or `\`. A dedicated test ensures this guard isn't accidentally removed in future changes.

### 8. Total test count: 148 across 7 files
**Decision**: Defined 148 concrete test cases, exceeding the design doc's estimate of ~114.
**Rationale**: Upon detailed inspection of the source code, more test paths were identified than the design doc estimated. The additional tests primarily cover error paths, edge cases, and the async handler wrapper in copilot_tools. The extra tests provide a safety margin for hitting 70%.

## Assumptions Made

1. **`copilot` SDK is not installed in the test environment** — all tests mock it via `sys.modules`.
2. **Tk is available** — tests skip gracefully via `pytest.importorskip("tkinter")` if not.
3. **No existing test files are modified** — all 7 test files are new per PM decision.
4. **`pytest-cov` is installed** — the developer role should verify and install if missing.
5. **Coverage is statement-based** — matching the user story and PM decision.

## Artifacts Created

- `WorkItems/SFI-039/Design/SFI-039-Review-Comments.md` — Design review with 8 observations, all advisory (no blockers).
- `WorkItems/SFI-039/Design/SFI-039-Test-Cases.md` — 148 test cases across 7 files with traceability to acceptance criteria.
- `WorkItems/SFI-039/RoleDecisionNotes/SFI-039-quality-assurance.md` — This file.
