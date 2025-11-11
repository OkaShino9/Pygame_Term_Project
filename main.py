import pygame
import sys
import math
from select_player import run_player_select
from transitions import curtain_transition
from howtoplay import run_how_to
from game import run_game

# --- Button Class ---
class Button:
    def __init__(self, image_path, center_pos, size, pulse=False):
        self.image_original = pygame.image.load(image_path).convert_alpha()
        self.image_original = pygame.transform.scale(self.image_original, size)
        self.image = self.image_original
        self.rect = self.image.get_rect(center=center_pos)
        self.center_pos = center_pos
        self.pulse = pulse
        self.base_size = size
        self.time_elapsed = 0

    def effect(self, dt):
        if self.pulse:
            self.time_elapsed += dt
            scale_factor = 1 + 0.05 * math.sin(self.time_elapsed * 3)
            new_size = (int(self.base_size[0] * scale_factor),
                        int(self.base_size[1] * scale_factor))
            self.image = pygame.transform.scale(self.image_original, new_size)
            self.rect = self.image.get_rect(center=self.center_pos)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))

# --- Main Menu Class ---
class MainMenu:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        # BG & logo
        self.bg = pygame.image.load("assets/bg/bg_main.png").convert()
        self.bg = pygame.transform.scale(self.bg, (1280, 720))

        self.logo = pygame.image.load("assets/logo/logo.png").convert_alpha()
        self.logo = pygame.transform.scale(
            self.logo,
            (int(self.logo.get_width() * 1.2), int(self.logo.get_height() * 1.2))
        )
        self.logo_rect = self.logo.get_rect(center=(1280 // 2, 200))

        # Buttons
        self.start_button = Button(
            "assets/button/button_start.png",
            center_pos=(1280 // 2, 450),
            size=(300, 150),
            pulse=True
        )
        self.how_button = Button(
            "assets/button/button_how_to_play.png",
            center_pos=(1280 // 2, 550),
            size=(275, 125)
        )

    def render(self):
        """Render หน้าเมนูและ return surface"""
        surface = pygame.Surface((1280, 720))
        surface.blit(self.bg, (0, 0))
        surface.blit(self.logo, self.logo_rect)
        self.start_button.draw(surface)
        self.how_button.draw(surface)
        return surface

    def run(self):
        """แสดงเมนูและรีเทิร์น 'start' เมื่อกด START; How-to จะไปหน้าแยกแล้วกลับมา"""
        while True:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

                if self.start_button.is_clicked(event):
                    return "start"

                if self.how_button.is_clicked(event):
                    # ไปหน้า How-to แล้วกลับมาวนเมนูต่อ
                    run_how_to(self.screen)

            # update
            self.start_button.effect(dt)

            # draw
            self.screen.blit(self.bg, (0, 0))
            self.screen.blit(self.logo, self.logo_rect)
            self.start_button.draw(self.screen)
            self.how_button.draw(self.screen)
            pygame.display.flip()

def main():
    pygame.init()

    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ComSci Snakes & Ladders")

    pygame.mixer.music.load("assets/audio/background.ogg")
    pygame.mixer.music.set_volume(0.7)
    pygame.mixer.music.play(-1)

    state = "main_menu"
    player_infos = None
    selected_mode = "classic"
    menu = MainMenu(screen)

    while True:
        if state == "main_menu":
            choice = menu.run()
            if choice == "start":
                menu_snapshot = menu.render()
                temp_surface = pygame.Surface((1280, 720))
                curtain_transition(
                    screen,
                    menu_snapshot,
                    temp_surface,
                    "assets/bg/transitions.png",
                    duration=0.5
                )
                state = "select_player"

        elif state == "select_player":
            pygame.event.clear()
            selection = run_player_select(screen)
            if selection is None:
                state = "main_menu"
            else:
                player_infos, selected_mode = selection
                state = "game"

        elif state == "game":
            game_result = run_game(screen, player_infos, mode=selected_mode)
            if game_result == "back":
                state = "select_player"
            else:
                state = "main_menu"

if __name__ == "__main__":
    main()
