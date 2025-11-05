# how_to.py
import pygame, sys

def run_how_to(screen):
    sw, sh = screen.get_size()
    clock = pygame.time.Clock()

    how = pygame.image.load("assets/bg/howto.png").convert_alpha()
    k = min(sw / how.get_width(), sh / how.get_height())
    how = pygame.transform.smoothscale(how, (int(how.get_width()*k), int(how.get_height()*k)))
    how_rect = how.get_rect(center=(sw//2, sh//2))

    back = pygame.image.load("assets/button/back.png").convert_alpha()
    back = pygame.transform.scale(back, (250, 120))
    back_rect = back.get_rect(topleft=(24, sh - back.get_height() - 24))

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE: return
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and back_rect.collidepoint(e.pos): return

        screen.fill((18,18,18))
        screen.blit(how, how_rect)
        screen.blit(back, back_rect)
        pygame.display.flip()
        clock.tick(60)
