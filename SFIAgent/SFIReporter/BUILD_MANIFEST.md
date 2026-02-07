# SFI Reporter — Build Manifest

## Build Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Executable | `dist/SFIReporter.exe` | Standalone Windows exe (PyInstaller --onefile) |
| Distributable | `dist/SFIReporter.zip` | Zip of the exe for sharing |

> **`dist/` is gitignored.** Artifacts must be rebuilt locally after pulling.

## Build Steps

Run from `SFIReporter/`:

```powershell
# 1. Run tests
python -m pytest tests/ -v

# 2. Build the exe
python -m PyInstaller --onefile --name SFIReporter --hidden-import sfi_reporter.query_builder src/sfi_reporter/tk_app.py

# 3. Update the zip (MUST follow every exe rebuild)
Compress-Archive -Path dist/SFIReporter.exe -DestinationPath dist/SFIReporter.zip -Force
```

### One-liner

```powershell
python -m pytest tests/ -v; if ($LASTEXITCODE -eq 0) { python -m PyInstaller --onefile --name SFIReporter --hidden-import sfi_reporter.query_builder src/sfi_reporter/tk_app.py; Compress-Archive -Path dist/SFIReporter.exe -DestinationPath dist/SFIReporter.zip -Force }
```

## Hidden Imports

PyInstaller cannot auto-discover these — they must be passed explicitly:

| Module | Reason |
|--------|--------|
| `sfi_reporter.query_builder` | Lazy-imported from `tk_app.py` via `from sfi_reporter.query_builder import QueryBuilder` inside `_on_query()` |

## Prerequisites

- Python 3.10+
- `pip install -e ".[dev]"` (includes PyInstaller, pytest)
- Azure CLI authenticated (`az login`) — needed for tests that hit live APIs
