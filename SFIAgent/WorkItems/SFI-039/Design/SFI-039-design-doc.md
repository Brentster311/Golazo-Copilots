# SFI-039 Design Document — Achieve 70% Code Coverage on All Source Files

## Summary

Write new unit tests (no production code changes) for seven under-covered source files in `SFIReporter/src/sfi_reporter/` to bring every file to ≥ 70 % statement coverage as measured by `pytest-cov`.

## Problem Statement

Seven source files currently fall below the 70 % coverage threshold. The largest gaps are in the Tkinter GUI layer (`app.py` 0 %, `dialogs.py` 14 %) and the Copilot integration layer (`copilot_tools.py` 0 %, `copilot_panel.py` 34 %). Without adequate test coverage, regressions in core UI flows, query logic, logging setup, and copilot tooling go undetected until manual testing.

## Business Case

| Dimension | Detail |
|-----------|--------|
| **Why now** | The project is stable enough that adding test coverage has high ROI — no major feature churn. Several SFI work items (SFI-023 through SFI-038) have added significant functionality without proportional test investment. |
| **Impact** | Catching regressions earlier reduces manual QA time and production incident frequency. |
| **KPIs** | Every file listed in the coverage table reaches ≥ 70 % statement coverage. Total test suite runtime stays under 120 s. No individual test > 2 s. |

## Stakeholders

| Role | Responsibility |
|------|---------------|
| Developer (implementer) | Write new test files, fixture factories, mock patterns. |
| Quality Assurance | Define test-case matrix, verify coverage numbers post-implementation. |
| Build / CI | Confirm `pytest --cov` gate passes after merge. |

## Functional Requirements

1. **FR-1 – `logging_config.py` ≥ 70 %**: Test `setup_logging` (idempotency, handler creation), `patch_subprocess_windows` (idempotency, platform guard), `get_log_path`.
2. **FR-2 – `kpi_analyzer.py` ≥ 70 %**: Cover remaining ~58 stmts — likely `_fetch_via_cdp`, `_fetch_with_bearer_token`, `_fetch_via_urllib` error paths, `_is_js_shell`, `_is_login_page` edge cases, `truncate_content`, `collect_urls`.
3. **FR-3 – `query_builder.py` ≥ 70 %**: Cover remaining ~129 stmts — `ClauseRow` widget, `QueryBuilder` dialog lifecycle, `_build_field_metadata`, `_enrich_items`, date-clause edge cases.
4. **FR-4 – `copilot_tools.py` ≥ 70 %**: Test each `_build_*` tool builder, `_get_items`, `_summarise_item`, `_truncate`, `set_current_docs_dir`, `_build_read_fetched_doc`, `build_tools`.
5. **FR-5 – `copilot_panel.py` ≥ 70 %**: Test `AsyncBridge` lifecycle, `CopilotPanel` UI build, message rendering (`_append_message`, `_render_markdown`, `_insert_inline_md`), session event handling, send/stop flows.
6. **FR-6 – `dialogs.py` ≥ 70 %**: Test `SortableTreeview` sorting, `ColumnSelectorDialog` select/clear/apply, `DetailModal` row population and double-click, `ItemDetailsModal` content build and link insertion, `SingleEtaEditDialog` save flow.
7. **FR-7 – `app.py` ≥ 70 %**: Test `SFIReporterApp.__init__` and `_build_ui`, `_update_tables` with various data shapes, `_load_cached_data`, `_on_refresh` / `_on_refresh_complete`, `_on_update_etas` / `_on_eta_update_complete`, `_on_query` / `_on_filter_applied`, `_on_clear_cache`, `_toggle_copilot_panel`, `_on_service_double_click` / `_on_program_double_click` / `_on_action_double_click` / `_on_kpi_right_click`, `_on_retry_failed` / `_on_retry_complete`, `main()`.

## Non-Functional Requirements

| NFR | Target |
|-----|--------|
| **Speed** | No single test > 2 s; total suite < 120 s. |
| **No production changes** | Zero edits to files under `src/sfi_reporter/`. |
| **Isolation** | Tests must not open real Tk windows, call real APIs, or create files outside `tmp_path`. |
| **Maintainability** | Shared fixtures and mock factories in `conftest.py` or dedicated helpers to reduce duplication. |
| **Determinism** | No flaky tests — freeze time where needed, seed random values. |

## Proposed Approach (High Level)

### Phase 1 — Quick wins (logging_config, kpi_analyzer)
- **`test_logging_config.py`** — straightforward: mock `RotatingFileHandler`, `sys.platform`, test each function.
- **`test_kpi_analyzer_extended.py`** — extend existing tests with error-path and edge-case scenarios for fetch functions.

### Phase 2 — Pure-logic modules (query_builder, copilot_tools)
- **`test_query_builder_extended.py`** — add Tk-widget tests for `ClauseRow` / `QueryBuilder` using `tk.Tk()` in a fixture that calls `root.destroy()` in teardown. Test `_enrich_items`, `_build_field_metadata`, aggregate helpers.
- **`test_copilot_tools.py`** — mock `SFIReporterApp` data, test each tool builder's handler output. Mock `copilot` SDK imports.

