import pygame
from game.constants import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, STATE_MENU
from game.state_manager import StateManager

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('California Jack')
    clock = pygame.time.Clock()
    state_manager = StateManager()
    state_manager.change_state(STATE_MENU)
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                state_manager.handle_event(event)
        state_manager.update(dt)
        state_manager.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__ == '__main__':
    main()
