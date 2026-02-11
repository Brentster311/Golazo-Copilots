# SFI-028 Builder Notes

## Branch
- Feature branch `SFI-028` created from `LLM-0012`
- Commit: `d1063fe` — "SFI-028: Replace S360 search chain-walking with MS Graph get_manager_chain() in SFIReporter"

## Build Verification
- **PyInstaller**: `pyinstaller SFIReporter.spec --noconfirm` — **SUCCESS**
  - Output: `dist/SFIReporter.exe`
  - Build log: "Building EXE from EXE-00.toc completed successfully."

## Test Results
- **SFI-026 + SFI-028 unit tests**: 42/42 pass
- **Full regression**: 276/276 non-live, non-infra tests pass
- **Pre-existing failures**: 6 failed (1 tkinter TCL, 5 live), 19 errors (pytest-mock missing)

## Files Committed (15 files, +832/-90)
- `SFIReporter/src/sfi_reporter/tk_app.py` (modified)
- `SFIReporter/tests/test_sfi_026.py` (modified)
- `SFIReporter/tests/test_sfi_028.py` (new)
- `WorkItems/SFI-028/` (12 files: user story, design docs, role notes, state)

## Push Status
- Not pushed — awaiting user confirmation for `git push -u origin SFI-028`
