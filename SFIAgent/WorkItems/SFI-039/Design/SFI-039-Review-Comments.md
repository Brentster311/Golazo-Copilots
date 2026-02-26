# SFI-039 — QA Review Comments

## Review Scope

Reviewed the design document (`SFI-039-design-doc.md`), user story, program-manager decisions, and all 7 target source files against acceptance criteria and non-functional requirements.

---

## Approval Status: **APPROVED with observations**

The design is well-structured, the phased approach is sound, and the file-to-test mapping is concrete enough for direct implementation. Observations below are advisory — none are blockers.

---

## Review Comments

### RC-1: Copilot SDK import mocking needs explicit guidance *(Medium)*

**File**: `copilot_tools.py`, `copilot_panel.py`

Both files import directly from `copilot` at module level:
```python
from copilot import define_tool, Tool  # copilot_tools.py line 13
```

The design says "mock copilot module imports" but doesn't specify _how_. The developer should use `sys.modules` injection **before** importing the module under test, e.g.:

```python
sys.modules["copilot"] = MagicMock()
```

If the developer imports `copilot_tools` without this, the test will crash if the `copilot` package isn't installed. The test cases below assume this pattern.

### RC-2: `_make_tool` async handler needs coverage *(Low)*

`_make_tool` wraps each tool handler in an `async def _async_handler(invocation)` that catches exceptions and returns `ToolResult`. The test cases should invoke the async handler path (via `asyncio.run`) to cover the try/except and the truncation logic. Added specific test cases for this.

### RC-3: `AnalysisResult.__str__` is trivial but still needs a test *(Low)*

`AnalysisResult.__str__` returns `self.prompt` — trivial, but the 70% gate counts every statement. Included in test cases.

### RC-4: `SortableTreeview.sort_by_columns` multi-column sort is complex *(Low)*

The `sort_by_columns` method on line 46 of `dialogs.py` has nested sorting logic that produces a stable multi-column sort. Test cases should verify ordering with 3+ rows and 2 sort columns.

### RC-5: `QueryBuilder._enrich_items` and `_build_field_metadata` need Tk *(Medium)*

These methods are on the `QueryBuilder(tk.Toplevel)` class. They require a real `tk.Tk()` parent. Test cases use a shared `tk_root` fixture that creates and destroys a root once per module.

### RC-6: Confirm `_patched_popen_init` only fires on win32 *(Low)*

`logging_config.py` has platform-specific logic. Tests should verify both the win32 path and the non-win32 early return using `mocker.patch("sys.platform", ...)`.

### RC-7: `fetch_url_content` cascade has 5 code paths *(Medium)*

The multi-step fetch cascade (CDP → bearer → Edge CDP → urllib fallback) creates many paths. Test cases collapse these into parameterized scenarios using mocks for each fetcher.

### RC-8: `_build_read_fetched_doc` path-traversal guard *(Low)*

