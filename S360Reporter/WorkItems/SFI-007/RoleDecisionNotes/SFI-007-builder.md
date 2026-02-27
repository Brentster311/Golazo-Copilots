# SFI-007 Builder Notes

## Build Verification

- **Date**: 2026-02-06
- **Build command**: `python -m pytest GUI/tests/ --rootdir=GUI -v --tb=short`
- **Result**: 84 tests passed, 1 warning
- **PyInstaller build**: `pyinstaller --onefile --name S360Reporter src/sfi_reporter/tk_app.py` — 18.7 MB exe built successfully
- **Commit**: `7264321`

## Verification

- Item details modal opens on double-click from drill-down modal
- All non-empty fields displayed in label:value pairs
- Modal shows action item title, all 30+ cached fields
- Modal closeable via Close button and Escape key

## Environment

- Python 3.14.3
- Windows 11 (10.0.26200)
- PyInstaller 6.18.0
