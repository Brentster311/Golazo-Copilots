# SFI-018 — Builder Notes

## Branch
- Branch: `SFI-018` (created from `SFI-015`)

## Build Verification

| Step | Command | Result |
|------|---------|--------|
| Tests (accia-s360) | `python -m pytest tests/test_auth_chain.py -v` | ✅ 10 passed |
| Tests (SFIReporter) | `python -m pytest tests/ -v` | ✅ 133 passed |
| PyInstaller build | `python -m PyInstaller --onefile --name SFIReporter --hidden-import sfi_reporter.query_builder src/sfi_reporter/tk_app.py` | ✅ Build successful |
| Zip | `Compress-Archive -Path dist\SFIReporter.exe, README.md -DestinationPath dist\SFIReporter.zip -Force` | ✅ Updated |
| App launch | `dist\SFIReporter.exe` | ✅ Launched successfully |

## Commit
- Hash: `872a38d`
- Message: `SFI-018: In-app Azure login with browser fallback`
- Files: 13 changed, 689 insertions, 43 deletions

## Files Changed

| File | Change |
|------|--------|
| `accia-s360/src/accia_s360/auth.py` | Credential chain implementation |
| `accia-s360/tests/test_auth_chain.py` | 10 new tests |
| `SFIReporter/LAUNCHME.ps1` | Deleted |
| `SFIReporter/BUILD_MANIFEST.md` | Removed LAUNCHME.ps1 references |
| `SFIReporter/README.md` | Updated features + requirements |
| `WorkItems/SFI-018/*` | Design docs + role notes (9 files) |
