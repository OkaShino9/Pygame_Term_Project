# player_select_screen_hover_with_hint.py
import sys
import pygame

pygame.init()

# ---- CONFIG ----
WINDOW_SIZE = (1280, 730)
FPS = 60

# Asset paths
BG_IMG = "assets/bg/bg_main.png"
BTN_2P = "assets/button/button_player/3.png"
BTN_3P = "assets/button/button_player/5.png"
BTN_4P = "assets/button/button_player/7.png"
AVATAR_FILES = [
    "assets/players/player_kao.png",
    "assets/players/player_king.png",
    "assets/players/player_phum.png",
    "assets/players/player_sorkhaw.png",
]
BTN_MODE_CLASSIC = "assets/button/button_classic.png"
BTN_MODE_SPECIAL = "assets/button/button_special.png"

# Layout and scaling constants
TOP_ROW_Y, BOTTOM_ROW_Y = 0.35, 0.66
TOP_GAP_X, AVATAR_GAP_X = 0.15, 0.07
BTN_REL_W, BTN_MAX_WH   = 0.15, (380, 120)
AVA_REL_W, AVA_MAX_WH   = 0.18, (280, 280)
HOVER_SCALE = 1.05
MODE_ROW_Y = 0.25
MODE_GAP_X = 0.12
MODE_BTN_REL_W, MODE_BTN_MAX_WH = 0.17, (450, 150)
MODE_HIGHLIGHT_COLOR = (255, 220, 120)
MODE_DEFAULT = "classic"

# ---- UTILITIES ----
def load_img(path):
    """Safely loads an image, providing a fallback surface if the asset is missing."""
    try:
        return pygame.image.load(path)
    except (pygame.error, FileNotFoundError):
        # Create a fallback gray surface if the image can't be loaded.
        surf = pygame.Surface((10, 10), pygame.SRCALPHA)
        surf.fill((200, 200, 200, 255))
        return surf

def scale_fit(img, out_size):
    """Scales an image to fit within a given size while maintaining aspect ratio."""
    iw, ih = img.get_size(); W, H = out_size
    s = min(W/iw, H/ih)
    return pygame.transform.smoothscale(img, (int(iw*s), int(ih*s)))

def autoscale_by_width(img, target_w, max_w, max_h):
    """Scales an image to a target width, constrained by max width and height."""
    iw, ih = img.get_size()
    w = min(int(target_w), max_w); s = w/iw
    w, h = int(iw*s), int(ih*s)
    if h > max_h:
        s = max_h/ih; w, h = int(iw*s), int(ih*s)
    return pygame.transform.smoothscale(img, (w, h))

def draw_neobrutalist_box(screen, text, center_pos, font, bg_color=(255, 255, 255), text_color=(0, 0, 0), border_color=(0, 0, 0), shadow_offset=(8, 8), padding=(20, 12), border_width=4):
    """Draws a text box with a neo-brutalist style (sharp edges, shadow)."""
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect()

    box_size = (text_rect.width + padding[0] * 2, text_rect.height + padding[1] * 2)
    box_rect = pygame.Rect((0, 0), box_size)
    box_rect.center = center_pos

    shadow_rect = box_rect.copy()
    shadow_rect.x += shadow_offset[0]
    shadow_rect.y += shadow_offset[1]

    pygame.draw.rect(screen, border_color, shadow_rect, border_radius=6)
    pygame.draw.rect(screen, bg_color, box_rect, border_radius=6)
    pygame.draw.rect(screen, border_color, box_rect, border_width, border_radius=6)

    text_rect.center = box_rect.center
    screen.blit(text_surf, text_rect)

