"""Language manager for internationalization."""

from typing import List, Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    'en': {
        'new_game': 'New Game',
        'settings': 'Settings',
        'help': 'Help',
        'back': 'Back',
        'player1': 'Player 1',
        'player2': 'Player 2',
        'player1_you': 'Player 1 (You)',
        'trump': 'Trump:',
        'stock': 'Stock:',
        'player_turn': "Player {}'s Turn",
        'game_over': 'Game Over!',
        'end_game': 'End the game?',
        'yes_exit': 'Yes, Exit',
        'cancel': 'Cancel',
        'language': 'Language',
        'lang_english': 'English',
        'lang_chinese': '??',
        'lang_russian': '???????',
        'california_jack': 'California Jack',
        'trick_complete': 'Trick Complete!',
    },
    'zh': {
        'new_game': '???',
        'settings': '??',
        'help': '??',
        'back': '??',
        'player1': '??1',
        'player2': '??2',
        'player1_you': '??1 (?)',
        'trump': '??:',
        'stock': '??:',
        'player_turn': '??{}???',
        'game_over': '????!',
        'end_game': '?????',
        'yes_exit': '????',
        'cancel': '??',
        'language': '??',
        'lang_english': 'English',
        'lang_chinese': '??',
        'lang_russian': '???????',
        'california_jack': '????',
        'trick_complete': '????!',
    },
    'ru': {
        'new_game': '????? ????',
        'settings': '?????????',
        'help': '??????',
        'back': '?????',
        'player1': '????? 1',
        'player2': '????? 2',
        'player1_you': '????? 1 (??)',
        'trump': '??????:',
        'stock': '??????:',
        'player_turn': '??? ?????? {}',
        'game_over': '???? ????????!',
        'end_game': '????????? ?????',
        'yes_exit': '??, ?????',
        'cancel': '??????',
        'language': '????',
        'lang_english': 'English',
        'lang_chinese': '??',
        'lang_russian': '???????',
        'california_jack': '?????????? ????',
        'trick_complete': '??????!',
    },
}


class LanguageManager:
    """Singleton manager for language/translations."""
    
    _instance = None
    LANGUAGES = ['en', 'zh', 'ru']
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current = 'en'
        return cls._instance
    
    def get(self, key: str) -> str:
        """Get translated string for key."""
        return TRANSLATIONS.get(self._current, {}).get(key, key)
    
    def set_language(self, lang: str) -> None:
        """Set current language."""
        if lang in self.LANGUAGES:
            self._current = lang
    
    def get_current(self) -> str:
        """Get current language code."""
        return self._current
    
    def get_languages(self) -> List[str]:
        """Get list of available language codes."""
        return self.LANGUAGES.copy()


# Global instance for easy import
lang = LanguageManager()