### Phase 3 — GUI-heavy modules (copilot_panel, dialogs, app)
- **`test_copilot_panel.py`** — mock `copilot` SDK, test `_build_ui`, message formatting, event routing.
- **`test_dialogs_extended.py`** — instantiate dialogs with headless Tk root, verify widget states, sort logic, callback invocations.
- **`test_app.py`** — create `SFIReporterApp` with heavily-patched dependencies; test method-level behavior via mock interactions.

### Tk Mocking Strategy
Use a real `tk.Tk()` per test class (created once, destroyed on teardown) with all external dependencies (Graph API, cache, filesystem) patched out. For truly headless CI, wrap root creation in a `pytest.fixture` that skips if `$DISPLAY` / `$TK_SILENT_EXIT` is unavailable.

### File-to-Test Mapping

| Source File | New Test File | Est. New Tests |
|-------------|--------------|:--------------:|
| `logging_config.py` | `test_logging_config.py` | ~8 |
| `kpi_analyzer.py` | `test_kpi_analyzer_extended.py` | ~12 |
| `query_builder.py` | `test_query_builder_extended.py` | ~15 |
| `copilot_tools.py` | `test_copilot_tools.py` | ~18 |
| `copilot_panel.py` | `test_copilot_panel.py` | ~16 |
| `dialogs.py` | `test_dialogs_extended.py` | ~20 |
| `app.py` | `test_app_coverage.py` | ~25 |

**Total**: ~114 new test functions across 7 new test files.

## Alternatives Considered

| Alternative | Why Rejected |
|-------------|-------------|
| **Use coverage pragmas (`# pragma: no cover`)** | Hides gaps rather than fixing them; violates the spirit of the work item. |
| **Refactor production code first to improve testability** | Out of scope per user story — adds risk and scope creep. |
| **GUI integration tests with real Tk mainloop** | Too slow, flaky in CI, hard to maintain. Mocked approach is sufficient for statement coverage. |
| **Property-based testing (Hypothesis)** | Overkill for coverage targets; may add later for query_builder date logic. |

## Risks, Mitigations, Open Questions

### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|-----------|
| **Tk availability in CI** | Medium | High | Fixture skips gracefully; most tests mock at widget level. |
| **Mocking drift** — tests pass but mocks diverge from real behavior | Medium | Medium | Keep mocks shallow; test via public method signatures, not internals. |
| **Test speed** — GUI instantiation overhead | Low | Medium | Share `tk.Tk()` root per class; destroy once at end. |
| **Coverage < 70 % despite effort** — some branches deeply nested in UI callbacks | Low | Medium | Prioritize highest-statement methods first; accept minor exceptions only if documented. |

### Open Questions

1. Should existing test files (e.g., `test_query_builder.py`, `test_tk_app.py`) be extended, or should all new coverage go in new files to keep diffs clean? **Decision: Create new files to avoid merge conflicts and keep existing tests stable.**
2. Is there a CI pipeline that enforces the 70 % gate? **Assumption: Not yet — the build role should verify coverage locally; CI enforcement is a future work item.**

## Dependencies

| Dependency | Type | Notes |
|-----------|------|-------|
| `pytest` ≥ 7.0 | Dev dependency | Already in `pyproject.toml` |
| `pytest-mock` ≥ 3.10 | Dev dependency | Already in `pyproject.toml` |
| `pytest-cov` | Dev dependency | Needed for coverage measurement — **must be present** |
| `tkinter` | Stdlib | Available in standard CPython; may not be in minimal Docker images |
| `copilot` SDK (mocked) | Runtime dep (mocked) | `copilot_panel.py` and `copilot_tools.py` import from `copilot` — must be mocked in tests |
| Existing test infrastructure | Local | `conftest.py`, existing fixtures in `test_query_builder.py` etc. |

## Migration / Rollout / Rollback Plan

| Phase | Action |
|-------|--------|
| **Rollout** | Merge new test files to main branch. No production code changes — zero risk to runtime behavior. |
| **Validation** | Run `pytest --cov=sfi_reporter --cov-report=term-missing` and verify every file ≥ 70 %. |
| **Rollback** | Delete the new test files. No other changes to undo. |

## Observability Plan

- **Coverage report**: `pytest --cov=sfi_reporter --cov-report=html` produces an HTML report in `htmlcov/`.
- **Per-file metrics**: The `term-missing` report shows exact uncovered lines.
- **CI gate (future)**: Add `--cov-fail-under=70` to pytest invocation in CI config.

## Test Strategy Summary

| Aspect | Approach |
|--------|---------|
| **Framework** | `pytest` + `pytest-mock` + `pytest-cov` |
| **GUI mocking** | Real `tk.Tk()` root shared per test class with all I/O patched; alternatively, mock `tk.*` entirely for CI without display. |
| **API mocking** | `unittest.mock.patch` on `sfi_reporter.data`, `sfi_reporter.services`, `sfi_reporter.cache` entry points. |
| **Copilot SDK mocking** | Mock `copilot` module imports (`CopilotClient`, `define_tool`, `Tool`, `ToolResult`). |
| **Filesystem** | Use `tmp_path` fixture for cache/log operations. |
| **Coverage measurement** | `pytest --cov=sfi_reporter --cov-report=term-missing` |
| **Pass criteria** | All 7 files ≥ 70 % statement coverage; no test > 2 s; total suite < 120 s. |
| **Execution order** | Phase 1 (logging, kpi_analyzer) → Phase 2 (query_builder, copilot_tools) → Phase 3 (copilot_panel, dialogs, app). |
