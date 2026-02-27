# SFI-030 — Refactor tk_app.py into Focused Modules

**Status**: IN PROGRESS

## User Story

- **Title**: Split tk_app.py (3813 lines) into 6 focused modules
- **As a**: S360Reporter developer
- **I want**: tk_app.py decomposed into `models.py`, `services.py`, `formatters.py`, `dialogs.py`, `app.py`, and a thin `tk_app.py` re-export shim
- **So that**:
  - Each module has a single responsibility and is independently testable
  - Navigation and code review are tractable (no 3800-line files)
  - Import cycles are eliminated by layering: models → formatters → services → dialogs → app
  - Existing tests and PyInstaller build continue to work without modification

- **Out of scope**:
  - Bug fixes (no behavior changes — pure structural refactor)
  - New features or API changes
  - Changes to `data.py`, `cache.py`, or `accia-s360` library

- **Assumptions**:
  - **Assumption (explicit)**: Tkinter desktop GUI, Windows, same package structure `sfi_reporter/`
  - **Assumption (explicit)**: All existing imports of `from sfi_reporter.tk_app import X` continue to work via re-exports in `tk_app.py`
  - **Assumption (explicit)**: No public API changes — all function signatures remain identical
  - **Assumption (explicit)**: Test files are NOT moved, only import paths may be updated if needed

- **Acceptance Criteria**:
  - [ ] `tk_app.py` reduced to <100 lines (re-exports only)
  - [ ] All 6 new/modified modules exist in `sfi_reporter/` package
  - [ ] All existing tests pass without modification (or with import-only updates)
  - [ ] PyInstaller build succeeds and produces working `.exe`
  - [ ] No circular imports between new modules
  - [ ] `git diff --stat` shows net negative line change in `tk_app.py`

- **Non-functional requirements**: No runtime performance impact (pure file reorganization)
- **Telemetry / metrics expected**: None
- **Rollout / rollback notes**: Single commit, revertible
