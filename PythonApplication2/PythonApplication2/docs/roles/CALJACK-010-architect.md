# Role Decision Document: Architect

**Work Item**: CALJACK-010 - Settings Menu with Language Selection  
**Role**: Architect  
**Date**: 2025-01-XX

---

## First Action Verification

- [x] User Story exists
- [x] Design Doc exists
- [x] Reviewer approved

---

## Architecture Review

### Proposed Structure

```
game/
??? i18n/
?   ??? __init__.py
?   ??? language_manager.py  # Singleton + translations
??? states/
?   ??? settings_state.py    # New state
??? constants.py             # Add STATE_SETTINGS
??? state_manager.py         # Register settings state
```

### Design Decisions

| Decision | Rationale |
|----------|-----------|
| Singleton LanguageManager | Global access needed from all states |
| Translations in Python dict | Simple, no external files needed for 3 languages |
| Button-based selector | Simpler than dropdown, works with existing Button class |

---

## Integration Points

1. **constants.py**: Add `STATE_SETTINGS = 'settings'`
2. **state_manager.py**: Add settings state registration
3. **menu_state.py**: Add Settings button, use translations
4. **game_state.py**: Use translations for all labels
5. **All buttons**: Get text from LanguageManager

---

## Font Strategy

```python
# Try fonts in order until one works
FONT_CHAIN = ['Segoe UI Symbol', 'Noto Sans', 'Arial Unicode MS', None]

def get_font(size):
    for font_name in FONT_CHAIN:
        try:
            return pygame.font.SysFont(font_name, size)
        except:
            continue
    return pygame.font.Font(None, size)  # Fallback
```

---

## API Design

### LanguageManager

```python
class LanguageManager:
    def get(self, key: str) -> str
    def set_language(self, lang: str) -> None
    def get_current(self) -> str
    def get_languages(self) -> List[str]
```

### Usage Pattern

```python
from game.i18n import lang

# In any state:
text = lang.get('new_game')  # Returns translated string
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Missing translation key | Return key itself as fallback |
| Font not found | Fallback chain with default |
| Button too small for text | Buttons auto-size to content |

---

## Review Notes

Created at: `docs/design/CALJACK-010-review-notes.md`

---

## Recommendation

**APPROVED** - Architecture is sound and follows existing patterns.

No new User Stories required.
