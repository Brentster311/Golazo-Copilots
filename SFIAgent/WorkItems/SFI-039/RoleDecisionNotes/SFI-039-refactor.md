# SFI-039 Refactor Expert Notes

**Date:** 2026-02-25
**Work Item:** SFI-039 — Achieve ≥70% test coverage on all SFIReporter source files
**Scope:** Test files only (no production code was changed)

---

## Modularity Audit

### Line Counts & Test Functions

| File | Lines | Tests | Status |
|------|------:|------:|--------|
| `test_sfi_039_logging.py` | 156 | 12 | ✅ Under 300 |
| `test_sfi_039_kpi_analyzer.py` | 935 | 87 | ⚠️ Over 300 |
| `test_sfi_039_copilot_tools.py` | 497 | 53 | ⚠️ Over 300 |
| `test_sfi_039_query_builder.py` | 587 | 82 | ⚠️ Over 300 |
| `test_sfi_039_copilot_panel.py` | 773 | 95 | ⚠️ Over 300 |
| `test_sfi_039_dialogs.py` | 1,098 | 121 | ⚠️ Over 300 |
| `test_sfi_039_app.py` | 1,323 | 128 | ⚠️ Over 300 |
| **Total** | **5,369** | **578** | |

### Single-Responsibility Check

Each test file targets exactly one production module:

| Test File | Production Module | Verdict |
|-----------|-------------------|---------|
| `test_sfi_039_logging.py` | `logging_config.py` | ✅ Single responsibility |
| `test_sfi_039_kpi_analyzer.py` | `kpi_analyzer.py` | ✅ Single responsibility |
| `test_sfi_039_copilot_tools.py` | `copilot_tools.py` | ✅ Single responsibility |
| `test_sfi_039_query_builder.py` | `query_builder.py` | ✅ Single responsibility |
| `test_sfi_039_copilot_panel.py` | `copilot_panel.py` | ✅ Single responsibility |
| `test_sfi_039_dialogs.py` | `dialogs.py` | ✅ Single responsibility |
| `test_sfi_039_app.py` | `app.py` | ✅ Single responsibility |

### Large File Justification

Six of seven files exceed 300 lines. **No splitting is recommended.** Rationale:

1. **1:1 module mapping** — Each test file corresponds to exactly one source module. Splitting a test file would create artificial boundaries that reduce discoverability (e.g., "where are the tests for `app._on_service_double_click`?").
2. **Cohesive test classes** — Tests are already organized into classes by feature area within each file (e.g., `TestTreeUpdates`, `TestExport`, `TestEtaActions`). This provides the logical grouping that splitting into files would attempt to achieve.
3. **Shared fixtures** — Each file defines module-specific fixtures and sample data at the top. Splitting would require duplicating or extracting these into conftest modules, adding complexity for no functional gain.
4. **Convention consistency** — The existing SFIReporter test suite follows the `test_sfi_NNN_<module>.py` naming convention. Maintaining one file per module keeps the pattern predictable.
5. **Test file size norms** — Large test files are standard in Python projects where comprehensive coverage of a complex module is the goal. The 300-line guideline is a production code heuristic; test files routinely and acceptably exceed it.

---

## Lint Audit (ruff)

### Before Fixes
- **31 violations found** across 7 files
  - **24 F401** (unused imports) — auto-fixed by `ruff --fix`
  - **7 F841** (unused local variables from mock assignments) — manually fixed

### F841 Fixes Applied

| File | Line | Variable | Fix |
|------|-----:|----------|-----|
| `test_sfi_039_app.py` | 646 | `mock_collect` | Removed assignment; `mocker.patch()` call retained |
| `test_sfi_039_app.py` | 698 | `mock_filter` | Removed assignment; `mocker.patch()` call retained |
| `test_sfi_039_app.py` | 831 | `mock_get` | Removed assignment; `mocker.patch()` call retained |
| `test_sfi_039_copilot_panel.py` | 744 | `mock_rc` | Removed `as mock_rc` from context manager |
| `test_sfi_039_copilot_panel.py` | 786 | `mock_after` | Removed `as mock_after` from context manager |
| `test_sfi_039_copilot_panel.py` | 852 | `mock_set` | Removed `as mock_set` from context manager |
| `test_sfi_039_dialogs.py` | 522 | `initial_counter` | Removed unused assignment |

### After Fixes
- **0 violations** — all checks passed
- **578 tests pass** (unchanged from pre-fix)

---

## Refactoring Actions Taken

1. **Removed 24 unused imports** via `ruff --fix` (F401)
2. **Removed 7 unused variable assignments** manually (F841)
3. **No test logic changed** — all fixes were cosmetic (import/variable cleanup)
4. **No production code touched** — scope limited to test files per work item

## Refactoring Actions NOT Taken (with justification)

1. **Did not split large test files** — Each file has single responsibility (1:1 with source module), uses cohesive test classes, and follows project conventions. Splitting would reduce clarity.
2. **Did not extract shared test fixtures** — Fixtures are module-specific and not shared across files. Extraction would add indirection without benefit.
3. **Did not refactor production code** — Out of scope for SFI-039 (test-only work item).
