# SFI-018 — Builder Notes

## Branch
- Branch: `SFI-018` (created from `SFI-015`)

## Build Verification

| Step | Command | Result |
|------|---------|--------|
| Tests (accia-s360) | `python -m pytest tests/test_auth_chain.py -v` | ✅ 10 passed |
| Tests (S360Reporter) | `python -m pytest tests/ -v` | ✅ 133 passed |
| PyInstaller build | `python -m PyInstaller --onefile --name S360Reporter --hidden-import sfi_reporter.query_builder src/sfi_reporter/tk_app.py` | ✅ Build successful |
| Zip | `Compress-Archive -Path dist\S360Reporter.exe, README.md -DestinationPath dist\S360Reporter.zip -Force` | ✅ Updated |
| App launch | `dist\S360Reporter.exe` | ✅ Launched successfully |

## Commit
- Hash: `872a38d`
- Message: `SFI-018: In-app Azure login with browser fallback`
- Files: 13 changed, 689 insertions, 43 deletions

## Files Changed

| File | Change |
|------|--------|
| `accia-s360/src/accia_s360/auth.py` | Credential chain implementation |
| `accia-s360/tests/test_auth_chain.py` | 10 new tests |
| `GUI/LAUNCHME.ps1` | Deleted |
| `BUILD_MANIFEST.md` | Removed LAUNCHME.ps1 references |
| `GUI/README.md` | Updated features + requirements |
| `WorkItems/SFI-018/*` | Design docs + role notes (9 files) |
