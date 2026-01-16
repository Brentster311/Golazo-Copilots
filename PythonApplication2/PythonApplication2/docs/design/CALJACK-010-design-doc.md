# Design Document: CALJACK-010

**Title**: Settings Menu with Language Selection  
**Status**: DRAFT  
**Author**: Copilot  
**Date**: 2025-01-XX

---

## Business Case

Internationalization (i18n) enables the game to reach a broader audience. Supporting English, Chinese, and Russian covers a significant portion of global players. A settings menu also establishes the foundation for future user preferences.

---

## Technical Approach

### Architecture

```
game/
??? i18n/
?   ??? __init__.py
?   ??? translations.py    # Translation dictionaries
?   ??? language_manager.py # Singleton for current language
??? states/
?   ??? settings_state.py  # New settings screen
??? ui/
    ??? dropdown.py        # New dropdown UI component (optional)
```

### Language Manager (Singleton)

```python
class LanguageManager:
    _instance = None
    LANGUAGES = ['en', 'zh', 'ru']
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current = 'en'
        return cls._instance
    
    def get(self, key: str) -> str:
        return TRANSLATIONS[self._current].get(key, key)
    
    def set_language(self, lang: str) -> None:
        if lang in self.LANGUAGES:
            self._current = lang
```

### Translation Dictionary Structure

```python
TRANSLATIONS = {
    'en': {
        'new_game': 'New Game',
        'settings': 'Settings',
        'help': 'Help',
        'back': 'Back',
        # ...
    },
    'zh': {
        'new_game': '???',
        'settings': '??',
        # ...
    },
    'ru': {
        'new_game': '????? ????',
        'settings': '?????????',
        # ...
    }
}
```

### Settings Screen

- Simple screen with:
  - Title: "Settings" (translated)
  - Language selector (3 buttons or cycle button)
  - Back button
- Language buttons show native names: English, ??, ???????

### Font Requirements

- Use a font that supports Latin, CJK, and Cyrillic
- Options:
  1. `Noto Sans` (Google's universal font)
  2. `Arial Unicode MS` (Windows)
  3. Fallback chain in pygame

### Integration Points

1. **MenuState**: Add "Settings" button, use `lang.get('new_game')` for text
2. **GameState**: Translate all labels (Trump, Stock, Player, Turn)
3. **Button**: Accept translated text dynamically
4. **All States**: Get text from LanguageManager instead of hardcoded strings

---

## UI Mockup

```
???????????????????????????????????????
?           Settings                   ?
?                                     ?
?   Language:                         ?
?   ??????????? ??????? ???????????  ?
?   ? English ? ? ?? ? ? ??????? ?  ?
?   ??????????? ??????? ???????????  ?
?                                     ?
?   [ Back ]                          ?
???????????????????????????????????????
```

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Font doesn't support all characters | Test with all 3 languages; use Noto Sans |
| Text overflow in buttons | Use flexible button sizing or shorter translations |
| Performance on language switch | Pre-render nothing; just change strings |

---

## Alternatives Considered

1. **Dropdown selector**: More complex UI, deferred
2. **System locale detection**: Adds complexity, out of scope
3. **External translation files (JSON/YAML)**: Over-engineering for 3 languages

---

## Test Strategy

- Unit tests for LanguageManager
- Unit tests for translation key coverage
- Manual visual testing for all 3 languages
