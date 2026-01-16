# Review Notes: CALJACK-010

**Work Item**: CALJACK-010 - Settings Menu with Language Selection  
**Date**: 2025-01-XX

---

## Reviewer Notes

1. All 7 AC are testable and clear
2. Translation table provided in User Story - comprehensive
3. Font support is the main technical risk
4. Button-based selector approved (simpler than dropdown)

---

## Architect Notes

1. LanguageManager singleton pattern approved
2. Translations stored in Python dict (simple for 3 languages)
3. Font fallback chain recommended
4. Integration points identified (5 files to modify)

---

## Agreed Approach

- New module: `game/i18n/` with LanguageManager
- New state: `game/states/settings_state.py`
- Modify: constants.py, state_manager.py, menu_state.py, game_state.py
- Button class unchanged (accepts dynamic text)

---

## Open Questions

None - all resolved.

---

## Sign-off

- Reviewer: ? Approved
- Architect: ? Approved
