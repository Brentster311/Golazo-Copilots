# SFI-039 — Project Owner Assistant Notes

## Decision Log
- **Scope**: Test-only changes — write new tests to cover uncovered source lines. No production code changes.
- **7 files below 70%**: app.py (0%), copilot_panel.py (34%), copilot_tools.py (0%), dialogs.py (14%), kpi_analyzer.py (59%), logging_config.py (0%), query_builder.py (40%)
- **8 files already above 70%**: __init__.py (100%), cache.py (81%), data.py (78%), eta_logic.py (93%), formatters.py (88%), kpi_lookup.py (93%), models.py (98%), services.py (87%)
- **Approach**: Heavy mocking of Tkinter (`Tk`, `Toplevel`, `Treeview`, etc.), Graph API client, and filesystem for GUI-heavy files
- **Must-Ask Checklist**: All items already known — this is a Tkinter desktop app on Windows for technical users with in-memory data

## Assumptions
- Coverage measured by pytest-cov statement coverage
- Tests use unittest.mock to avoid real GUI/API calls
- Existing passing tests remain unchanged
