import pytest
import pygame
pygame.init()

from game.state_manager import StateManager
from game.constants import STATE_MENU, STATE_GAME

class TestStateManager:
    def test_state_manager_creates(self):
        sm = StateManager()
        assert sm is not None

    def test_change_state_to_menu(self):
        sm = StateManager()
        sm.change_state(STATE_MENU)
        assert sm._current_state_name == STATE_MENU

    def test_change_state_to_game(self):
        sm = StateManager()
        sm.change_state(STATE_GAME)
        assert sm._current_state_name == STATE_GAME
