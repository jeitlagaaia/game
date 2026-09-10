
import pygame
WIDTH, HEIGHT, FPS = 800, 600, 60
NAVY = (9, 24, 43)
def run_game():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Star Catcher")
    clock = pygame.time.Clock()
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill(NAVY)
        pygame.display.flip()
    pygame.quit()
