# SFI-036 — Test Cases

## Test Strategy

This is a pure refactoring — no new behavior is introduced. The test strategy is:

1. **All existing tests must pass** after retargeting imports (this is the primary validation)
2. **Import smoke test** — verify `from sfi_reporter.app import main` works
3. **App launch test** — verify `python -m sfi_reporter.app` starts without error
4. **No `tk_app` references remain** — grep the codebase to confirm zero remaining imports

## Test Cases

### TC-1: All existing tests pass
- **Maps to AC**: "All existing tests must pass after the import retargeting"
- **Steps**: Run `pytest SFIReporter/tests/ -v`
- **Expected**: 100% pass rate, zero failures
- **Failure message**: "Existing test {name} failed — likely a broken import retarget"

### TC-2: Import smoke test
- **Maps to AC**: "`python -m sfi_reporter.app` launches the application successfully"
- **Steps**: `python -c "from sfi_reporter.app import main; print('OK')"`
- **Expected**: Prints "OK" with no ImportError
- **Failure message**: "Cannot import main from sfi_reporter.app"

### TC-3: No tk_app references in production code
- **Maps to AC**: "`tk_app.py` is deleted"
- **Steps**: Grep for `sfi_reporter.tk_app` in `SFIReporter/src/`
- **Expected**: Zero matches
- **Failure message**: "Production code still references tk_app"

### TC-4: No tk_app references in test code
- **Maps to AC**: "All test file imports are retargeted"
- **Steps**: Grep for `sfi_reporter.tk_app` in `SFIReporter/tests/`
- **Expected**: Zero matches
- **Failure message**: "Test code still references tk_app"

### TC-5: Entry point updated
- **Maps to AC**: "pyproject.toml entry point is updated"
- **Steps**: Read `pyproject.toml`, check `[project.scripts]`
- **Expected**: Contains `sfi_reporter.app:main`, not `sfi_reporter.tk_app:main`
- **Failure message**: "pyproject.toml still points to tk_app"

### TC-6: Spec files updated
- **Maps to AC**: "Both .spec files reference app.py"
- **Steps**: Read both `.spec` files
- **Expected**: Reference `app.py`, not `tk_app.py`
- **Failure message**: ".spec file still references tk_app.py"

### TC-7: tk_app.py does not exist
- **Maps to AC**: "`tk_app.py` is deleted"
- **Steps**: Check file system
- **Expected**: `SFIReporter/src/sfi_reporter/tk_app.py` does not exist
- **Failure message**: "tk_app.py still exists"
