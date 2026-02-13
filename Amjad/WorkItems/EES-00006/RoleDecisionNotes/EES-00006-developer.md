# Developer Decision Notes — EES-00006

## TDD Cycle

### RED
- 10 tests in `tests/test_settings.py`: 8 SettingsManager (load/save/effective/roundtrip), 2 FactExtractor kwargs
- Verified RED: `ModuleNotFoundError: No module named 'ees.gui.settings'`

### GREEN
- Created `src/ees/gui/settings.py` — `SettingsManager(data_dir)` with `load()`, `save()`, `get_effective()`
- Modified `src/ees/fact_extractor.py` — added `endpoint`, `deployment`, `api_version` kwargs (backward compatible)
- Modified `src/ees/gui/app.py` — integrated SettingsManager, added `SettingsDialog` class, File → Settings menu item
- All 217 tests pass

## Files Changed

| File | Action |
|------|--------|
| `src/ees/gui/settings.py` | Created — SettingsManager |
| `src/ees/fact_extractor.py` | Modified — additive kwargs |
| `src/ees/gui/app.py` | Modified — Settings dialog + integration |
| `tests/test_settings.py` | Created — 10 tests |
