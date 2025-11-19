# how_to.py
import pygame, sys

def run_how_to(screen):
    """
    Displays the 'How to Play' screen and handles user input to return to the main menu.

    Args:
        screen (pygame.Surface): The main display surface to draw on.
    """
    sw, sh = screen.get_size()
    clock = pygame.time.Clock()

    # Load and scale the main 'how to play' image to fit the screen.
    how_to_img = pygame.image.load("assets/bg/howto.png").convert_alpha()
    # Maintain aspect ratio while fitting the image to the screen dimensions.
    scale_factor = min(sw / how_to_img.get_width(), sh / how_to_img.get_height())
    how_to_img = pygame.transform.smoothscale(how_to_img, (int(how_to_img.get_width() * scale_factor), int(how_to_img.get_height() * scale_factor)))
    how_to_rect = how_to_img.get_rect(center=(sw // 2, sh // 2))

    # Load and position the 'back' button.
    back_img = pygame.image.load("assets/button/back.png").convert_alpha()
    back_img = pygame.transform.scale(back_img, (250, 120))
    back_rect = back_img.get_rect(topleft=(24, sh - back_img.get_height() - 24))

    # Main loop for the 'How to Play' screen.
    while True:
        # Event handling.
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Return to the main menu if ESC is pressed.
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return
            # Return to the main menu if the back button is clicked.
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and back_rect.collidepoint(e.pos):
                return

        # Drawing operations.
        screen.fill((18, 18, 18)) # Dark background fallback.
        screen.blit(how_to_img, how_to_rect)
        screen.blit(back_img, back_rect)
        
        pygame.display.flip()
        clock.tick(60)
