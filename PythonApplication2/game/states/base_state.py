from abc import ABC, abstractmethod
import pygame
from typing import Optional

class BaseState(ABC):
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        pass
