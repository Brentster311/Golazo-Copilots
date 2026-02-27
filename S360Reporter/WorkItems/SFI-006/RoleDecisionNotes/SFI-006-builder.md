# SFI-006 Builder Notes

## Build Verification

- **Date**: 2026-02-06
- **Build command**: `python -m pytest GUI/tests/ --rootdir=GUI -v --tb=short`
- **Result**: 84 tests passed, 1 warning
- **PyInstaller build**: `pyinstaller --onefile --name S360Reporter src/sfi_reporter/tk_app.py` — 18.7 MB exe built successfully
- **Commit**: `7264321` — "Add file logging, suppress subprocess windows, add LAUNCHME.ps1 launcher"

## Verification

- Double-click drill-down modals functional in tkinter app
- Detail modal opens for Services, Programs, and Action Items tables
- Modal closes via Close button and Escape key
- All tests in test_tk_app.py pass

## Environment

- Python 3.14.3
- Windows 11 (10.0.26200)
- PyInstaller 6.18.0
