from typing import List, Dict
TRANSLATIONS = {
    'en': {'new_game': 'New Game', 'settings': 'Settings', 'help': 'Help', 'back': 'Back', 'language': 'Language', 'california_jack': 'California Jack', 'player1': 'Player 1', 'player2': 'Player 2', 'player1_you': 'Player 1 (You)', 'trump': 'Trump:', 'stock': 'Stock:', 'player_turn': "Player {}'s Turn"},
    'zh': {'new_game': '新游戏', 'settings': '设置', 'help': '帮助', 'back': '返回', 'language': '语言', 'california_jack': '加州杰克', 'player1': '玩家1', 'player2': '玩家2', 'player1_you': '玩家1 (你)', 'trump': '王牌:', 'stock': '牌堆:', 'player_turn': '玩家{}的回合'},
    'ru': {'new_game': 'Новая игра', 'settings': 'Настройки', 'help': 'Помощь', 'back': 'Назад', 'language': 'Язык', 'california_jack': 'California Jack', 'player1': 'Игрок 1', 'player2': 'Игрок 2', 'player1_you': 'Игрок 1 (Вы)', 'trump': 'Козырь:', 'stock': 'Колода:', 'player_turn': 'Ход игрока {}'},
    'vi': {'new_game': 'Tro choi moi', 'settings': 'Cai dat', 'help': 'Tro giup', 'back': 'Quay lai', 'language': 'Ngon ngu', 'california_jack': 'California Jack', 'player1': 'Nguoi choi 1', 'player2': 'Nguoi choi 2', 'player1_you': 'Nguoi choi 1 (Ban)', 'trump': 'Chu bai:', 'stock': 'Bo bai:', 'player_turn': 'Luot cua nguoi choi {}'},
}
LANGUAGE_NAMES = {'en': 'English', 'zh': '中文', 'ru': 'Русский', 'vi': 'Tieng Viet'}
class LanguageManager:
    _instance = None
    LANGUAGES = ['en', 'zh', 'ru', 'vi']
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._current = 'en'
        return cls._instance
    def get(self, key): return TRANSLATIONS.get(self._current, {}).get(key, key)
    def set_language(self, lang): self._current = lang if lang in self.LANGUAGES else self._current
    def get_current(self): return self._current
    def get_languages(self): return self.LANGUAGES.copy()
    def get_language_name(self, lang): return LANGUAGE_NAMES.get(lang, lang)
lang = LanguageManager()