The handler rejects filenames containing `/`, `\`, or `..`. A security-oriented test case is included to verify this.

---

## Risk Items Verified

| Risk from Design Doc | QA Assessment |
|----------------------|---------------|
| Tk availability in CI | Mitigated by skip-if-unavailable fixture. Acceptable. |
| Mocking drift | Mitigated by testing via public APIs. Acceptable. |
| Test speed | Shared root per module minimizes overhead. Acceptable. |
| Coverage < 70% despite effort | Test case counts are generous (114 tests). Low risk. |

---

## Acceptance Criteria Traceability

| AC | Test File(s) | # Test Cases |
|----|-------------|:------------:|
| `logging_config.py` ≥ 70% | `test_logging_config.py` | 8 |
| `kpi_analyzer.py` ≥ 70% | `test_kpi_analyzer_extended.py` | 14 |
| `query_builder.py` ≥ 70% | `test_query_builder_extended.py` | 16 |
| `copilot_tools.py` ≥ 70% | `test_copilot_tools.py` | 20 |
| `copilot_panel.py` ≥ 70% | `test_copilot_panel.py` | 16 |
| `dialogs.py` ≥ 70% | `test_dialogs_extended.py` | 22 |
| `app.py` ≥ 70% | `test_app_coverage.py` | 25 |

**Total: 121 test cases** across 7 new test files.

---

## NFR Verification Plan

| NFR | How to verify |
|-----|---------------|
| No single test > 2 s | `pytest --durations=0` — flag any test > 2 s |
| Total suite < 120 s | `time pytest` — total wall-clock under 120 s |
| No production code changes | `git diff --name-only` shows only test files |
| Isolation (no real Tk, API, filesystem) | Review mocks in code review; CI has no display |
| Determinism | `pytest --count=3 -x` (repeat 3x, fail on first flake) |
---

## Architect Notes

### AN-1: `conftest.py` — shared fixtures blueprint (Decision)

No `conftest.py` currently exists in `SFIReporter/tests/`. The architect mandates **creating one** (`SFIReporter/tests/conftest.py`) with three shared fixtures. Per-file fixtures should supplement, not replace, these.

```
SFIReporter/tests/conftest.py
├── sys.modules["copilot"] injection  (module-level, runs on import)
├── @pytest.fixture(scope="module") tk_root
│      Creates tk.Tk(), withdraw(), yields, destroy()
├── @pytest.fixture mock_app(tk_root)
│      Returns MagicMock with .root = tk_root, .current_data = {}, etc.
└── @pytest.fixture auto_reset_logging
       Clears sfi_reporter logger handlers before each test
       (needed by test_logging_config.py to verify idempotency)
```

**Rationale**: Centralising the copilot mock and tk_root prevents every test file from duplicating the boilerplate. The `scope="module"` for `tk_root` means one Tk root per test module (not per test function) — this keeps GUI tests fast while ensuring `root.destroy()` at module teardown avoids stale windows.

### AN-2: Copilot SDK import-time side effect mitigation (Decision)

`copilot_tools.py` line 13 and `copilot_panel.py` lines ~50-60 import directly from the `copilot` package at module level. If these imports execute before the mock is installed, they raise `ModuleNotFoundError`.

**Prescribed pattern** (must appear in `conftest.py` *before* any test imports):

```python
import sys
from unittest.mock import MagicMock

_mock_copilot = MagicMock()
_mock_copilot.Tool = type("Tool", (), {})
_mock_copilot.ToolResult = type("ToolResult", (), {"__init__": lambda self, **kw: None})
_mock_copilot.define_tool = MagicMock()
sys.modules.setdefault("copilot", _mock_copilot)
```

Key detail: use **`setdefault`** so that if a real `copilot` package is installed (e.g. developer's local env), the mock doesn't clobber it. If the real package *is* present, the developer should instead use `sys.modules["copilot"] = _mock_copilot` (force override) to keep tests deterministic. The developer must choose one strategy and document it in conftest.

### AN-3: `app.py` constructor side effects — required patches (Decision)

`SFIReporterApp.__init__` calls:
1. `get_current_user_alias()` — reads OS env / Azure CLI
2. `_build_ui()` — creates Tkinter widgets and calls `_load_setting()`
3. `_load_cached_data()` — reads disk cache

All three must be patched **before** constructing the instance in tests. The developer should use a factory fixture:

```python
@pytest.fixture
def make_app(tk_root, mocker):
    """Factory that returns a fully-patched SFIReporterApp."""
    mocker.patch("sfi_reporter.app.get_current_user_alias", return_value="testuser")
    mocker.patch("sfi_reporter.app.is_cache_valid", return_value=False)
    mocker.patch("sfi_reporter.app.read_cache", return_value={})
    mocker.patch("sfi_reporter.app._load_setting", return_value=None)
    mocker.patch("sfi_reporter.app._save_setting")
    mocker.patch("sfi_reporter.app.setup_logging")
    mocker.patch("sfi_reporter.app.patch_subprocess_windows")

    def _factory(**overrides):
        from sfi_reporter.app import SFIReporterApp
        return SFIReporterApp(tk_root)
    return _factory
