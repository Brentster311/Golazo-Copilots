# SFI-017 — Builder Notes

## Build
- Branch `SFI-017` created from `SFI-016`
- PyInstaller build: `python -m PyInstaller --onefile --name S360Reporter --hidden-import sfi_reporter.query_builder src/sfi_reporter/tk_app.py`
- Exe: 20MB at `dist/S360Reporter.exe`
- All 171 tests pass
