import pygame
import sys

def curtain_transition(screen, old_surface, new_surface, curtain_image_path, duration=0.6):
    """
    Performs a two-phase curtain transition between two surfaces.

    Phase 1: A curtain image slides down from the top to cover the old_surface.
    Phase 2: After a brief pause, the new_surface is revealed as the curtain
             continues to slide down and off the screen.

    Args:
        screen (pygame.Surface): The main display surface.
        old_surface (pygame.Surface): The surface to transition from.
        new_surface (pygame.Surface): The surface to transition to.
        curtain_image_path (str): Path to the image used for the curtain.
        duration (float): The duration of each phase of the transition in seconds.
    """
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()
    
    # Load the curtain image.
    try:
        curtain = pygame.image.load(curtain_image_path).convert_alpha()
        curtain = pygame.transform.scale(curtain, (screen_width, screen_height))
    except pygame.error:
        # If the image fails to load, use a solid dark color as a fallback.
        curtain = pygame.Surface((screen_width, screen_height))
        curtain.fill((20, 20, 40))
    
    # ========== Phase 1: Curtain slides down to cover the screen ==========
    elapsed = 0
    while elapsed < duration:
        dt = clock.tick(60) / 1000.0
        elapsed += dt
        
        # Use a smoothstep function for eased animation.
        progress = min(elapsed / duration, 1.0)
        smooth_progress = progress * progress * (3.0 - 2.0 * progress)
        
        # The curtain starts at y = -screen_height (off-screen top) and moves to y = 0.
        curtain_y = -screen_height + int(smooth_progress * screen_height)
        
        screen.blit(old_surface, (0, 0))
        screen.blit(curtain, (0, curtain_y))
        pygame.display.flip()
        
        # Ensure the application can be closed during the transition.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
    # Pause for a moment when the curtain fully covers the screen.
    screen.blit(old_surface, (0, 0))
    screen.blit(curtain, (0, 0))
    pygame.display.flip()
    pygame.time.wait(100)  # Pause for 0.1 seconds.

    # ========== Phase 2: Curtain slides away to reveal the new screen ==========
    elapsed = 0
    while elapsed < duration:
        dt = clock.tick(60) / 1000.0
        elapsed += dt
        
        progress = min(elapsed / duration, 1.0)
        smooth_progress = progress * progress * (3.0 - 2.0 * progress)
        
        # The curtain starts at y = 0 and moves down to y = screen_height (off-screen bottom).
        curtain_y = int(smooth_progress * screen_height)
        
        # Draw the new surface underneath the moving curtain.
        screen.blit(new_surface, (0, 0))
        screen.blit(curtain, (0, curtain_y))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()