# ---- HoverSprite Class ----
class HoverSprite:
    """A versatile sprite for handling hover effects and clicks on UI elements."""
    def __init__(self, img: pygame.Surface, center):
        self.normal = img.convert_alpha()
        w, h = self.normal.get_size()
        self.hover  = pygame.transform.smoothscale(self.normal, (int(w*HOVER_SCALE), int(h*HOVER_SCALE))).convert_alpha()
        self.center = center
        self.rect   = self.normal.get_rect(center=center)
        self.is_hover = False

    def update_hover(self, pos):
        """Updates the hover state based on the mouse position."""
        cur = self.hover if self.is_hover else self.normal
        self.is_hover = cur.get_rect(center=self.center).collidepoint(pos)
        self.rect = (self.hover if self.is_hover else self.normal).get_rect(center=self.center)

    def clicked(self, event):
        """Checks if the sprite was clicked."""
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos)

    def draw(self, screen):
        """Draws the sprite, showing the hover effect if active."""
        screen.blit(self.hover if self.is_hover else self.normal, self.rect)

# ---- MAIN PLAYER SELECTION SCREEN ----
BTN_BACK = "assets/button/back.png"

def run_player_select(screen):
    """Runs the main loop for the player selection screen."""
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("Pixeltype", 48)
    mode_font = pygame.font.SysFont("Pixeltype", 40)

    # Scale and center the background image.
    bg = scale_fit(load_img(BG_IMG), WINDOW_SIZE).convert()
    bg_rect = bg.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))

    # Create and position the back button.
    back_img = autoscale_by_width(load_img(BTN_BACK), WINDOW_SIZE[0]*0.1, 200, 100)
    back_btn = HoverSprite(back_img, (100, 75))

    # Create and position the game mode buttons (Classic/Special).
    classic_img = autoscale_by_width(
        load_img(BTN_MODE_CLASSIC), WINDOW_SIZE[0] * MODE_BTN_REL_W, *MODE_BTN_MAX_WH
    )
    special_img = autoscale_by_width(
        load_img(BTN_MODE_SPECIAL), WINDOW_SIZE[0] * MODE_BTN_REL_W, *MODE_BTN_MAX_WH
    )
    mode_center_x = WINDOW_SIZE[0] // 2
    mode_y = int(WINDOW_SIZE[1] * MODE_ROW_Y)
    mode_gap = int(WINDOW_SIZE[0] * MODE_GAP_X)
    classic_btn = HoverSprite(classic_img, (mode_center_x - mode_gap, mode_y))
    special_btn = HoverSprite(special_img, (mode_center_x + mode_gap, mode_y))
    mode_buttons = {"classic": classic_btn, "special": special_btn}

    # Create buttons for selecting 2, 3, or 4 players.
    two_img   = autoscale_by_width(load_img(BTN_2P), WINDOW_SIZE[0]*BTN_REL_W, *BTN_MAX_WH)
    three_img = autoscale_by_width(load_img(BTN_3P), WINDOW_SIZE[0]*BTN_REL_W, *BTN_MAX_WH)
    four_img  = autoscale_by_width(load_img(BTN_4P), WINDOW_SIZE[0]*BTN_REL_W, *BTN_MAX_WH)

    cx, H = WINDOW_SIZE[0]//2, WINDOW_SIZE[1]
    top_y = int(H*TOP_ROW_Y); gap = int(WINDOW_SIZE[0]*TOP_GAP_X)

    two_btn   = HoverSprite(two_img,   (cx - (two_img.get_width()//2 + gap), top_y))
    three_btn = HoverSprite(three_img, (cx,                                   top_y))
    four_btn  = HoverSprite(four_img,  (cx + (four_img.get_width()//2 + gap), top_y))
    top_buttons = [two_btn, three_btn, four_btn]

    # Load and position the four avatar images.
    avatars = [autoscale_by_width(load_img(p), WINDOW_SIZE[0]*AVA_REL_W, *AVA_MAX_WH) for p in AVATAR_FILES]
    W = WINDOW_SIZE[0]
    spacing = int(W * AVATAR_GAP_X)
    total_w = sum(img.get_width() for img in avatars) + spacing*(len(avatars)-1)
    x = (W - total_w)//2
    y = int(H*BOTTOM_ROW_Y)

    tiles = []
    for img in avatars:
        center = (x + img.get_width()//2, y)
        tiles.append(HoverSprite(img, center))
        x += img.get_width() + spacing

    # --- Game State ---
    target_players = None   # Number of players to be selected (2, 3, or 4).
    selected_order = []     # Stores the indices of avatars in the order they are picked.
    selected_mode = MODE_DEFAULT # Game mode, "classic" or "special".

    while True:
        clock.tick(FPS)
        # --- Event Handling ---
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q): return None # Exit to main menu
                # Confirm selection and proceed to the game.
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and target_players and len(selected_order)==target_players:
                    avatar_paths = [AVATAR_FILES[i] for i in selected_order]
                    player_infos = [{"avatar": path} for path in avatar_paths]
                    return player_infos, selected_mode

            if back_btn.clicked(e): return None # Exit to main menu

            # Handle clicks on the player number selection buttons.
            if two_btn.clicked(e):   target_players, selected_order = 2, []
            if three_btn.clicked(e): target_players, selected_order = 3, []
            if four_btn.clicked(e):  target_players, selected_order = 4, []

            # Handle clicks on the game mode selection buttons.
            if classic_btn.clicked(e): selected_mode = "classic"
            if special_btn.clicked(e): selected_mode = "special"

            # Handle avatar selection logic.
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and target_players:
                for idx, t in enumerate(tiles):
                    if t.rect.collidepoint(e.pos):
                        if idx in selected_order:
                            # Deselect if already selected.
                            selected_order.remove(idx)
                        elif len(selected_order) < target_players:
                            # Select if there's space.
                            selected_order.append(idx)
                        else:
                            # If selection is full, use as a queue (remove first, add last).
                            selected_order.pop(0); selected_order.append(idx)

        # --- Updates ---
        # Update hover states for all interactive elements.
        mx, my = pygame.mouse.get_pos()
        back_btn.update_hover((mx,my))
        for b in top_buttons: b.update_hover((mx,my))
        for btn in mode_buttons.values(): btn.update_hover((mx,my))
        for t in tiles: t.update_hover((mx,my))

        # --- Drawing ---
        screen.blit(bg, bg_rect)
        back_btn.draw(screen)

        for btn in mode_buttons.values():
            btn.draw(screen)

        # ==== Dynamic Hint and Mode Display ====
        # Determine the appropriate hint text based on the current selection state.
        if not target_players:
            hint = "Select number of players"
        elif len(selected_order) < target_players:
            hint = f"Pick {target_players} characters in order ({len(selected_order)}/{target_players})"
        else:
            hint = "Press ENTER to confirm"

        mode_label = "Classic" if selected_mode == "classic" else "Special"
        mode_text = f"Mode: {mode_label}"

        row_y = int(WINDOW_SIZE[1] * 0.115)
        spacing = 40
        padding = (20, 12)

        # Pre-render text to calculate dimensions for centered layout.
        hint_surf = font.render(hint, True, (0, 0, 0))
        mode_surf = mode_font.render(mode_text, True, (0, 0, 0))

        hint_box_w = hint_surf.get_width() + padding[0] * 2
        mode_box_w = mode_surf.get_width() + padding[0] * 2

        total_width = hint_box_w + spacing + mode_box_w
        start_x = (WINDOW_SIZE[0] - total_width) // 2

        hint_center_x = start_x + hint_box_w / 2
        mode_center_x = start_x + hint_box_w + spacing + mode_box_w / 2

        # Draw the hint and mode boxes using the neo-brutalist style.
        draw_neobrutalist_box(screen, hint, (hint_center_x, row_y), font)
        draw_neobrutalist_box(screen, mode_text, (mode_center_x, row_y), mode_font)

        # Draw player count buttons and avatars.
        for b in top_buttons: b.draw(screen)
        for i, t in enumerate(tiles):
            t.draw(screen)
            # If an avatar is selected, display its player order (P1, P2, etc.).
            if i in selected_order:
                rank = selected_order.index(i) + 1
                label = font.render(f"P{rank}", True, (255,255,255))
                screen.blit(label, label.get_rect(midbottom=(t.rect.centerx, t.rect.top - 6)))

        pygame.display.flip()
