import pygame
from typing import Optional
from game.states.base_state import BaseState
from game.ui.button import Button, get_unicode_font
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BACKGROUND, STATE_GAME, STATE_HELP, STATE_SETTINGS
from game.i18n.language_manager import LanguageManager

class MenuState(BaseState):
    def __init__(self):
        self.lang = LanguageManager()
        self.font = get_unicode_font(72)
        btn_width, btn_height = 200, 50
        center_x = WINDOW_WIDTH // 2 - btn_width // 2
        self.new_game_button = Button(center_x, 260, btn_width, btn_height, self.lang.get('new_game'))
        self.settings_button = Button(center_x, 340, btn_width, btn_height, self.lang.get('settings'))
        self.help_button = Button(center_x, 420, btn_width, btn_height, self.lang.get('help'))

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if self.new_game_button.is_clicked(event):
            return STATE_GAME
        if self.settings_button.is_clicked(event):
            return STATE_SETTINGS
        if self.help_button.is_clicked(event):
            return STATE_HELP
        return None

    def update(self, dt: float) -> None:
        self.new_game_button.text = self.lang.get('new_game')
        self.settings_button.text = self.lang.get('settings')
        self.help_button.text = self.lang.get('help')

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BACKGROUND)
        title = self.font.render(self.lang.get('california_jack'), True, (255, 255, 255))
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(title, title_rect)
        self.new_game_button.draw(screen)
        self.settings_button.draw(screen)
        self.help_button.draw(screen)
