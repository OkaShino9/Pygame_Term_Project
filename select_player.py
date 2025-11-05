# player_select_screen_hover_with_hint.py
import sys
import pygame

pygame.init()

# ---- CONFIG ----
WINDOW_SIZE = (1280, 730)
FPS = 60

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

# layout / scale
TOP_ROW_Y, BOTTOM_ROW_Y = 0.20, 0.66
TOP_GAP_X, AVATAR_GAP_X = 0.15, 0.07
BTN_REL_W, BTN_MAX_WH   = 0.18, (420, 140)
AVA_REL_W, AVA_MAX_WH   = 0.18, (280, 280)
HOVER_SCALE = 1.05

# ---- UTIL ----
def load_img(path): 
    return pygame.image.load(path)

def scale_fit(img, out_size):
    iw, ih = img.get_size(); W, H = out_size
    s = min(W/iw, H/ih)
    return pygame.transform.smoothscale(img, (int(iw*s), int(ih*s)))

def autoscale_by_width(img, target_w, max_w, max_h):
    iw, ih = img.get_size()
    w = min(int(target_w), max_w); s = w/iw
    w, h = int(iw*s), int(ih*s)
    if h > max_h:
        s = max_h/ih; w, h = int(iw*s), int(ih*s)
    return pygame.transform.smoothscale(img, (w, h))

# ---- Hover sprite (ปุ่ม/อวาตาร์ ใช้ตัวเดียว) ----
class HoverSprite:
    def __init__(self, img: pygame.Surface, center):
        self.normal = img.convert_alpha()
        w, h = self.normal.get_size()
        self.hover  = pygame.transform.smoothscale(self.normal, (int(w*HOVER_SCALE), int(h*HOVER_SCALE))).convert_alpha()
        self.center = center
        self.rect   = self.normal.get_rect(center=center)
        self.is_hover = False

    def update_hover(self, pos):
        cur = self.hover if self.is_hover else self.normal
        self.is_hover = cur.get_rect(center=self.center).collidepoint(pos)
        self.rect = (self.hover if self.is_hover else self.normal).get_rect(center=self.center)

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.rect.collidepoint(event.pos)

    def draw(self, screen):
        screen.blit(self.hover if self.is_hover else self.normal, self.rect)

# ---- MAIN ----
def run_player_select():
    screen = pygame.display.set_mode(WINDOW_SIZE)
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont(None, 24)  # ใช้ฟอนต์เดียว

    # BG fit กลางจอ
    bg = scale_fit(load_img(BG_IMG), WINDOW_SIZE).convert()
    bg_rect = bg.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))

    # ปุ่ม 2/3/4
    two_img   = autoscale_by_width(load_img(BTN_2P), WINDOW_SIZE[0]*BTN_REL_W, *BTN_MAX_WH)
    three_img = autoscale_by_width(load_img(BTN_3P), WINDOW_SIZE[0]*BTN_REL_W, *BTN_MAX_WH)
    four_img  = autoscale_by_width(load_img(BTN_4P), WINDOW_SIZE[0]*BTN_REL_W, *BTN_MAX_WH)

    cx, H = WINDOW_SIZE[0]//2, WINDOW_SIZE[1]
    top_y = int(H*TOP_ROW_Y); gap = int(WINDOW_SIZE[0]*TOP_GAP_X)

    two_btn   = HoverSprite(two_img,   (cx - (two_img.get_width()//2 + gap), top_y))
    three_btn = HoverSprite(three_img, (cx,                                   top_y))
    four_btn  = HoverSprite(four_img,  (cx + (four_img.get_width()//2 + gap), top_y))
    top_buttons = [two_btn, three_btn, four_btn]

    # อวาตาร์ 4 ตัว
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

    # state
    target_players = None
    selected_order = []   # indices of avatars

    while True:
        clock.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit(0)
            if e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_ESCAPE, pygame.K_q): pygame.quit(); sys.exit(0)
                if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and target_players and len(selected_order)==target_players:
                    return target_players, selected_order, [AVATAR_FILES[i] for i in selected_order]

            # คลิกปุ่มจำนวนผู้เล่น
            if two_btn.clicked(e):   target_players, selected_order = 2, []
            if three_btn.clicked(e): target_players, selected_order = 3, []
            if four_btn.clicked(e):  target_players, selected_order = 4, []

            # คลิกเลือกอวาตาร์ตามลำดับ
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1 and target_players:
                for idx, t in enumerate(tiles):
                    if t.rect.collidepoint(e.pos):
                        if idx in selected_order:
                            selected_order.remove(idx)
                        elif len(selected_order) < target_players:
                            selected_order.append(idx)
                        else:
                            selected_order.pop(0); selected_order.append(idx)

        # hover update
        mx, my = pygame.mouse.get_pos()
        for b in top_buttons: b.update_hover((mx,my))
        for t in tiles: t.update_hover((mx,my))

        # draw
        screen.blit(bg, bg_rect)

        # ==== ข้อความแนะนำ (hint) ด้านบน ====
        if not target_players:
            hint = "Select number of players: 2 / 3 / 4"
        elif len(selected_order) < target_players:
            hint = f"Pick {target_players} avatars in order ({len(selected_order)}/{target_players})"
        else:
            hint = "Press ENTER to confirm"
        hint_surf = font.render(hint, True, (255,255,255))
        screen.blit(hint_surf, hint_surf.get_rect(center=(WINDOW_SIZE[0]//2, int(WINDOW_SIZE[1]*0.10))))

        # ปุ่มบน + อวาตาร์
        for b in top_buttons: b.draw(screen)
        for i, t in enumerate(tiles):
            t.draw(screen)
            if i in selected_order:
                rank = selected_order.index(i) + 1
                label = font.render(f"P{rank}", True, (255,255,200))
                screen.blit(label, label.get_rect(midbottom=(t.rect.centerx, t.rect.top - 6)))

        pygame.display.flip()

# demo
if __name__ == "__main__":
    print(run_player_select())