```

This fixture goes in `test_app_coverage.py` (local), not conftest, because it's specific to app tests.

### AN-4: Tk root lifecycle — `scope="module"` not `scope="session"` (Decision)

**Rejected**: `scope="session"` (single Tk root for all tests). Reason: Tkinter only allows **one `Tk()` instance per interpreter**. If a test creates a second root, Tk raises `TclError`. With `scope="module"`, each module gets its own root created/destroyed in sequence (pytest runs modules sequentially by default). This avoids cross-module leakage.

**Constraint for developer**: Never call `tk.Tk()` directly inside a test. Always use the `tk_root` fixture. If any GUI test needs a `Toplevel`, create it as `tk.Toplevel(tk_root)`.

### AN-5: `dialogs.py` and `app.py` coverage gap — expansion strategy (Advisory)

QA estimates (RC comments) show `dialogs.py` and `app.py` may land around 38% with the listed test cases. The developer **must** add tests beyond those in the test-case doc to hit 70%. Priority expansion targets:

| File | Method cluster | Est. stmts gained |
|------|---------------|:-----------------:|
| `dialogs.py` | `_build_tree`, `_on_item_right_click`, `BulkEtaProgressDialog._start`, `ManualEtaReviewDialog._accept`/`_show_summary` | ~150 |
| `app.py` | Full `_build_ui` widget assertions, `_refresh_tables_after_eta_update`, `_on_alias_change` debounce, double-click edge cases | ~170 |

The developer should run `pytest --cov=sfi_reporter --cov-report=term-missing` after each phase and add targeted tests for the highest-frequency uncovered lines.

### AN-6: `pytest-cov` not in dev dependencies (Blocker)

`pyproject.toml` lists `pytest` and `pytest-mock` in `[project.optional-dependencies].dev` but **not** `pytest-cov`. The developer must add `"pytest-cov>=4.0.0"` to the dev extras before running coverage. This is the only change to a non-test file and is infrastructure-only (no production code).

### AN-7: Test isolation — no real I/O contract (Constraint)

Every test must satisfy these isolation rules:
1. **No network calls**: All `urllib`, `requests`, Graph API, S360 API calls mocked.
2. **No filesystem writes outside `tmp_path`**: Use `tmp_path` for cache/log tests.
3. **No real Tk windows**: `root.withdraw()` in fixture; no `mainloop()` calls in tests.
4. **No `time.sleep`**: Use `mocker.patch("time.sleep")` if needed.
5. **No os.environ mutations**: Use `monkeypatch.setenv` / `monkeypatch.delenv`.

### AN-8: File naming and location (Constraint)

All 7 new test files go in `SFIReporter/tests/`:

| New file | Tests for |
|----------|-----------|
| `test_logging_config.py` | `logging_config.py` |
| `test_kpi_analyzer_extended.py` | `kpi_analyzer.py` (extends existing coverage) |
| `test_query_builder_extended.py` | `query_builder.py` (extends existing `test_query_builder.py`) |
| `test_copilot_tools.py` | `copilot_tools.py` |
| `test_copilot_panel.py` | `copilot_panel.py` |
| `test_dialogs_extended.py` | `dialogs.py` (extends existing `test_detail_modal_colors.py`) |
| `test_app_coverage.py` | `app.py` |

Plus one new/modified infrastructure file:
| File | Purpose |
|------|---------|
| `SFIReporter/tests/conftest.py` | Shared fixtures (new file) |

### AN-9: Execution order validation (Advisory)

The developer should implement in this order and validate coverage after each phase:

1. **Phase 0**: Create `conftest.py`, add `pytest-cov` to `pyproject.toml`.
2. **Phase 1**: `test_logging_config.py`, `test_kpi_analyzer_extended.py` — validate both ≥ 70%.
3. **Phase 2**: `test_copilot_tools.py`, `test_query_builder_extended.py` — validate both ≥ 70%.
4. **Phase 3**: `test_copilot_panel.py`, `test_dialogs_extended.py`, `test_app_coverage.py` — validate all ≥ 70%.
5. **Phase 4**: Run full suite, fix any cross-test interference (e.g. Tk root conflicts, copilot mock state leakage).

### AN-10: No production code changes (Hard constraint)

Zero changes to files under `SFIReporter/src/sfi_reporter/`. The only non-test change permitted is adding `pytest-cov` to `pyproject.toml` dev dependencies (AN-6).