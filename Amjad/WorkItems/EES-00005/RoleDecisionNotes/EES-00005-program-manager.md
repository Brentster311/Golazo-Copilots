# EES-00005 — Program Manager Decision Notes

## Key Decisions

### GUI Framework: Tkinter
- Zero dependencies (ships with Python)
- Adequate for forms, tables, tree views, file dialogs
- `ttk` themed widgets provide Windows-native look
- Consistent with project's minimal-dependency philosophy
- Rejected PyQt6 (too heavy, licensing), CustomTkinter (extra dep), web app (out of scope)

### Architecture: Multi-panel Tabbed Layout
- Single window with `ttk.Notebook` tabs: Process Incident, Knowledge Base, Evaluate
- Each tab maps to functional requirements (FR-1/2/3/4/5 → Process, FR-6 → KB, FR-7 → Evaluate)
- New `src/ees/gui/` package — additive, no changes to existing engine modules

### Threading Strategy
- LLM calls in `threading.Thread` with `root.after()` for UI updates
- Keeps UI responsive during API calls
- Worker threads never touch widgets directly

### Test Strategy
- Focus automated tests on non-UI logic (data transformations, worker results)
- GUI interaction tested manually
- No new external test dependencies needed

## Scope Notes
- FR-8 (data directory selection) kept simple — config dialog or command-line argument
- No web deployment, no multi-user features per user story scope
