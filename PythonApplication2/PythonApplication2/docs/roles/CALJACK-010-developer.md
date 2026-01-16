# Role Decision Document: Developer

**Work Item**: CALJACK-010 - Settings Menu with Language Selection  
**Role**: Developer  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] Failing tests exist (11 tests failed before implementation)

---

## Implementation Summary

### New Files Created

| File | Purpose |
|------|---------|
| `game/i18n/__init__.py` | Package init |
| `game/i18n/language_manager.py` | LanguageManager singleton + translations |
| `game/states/settings_state.py` | Settings screen with language buttons |

### Files Modified

| File | Change |
|------|--------|
| `game/constants.py` | Added `STATE_SETTINGS` |
| `game/state_manager.py` | Added settings state registration |
| `game/states/menu_state.py` | Added Settings button, use translations |

---

## Key Implementation Details

### LanguageManager
- Singleton pattern for global access
- 3 languages: English (en), Chinese (zh), Russian (ru)
- `get(key)` returns translated string or key itself if missing
- `set_language(lang)` changes current language

### Translations
- 24 translation keys covering all UI strings
- Stored in Python dict (simple for 3 languages)

### SettingsState
- 3 language buttons showing native names
- Current language highlighted with white border
- Back button returns to menu

### MenuState Updates
- Added Settings button between New Game and Help
- All buttons use translations from LanguageManager
- `update()` refreshes button text on each frame

---

## Test Results

```
11 passed in 0.25s (new tests)
58 passed in 0.33s (all tests)
```

---

## UI Verification Required

- [ ] Settings button visible on menu
- [ ] Language switching works
- [ ] Chinese characters render correctly
- [ ] Russian characters render correctly
