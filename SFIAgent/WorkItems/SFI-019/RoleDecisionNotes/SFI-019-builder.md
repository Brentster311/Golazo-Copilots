# SFI-019 Builder Notes

## Branch
- Branch: `SFI-019` (created from `SFI-018`)
- Commit: `c45f07f` — "SFI-019: Set ETAs and Statuses (Bulk & Individual)"

## Files Committed (21 changed, 1771 insertions, 47 deletions)

### New Files (14)
| File | Description |
|------|-------------|
| `SFIReporter/src/sfi_reporter/eta_logic.py` | ETA proposal, validation, filtering, payload building |
| `SFIReporter/tests/test_eta_logic.py` | 5 tests for eta_logic functions |
| `SFIReporter/tests/test_eta_ui.py` | 9 tests for UI dialogs |
| `accia-s360/tests/test_eta_payload.py` | 3 tests for API payload format |
| `WorkItems/SFI-019/SFI-019-User-Story.md` | User story (status: IMPLEMENTED) |
| `WorkItems/SFI-019/Design/SFI-019-design-doc.md` | Design document |
| `WorkItems/SFI-019/Design/SFI-019-Review-Comments.md` | Review comments + architect notes |
| `WorkItems/SFI-019/Design/SFI-019-Test-Cases.md` | 15 test cases |
| `WorkItems/SFI-019/RoleDecisionNotes/SFI-019-*.md` | 7 role notes |

### Modified Files (7)
| File | Description |
|------|-------------|
| `SFIReporter/src/sfi_reporter/tk_app.py` | 4 dialog classes + button wiring + cache refresh |
| `accia-s360/src/accia_s360/models.py` | EtaUpdate payload format fix |
| `accia-s360/src/accia_s360/endpoints/action_items.py` | save_etas one-per-POST |
| `accia-s360/src/accia_s360/client.py` | save_eta assigned_to parameter |
| `SFIReporter/README.md` | Added Update ETAs feature |
| `SFIReporter/BUILD_MANIFEST.md` | Added eta_logic hidden import |

## Build Commands
```powershell
cd SFIReporter/
python -m pytest tests/ -v
python -m PyInstaller --onefile --name SFIReporter --hidden-import sfi_reporter.query_builder --hidden-import sfi_reporter.eta_logic src/sfi_reporter/tk_app.py
Compress-Archive -Path dist/SFIReporter.exe, README.md -DestinationPath dist/SFIReporter.zip -Force
```

## Test Results
- SFIReporter: 147 passed
- accia-s360: 29 passed
- Total: **176 tests all green**

## Build Result
- `dist/SFIReporter.exe` — 19.2 MB
- `dist/SFIReporter.zip` — distributable created
