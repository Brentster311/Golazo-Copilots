# SFI Reporter — Build Manifest

## Build Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Executable | `dist/SFIReporter.exe` | Standalone Windows exe (PyInstaller --onefile) |
| Distributable | `dist/SFIReporter.zip` | Zip for sharing (contains exe + README) |

### Zip Contents

| File | Source | Purpose |
|------|--------|----------|
| `SFIReporter.exe` | `dist/SFIReporter.exe` | The app |
| `README.md` | `SFIReporter/README.md` | Usage docs |

> **`dist/` is gitignored.** Artifacts must be rebuilt locally after pulling.

## Build Steps

Run from `SFIReporter/`:

```powershell
# 1. Run tests
python -m pytest tests/ -v

# 2. Build the exe
python -m PyInstaller --onefile --name SFIReporter --hidden-import sfi_reporter.query_builder --hidden-import sfi_reporter.eta_logic src/sfi_reporter/tk_app.py

# 3. Update the zip (MUST follow every exe rebuild)
Compress-Archive -Path dist/SFIReporter.exe, README.md -DestinationPath dist/SFIReporter.zip -Force
```

### One-liner

```powershell
python -m pytest tests/ -v; if ($LASTEXITCODE -eq 0) { python -m PyInstaller --onefile --name SFIReporter --hidden-import sfi_reporter.query_builder --hidden-import sfi_reporter.eta_logic src/sfi_reporter/tk_app.py; Compress-Archive -Path dist/SFIReporter.exe, README.md -DestinationPath dist/SFIReporter.zip -Force }
```

## Hidden Imports

PyInstaller cannot auto-discover these — they must be passed explicitly:

| Module | Reason |
|--------|--------|
| `sfi_reporter.query_builder` | Lazy-imported from `tk_app.py` via `from sfi_reporter.query_builder import QueryBuilder` inside `_on_query()` |
| `sfi_reporter.eta_logic` | Lazy-imported from `tk_app.py` ETA dialog classes inside `_on_save()`, `_show_current()`, `_run_bulk()`, `_on_update_etas()` |

## Prerequisites

- Python 3.10+
- `pip install -e ".[dev]"` (includes PyInstaller, pytest)
- Azure CLI (`az login`) optional — app falls back to browser login if unavailable
