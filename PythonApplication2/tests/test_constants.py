import pytest
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, STATE_MENU, STATE_GAME, STATE_HELP

class TestConstants:
    def test_window_dimensions(self):
        assert WINDOW_WIDTH > 0
        assert WINDOW_HEIGHT > 0

    def test_state_names_exist(self):
        assert STATE_MENU == 'menu'
        assert STATE_GAME == 'game'
        assert STATE_HELP == 'help'
