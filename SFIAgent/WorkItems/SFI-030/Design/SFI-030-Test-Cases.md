# Test Cases — SFI-030

## TC-01: All existing tests pass unchanged

**Verify**: Run `pytest SFIReporter/tests/ -m "not live" --tb=short -q`
**Expected**: Same pass count as before refactor (241 passed), no new failures.

## TC-02: Re-exports work

**Verify**: `from sfi_reporter.tk_app import OrgAncestry, aggregate_by_owner, do_refresh, SFIReporterApp, DetailModal, SortableTreeview`
**Expected**: All imports succeed.

## TC-03: No circular imports

**Verify**: `python -c "import sfi_reporter.models; import sfi_reporter.formatters; import sfi_reporter.services; import sfi_reporter.dialogs; import sfi_reporter.app"`
**Expected**: No `ImportError` or `AttributeError`.

## TC-04: PyInstaller build succeeds

**Verify**: `pyinstaller --clean SFIReporter.spec`
**Expected**: `SFIReporter.exe` produced without errors.

## TC-05: tk_app.py is under 100 lines

**Verify**: `wc -l SFIReporter/src/sfi_reporter/tk_app.py`
**Expected**: < 100 lines.

## TC-06: Each module defines `__all__`

**Verify**: Grep for `__all__` in each new module.
**Expected**: All 5 new modules define `__all__`.
