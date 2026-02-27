# SFI-030 Developer Notes

## Implementation Summary

Refactored the monolithic `tk_app.py` (3,813 lines) into 6 focused modules:

| Module | Lines | Purpose |
|--------|-------|---------|
| `models.py` | ~230 | OrgAncestry, constants, column utilities |
| `formatters.py` | ~155 | Text formatting, URL extraction, field grouping |
| `services.py` | ~490 | Business logic, data refresh, org mapping, filters |
| `dialogs.py` | ~1,400 | All 12 Tkinter dialog/widget classes + LLM launcher |
| `app.py` | ~520 | SFIReporterApp main class + main() entry point |
| `tk_app.py` | ~25 | Backward-compatible re-export shim |

## Dependency Layering

```
models → formatters → services → dialogs → app → tk_app (shim)
```

## Backward Compatibility

- `tk_app.py` is now a re-export shim using `from X import *` from all 5 modules
- All 50+ `from sfi_reporter.tk_app import X` statements in tests and source continue to work
- PyInstaller spec updated with 5 new `hiddenimports`
- Original backed up as `tk_app_original.py`

## Test Patch Updates

Tests patching module-level names needed their targets updated:
- `test_sfi_025.py`: Changed `sfi_reporter.tk_app._load_setting` → `sfi_reporter.dialogs._load_setting` (for dialog tests) and `sfi_reporter.services._load_setting` (for `_load_llm_config` tests)
- `test_sfi_025.py`: Changed `sfi_reporter.tk_app._save_setting` → `sfi_reporter.dialogs._save_setting`
- `test_sfi_025.py`: Changed `sfi_reporter.tk_app.messagebox` → `sfi_reporter.dialogs.messagebox`

## Test Results

- **242 passed** (0 new failures introduced)
- **19 errors** (all pre-existing: missing `pytest-mock`, tcl teardown)
- **1 flaky** (tkinter teardown, passes in isolation)

## Files Changed

- **Created**: `models.py`, `formatters.py`, `services.py`, `dialogs.py`, `app.py`
- **Replaced**: `tk_app.py` (shim)
- **Updated**: `S360Reporter.spec` (hiddenimports), `test_sfi_025.py` (patch targets)
- **Backup**: `tk_app_original.py`
