import pytest
import pygame
pygame.init()

from game.states.menu_state import MenuState
from game.constants import STATE_GAME, STATE_HELP

class TestMenuState:
    def test_menu_state_creates(self):
        state = MenuState()
        assert state is not None

    def test_has_new_game_button(self):
        state = MenuState()
        assert state.new_game_button is not None

    def test_has_help_button(self):
        state = MenuState()
        assert state.help_button is not None
