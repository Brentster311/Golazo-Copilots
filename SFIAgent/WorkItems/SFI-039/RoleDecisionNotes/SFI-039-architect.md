# SFI-039 — Architect Role Decision Notes

**Role**: Architect
**Work Item**: SFI-039 — Achieve 70% Code Coverage on All Source Files
**Date**: 2026-02-25

---

## Decisions Made

### D-1: Create `SFIReporter/tests/conftest.py` with shared fixtures

**Decision**: Create a new `conftest.py` with three shared fixtures: `tk_root` (module-scoped), `mock_app`, and `auto_reset_logging`. The copilot SDK mock injection happens at module level in conftest.

**Rationale**: No conftest.py exists today. Seven new test files share common needs (Tk root, copilot mock, app mock). Centralising avoids ~100 lines of duplicated boilerplate and ensures the copilot `sys.modules` injection runs before any test file imports `copilot_tools` or `copilot_panel`.

**Alternatives rejected**:
- Per-file fixture duplication: higher maintenance, risk of inconsistency.
- `scope="session"` for tk_root: Tkinter forbids multiple `Tk()` instances; module scope is the safe maximum.

---

### D-2: Copilot SDK mock via `sys.modules.setdefault` in conftest

**Decision**: Inject a `MagicMock` for the `copilot` package into `sys.modules` at conftest import time, using `setdefault` to avoid clobbering if the real package is installed.

**Rationale**: `copilot_tools.py` (line 13) and `copilot_panel.py` both import `from copilot import ...` at module level. Without this injection, any test importing these modules crashes with `ModuleNotFoundError`.

**Risk**: If the real `copilot` package is installed, `setdefault` is a no-op and tests would use the real SDK. Developer must verify locally and switch to force-override if needed.

---

### D-3: `app.py` factory fixture pattern

**Decision**: Use a local `make_app` factory fixture (inside `test_app_coverage.py`) that patches all side-effecting dependencies before constructing `SFIReporterApp`.

**Rationale**: `SFIReporterApp.__init__` calls `get_current_user_alias()`, `_build_ui()` (which calls `_load_setting()`), and `_load_cached_data()`. All three execute real I/O. A factory fixture lets tests override specific patches per scenario while keeping the core set applied.

**Patches required for construction**:
- `sfi_reporter.app.get_current_user_alias` → `"testuser"`
- `sfi_reporter.app.is_cache_valid` → `False`
- `sfi_reporter.app.read_cache` → `{}`
- `sfi_reporter.app._load_setting` → `None`
- `sfi_reporter.app._save_setting` → no-op
- `sfi_reporter.app.setup_logging` → no-op
- `sfi_reporter.app.patch_subprocess_windows` → no-op

---

### D-4: Tk root scope is `module`, not `session` or `function`

**Decision**: `scope="module"` for the `tk_root` fixture.

**Rationale**:
- `scope="function"`: Too slow — Tk root creation/destruction per test adds ~50ms overhead × 100+ GUI tests.
- `scope="session"`: Risky — Tkinter's single-root constraint means a stale root from an early module can corrupt later modules.
- `scope="module"`: One root per test module, created fresh, destroyed at module end. Balances speed and isolation.

---

### D-5: Add `pytest-cov` to dev dependencies

**Decision**: Add `"pytest-cov>=4.0.0"` to `[project.optional-dependencies].dev` in `SFIReporter/pyproject.toml`.

**Rationale**: The work item's primary acceptance criteria require `pytest --cov` measurement. `pytest-cov` is not currently listed. This is the only permitted non-test file change.

---

### D-6: New test files only — no modification of existing tests

**Decision**: All new coverage goes in 7 new test files. Existing files (`test_query_builder.py`, `test_tk_app.py`, `test_detail_modal_colors.py`, etc.) are not modified.

**Rationale**: Avoids merge conflicts, keeps existing test stability intact, and makes the diff cleanly reviewable (all additions, no modifications to production or existing test code).

---

### D-7: Developer must expand `dialogs.py` and `app.py` tests beyond QA spec

**Decision**: The QA test-case document provides 24 tests for `dialogs.py` (790 stmts) and 32 for `app.py` (681 stmts). Coverage estimates show these may only reach ~38% with the listed cases. The developer must add additional tests iteratively using `--cov-report=term-missing` to identify and cover remaining lines until ≥70% is reached.

**Rationale**: It's impractical to enumerate every test case upfront for 1,262 + 1,068 lines of GUI code. The QA doc provides the framework; the developer fills gaps using coverage reports.

---

## Assumptions

| # | Assumption | Impact if wrong |
|---|-----------|-----------------|
| A-1 | Tkinter is available in the developer's Python environment (standard CPython). | GUI tests would skip; non-GUI tests unaffected. |
| A-2 | No CI pipeline currently enforces coverage gates. | Coverage is verified manually during build role. |
| A-3 | The `copilot` package is NOT installed in the test environment. | If installed, `sys.modules.setdefault` won't inject the mock — developer must switch to force override. |
| A-4 | `SFIReporter/tests/__init__.py` (currently just a comment) does not need modification. | conftest.py at the same level handles fixture sharing. |
| A-5 | All existing tests continue to pass after adding conftest.py. | If any existing test already imports `copilot` differently, there could be interference. Developer runs full suite in Phase 4 to catch this. |

---

## Risks Identified

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|-----------|
| conftest copilot mock interferes with existing tests | Low | Medium | Run full suite after Phase 0; revert to per-file mock if any failures. |
| `dialogs.py`/`app.py` can't reach 70% without production changes | Low | High | Developer adds more tests iteratively; accepts ≥65% with documented justification only as last resort. |
| Tk root `scope="module"` leaks state between tests within a module | Medium | Low | Call `root.withdraw()` in fixture; destroy all Toplevels in test teardown. |
| `pytest-cov` version conflict with existing dependencies | Low | Low | Pin `>=4.0.0` (wide range); developer resolves any pin conflict during install. |

---

## Artifacts Created

| Artifact | Path |
|----------|------|
| Architect notes (appended) | `WorkItems/SFI-039/Design/SFI-039-Review-Comments.md` |
| Architect role notes | `WorkItems/SFI-039/RoleDecisionNotes/SFI-039-architect.md` |
