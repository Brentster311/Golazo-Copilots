# S360Reporter — Build Manifest

## Build Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| Executable | `dist/S360Reporter.exe` | Standalone Windows exe (PyInstaller --onefile) |
| Distributable | `dist/S360Reporter.zip` | Zip for sharing (contains exe + README) |

### Zip Contents

| File | Source | Purpose |
|------|--------|----------|
| `S360Reporter.exe` | `dist/S360Reporter.exe` | The app |
| `README.md` | `GUI/README.md` | Usage docs |

> **`dist/` is gitignored.** Artifacts must be rebuilt locally after pulling.

## Build Steps

### Preferred (from repo root)

```powershell
./build.ps1
```

Optional flags:
- `./build.ps1 -SkipTests` (faster local packaging)
- `./build.ps1 -NoClean` (reuse PyInstaller cache)

Run from `GUI/`:

```powershell
# 1. Run tests
python -m pytest tests/ -v

# 2. Build the exe
python -m PyInstaller --onefile --name S360Reporter --hidden-import s360_reporter.query_builder --hidden-import s360_reporter.eta_logic --hidden-import llm_extender --hidden-import llm_extender.exceptions --hidden-import llm_extender.url_fetcher --hidden-import llm_extender.client --hidden-import llm_extender.config --hidden-import llm_extender.auth --hidden-import llm_extender.providers --hidden-import accia_s360 --hidden-import accia_s360.client --hidden-import accia_s360.models --hidden-import accia_s360.auth --hidden-import accia_s360.cache --hidden-import accia_s360.config --hidden-import accia_s360.exceptions --paths ..\..\LLMExtender --paths ..\accia-s360\src src/s360_reporter/S360Reporter.py

# 3. Update the zip (MUST follow every exe rebuild)
Compress-Archive -Path dist/S360Reporter.exe, README.md -DestinationPath dist/S360Reporter.zip -Force
```

### One-liner

```powershell
python -m pytest tests/ -v; if ($LASTEXITCODE -eq 0) { python -m PyInstaller --onefile --name S360Reporter --hidden-import s360_reporter.query_builder --hidden-import s360_reporter.eta_logic --hidden-import llm_extender --hidden-import llm_extender.exceptions --hidden-import llm_extender.url_fetcher --hidden-import llm_extender.client --hidden-import llm_extender.config --hidden-import llm_extender.auth --hidden-import llm_extender.providers --hidden-import accia_s360 --hidden-import accia_s360.client --hidden-import accia_s360.models --hidden-import accia_s360.auth --hidden-import accia_s360.cache --hidden-import accia_s360.config --hidden-import accia_s360.exceptions --paths ..\..\LLMExtender --paths ..\accia-s360\src src/s360_reporter/S360Reporter.py; Compress-Archive -Path dist/S360Reporter.exe, README.md -DestinationPath dist/S360Reporter.zip -Force }
```

## Hidden Imports

PyInstaller cannot auto-discover these — they must be passed explicitly:

| Module | Reason |
|--------|--------|
| `s360_reporter.query_builder` | Lazy-imported from `S360Reporter.py` via `from s360_reporter.query_builder import QueryBuilder` inside `_on_query()` |
| `s360_reporter.eta_logic` | Lazy-imported from dialog classes inside `_on_save()`, `_show_current()`, `_run_bulk()`, `_on_update_etas()` |
| `llm_extender` | Editable install from `../../LLMExtender` — PyInstaller needs `--paths` to locate it |
| `llm_extender.exceptions` | Imported by `llm_client.py` |
| `llm_extender.url_fetcher` | Imported by `llm_client.py` |
| `llm_extender.client` | Core LLM client module |
| `llm_extender.config` | LLM configuration module |
| `llm_extender.auth` | Auth sub-package |
| `llm_extender.providers` | Provider sub-package |
| `accia_s360` | S360 client package — editable install from `../accia-s360/src` |
| `accia_s360.client` | Core S360 API client |
| `accia_s360.models` | Typed models (EtaUpdate, SaveResult, etc.) |
| `accia_s360.auth` | Azure credential management |
| `accia_s360.cache` | Local JSON caching |
| `accia_s360.config` | Configuration module |
| `accia_s360.exceptions` | Exception hierarchy |

## Prerequisites

- Python 3.10+
- `pip install -e ".[dev]"` (includes PyInstaller, pytest)
- `pip install -e ../../LLMExtender` (llm-extender dependency)
- `pip install -e ../accia-s360 --no-deps` (accia-s360 dependency)
- Azure CLI (`az login`) optional — app falls back to browser login if unavailable

## Last Build

- Timestamp: `2026-02-26 11:40:46 -08:00`
- Zip command: `Compress-Archive -Path "dist/S360Reporter.exe", "README.md" -DestinationPath "dist/S360Reporter.zip" -Force`
- `dist/S360Reporter.exe`: `13631713` bytes
- `dist/S360Reporter.zip`: `13391395` bytes
