"""Settings state for California Jack game."""

import pygame
from typing import Optional

from game.states.base_state import BaseState
from game.ui.button import Button, get_unicode_font
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BACKGROUND, COLOR_WHITE, STATE_MENU
from game.i18n.language_manager import LanguageManager


class SettingsState(BaseState):
    """Settings screen with language selection."""
    
    def __init__(self):
        self.lang = LanguageManager()
        self._create_fonts()
        self._create_buttons()
    
    def _create_fonts(self):
        """Create fonts that support multiple languages."""
        self.title_font = get_unicode_font(48)
        self.label_font = get_unicode_font(32)
    
    def _create_buttons(self):
        """Create UI buttons."""
        btn_width, btn_height = 120, 50
        center_x = WINDOW_WIDTH // 2
        spacing = 130
        
        # Language buttons (single row, 4 languages)
        self.lang_buttons = {
            'en': Button(center_x - int(1.5 * spacing), 320, btn_width, btn_height, self.lang.get_language_name('en')),
            'zh': Button(center_x - int(0.5 * spacing), 320, btn_width, btn_height, self.lang.get_language_name('zh')),
            'ru': Button(center_x + int(0.5 * spacing), 320, btn_width, btn_height, self.lang.get_language_name('ru')),
            'vi': Button(center_x - int(0.5 * spacing), 390, btn_width, btn_height, self.lang.get_language_name('vi')),
        }
        
        # Back button
        self.back_button = Button(40, WINDOW_HEIGHT - 80, 100, 40, self.lang.get('back'))
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle input events."""
        # Check language buttons
        for lang_code, button in self.lang_buttons.items():
            if button.is_clicked(event):
                self.lang.set_language(lang_code)
                self._update_button_text()
                return None
        
        # Check back button
        if self.back_button.is_clicked(event):
            return STATE_MENU
        
        return None
    
    def _update_button_text(self):
        """Update button text after language change."""
        self.back_button.text = self.lang.get('back')
    
    def update(self, dt: float) -> None:
        """Update state."""
        pass
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw settings screen."""
        screen.fill(COLOR_BACKGROUND)
        
        # Draw title
        title_text = self.title_font.render(self.lang.get('settings'), True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 120))
        screen.blit(title_text, title_rect)
        
        # Draw language label
        lang_label = self.label_font.render(self.lang.get('language'), True, COLOR_WHITE)
        lang_rect = lang_label.get_rect(center=(WINDOW_WIDTH // 2, 260))
        screen.blit(lang_label, lang_rect)
        
        # Draw current language indicator
        current = self.lang.get_current()
        for lang_code, button in self.lang_buttons.items():
            button.draw(screen)
            # Highlight current language
            if lang_code == current:
                pygame.draw.rect(screen, COLOR_WHITE, button.rect, 3)
        
        # Draw back button
        self.back_button.draw(screen)
