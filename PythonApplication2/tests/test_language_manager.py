import pytest


class TestLanguageManager:
    def test_singleton_returns_same_instance(self):
        from game.i18n.language_manager import LanguageManager
        lm1 = LanguageManager()
        lm2 = LanguageManager()
        assert lm1 is lm2

    def test_default_language_is_english(self):
        from game.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        assert lm.get_current() == 'en'

    def test_get_translation_returns_string(self):
        from game.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        result = lm.get('new_game')
        assert result == 'New Game'

    def test_get_missing_key_returns_key(self):
        from game.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        result = lm.get('nonexistent_key')
        assert result == 'nonexistent_key'

    def test_set_language_to_chinese(self):
        from game.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        lm.set_language('zh')
        assert lm.get_current() == 'zh'
        lm.set_language('en')

    def test_set_language_to_russian(self):
        from game.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        lm.set_language('ru')
        assert lm.get_current() == 'ru'
        lm.set_language('en')

    def test_set_invalid_language_unchanged(self):
        from game.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        lm.set_language('en')
        lm.set_language('invalid')
        assert lm.get_current() == 'en'

    def test_get_languages_returns_list(self):
        from game.i18n.language_manager import LanguageManager
        lm = LanguageManager()
        langs = lm.get_languages()
        assert 'en' in langs
        assert 'zh' in langs
        assert 'ru' in langs


class TestSettingsState:
    def test_settings_state_creates(self):
        import pygame
        pygame.init()
        from game.states.settings_state import SettingsState
        state = SettingsState()
        assert state is not None

    def test_has_back_button(self):
        import pygame
        pygame.init()
        from game.states.settings_state import SettingsState
        state = SettingsState()
        assert state.back_button is not None

    def test_back_returns_menu(self):
        import pygame
        pygame.init()
        from game.states.settings_state import SettingsState
        from game.constants import STATE_MENU
        state = SettingsState()
        event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': state.back_button.rect.center})
        result = state.handle_event(event)
        assert result == STATE_MENU
