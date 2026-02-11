# SFI-028 Project Owner Assistant Notes

**Role**: Project Owner Assistant  
**Date**: 2025-07-20  

## Must-Ask Checklist
All answered from context — this is a modification to existing Tkinter desktop app:
- Interface type: Tkinter GUI (existing)
- Target platform: Windows (PyInstaller .exe)
- Data persistence: JSON file cache (existing)
- User type: Technical (Microsoft managers)

## Decisions
- Express profile chosen — this is a focused refactor of one function (`get_org_mapping`) to use a new API that already exists and is proven by POC.
- Existing SFI-026 tests must pass unmodified to prove backward compatibility.
- `get_service_owners()` stays on S360 search — only hierarchy resolution changes.
