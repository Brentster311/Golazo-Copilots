import pygame
from typing import Optional
from game.states.base_state import BaseState
from game.ui.button import Button
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BACKGROUND, COLOR_WHITE, STATE_MENU

class PlaceholderState(BaseState):
    def __init__(self, title: str):
        self.title = title
        self.font = pygame.font.Font(None, 48)
        self.back_button = Button(80, WINDOW_HEIGHT - 50, 100, 40, 'Back')

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if self.back_button.is_clicked(event):
            return STATE_MENU
        return None

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_BACKGROUND)
        title = self.font.render(self.title, True, COLOR_WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(title, title_rect)
        self.back_button.draw(screen)
