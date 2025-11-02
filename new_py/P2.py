# player_select_screen.py
import sys
from pathlib import Path
import math
import pygame

pygame.init()

# ===== CONFIG =====
WINDOW_SIZE = (1280, 730)
TITLE = "ComSci Snakes & Ladders — Select Players"
FPS = 60
LETTERBOX_COLOR = (12, 24, 36)

# assets (หลายชื่อเผื่อไฟล์ของคุณ)
BG_IMG = "assets/bg.png"
BTN_2P_CANDIDATES = ["C:/pythonproject/new_py/assets/button_player/3.png"]
BTN_3P_CANDIDATES = ["C:/pythonproject/new_py/assets/button_player/5.png"]
BTN_4P_CANDIDATES = ["C:/pythonproject/new_py/assets/button_player/7.png"]

AVATAR_FILES = [
    "assets/p1.png",
    "assets/p2.png",
    "assets/p3.png",
    "assets/p4.png",
]

# ขนาด/เอฟเฟกต์
BTN_TOP_REL_W   = 0.17  # ความกว้างปุ่มบน ≈ 17% ของความกว้างหน้าต่าง
BTN_TOP_MAX_W   = 360
BTN_TOP_MAX_H   = 130
AVATAR_REL_W    = 0.16  # ความกว้าง avatar ≈ 16% ของความกว้างหน้าต่าง
AVATAR_MAX_W    = 260
AVATAR_MAX_H    = 260

HOVER_SCALE     = 1.06
HOVER_LIFT_PX   = 2
PRESS_OFFSET_PX = 2
USE_HAND_CURSOR = True

# ตำแหน่ง (อิงสัดส่วนจอ)
TOP_ROW_Y       = 0.18   # ปุ่ม 2/3/4
BOTTOM_ROW_Y    = 0.65   # avatar ทั้ง 4
TOP_GAP_X       = 0.06   # ระยะห่างแนวนอนระหว่างปุ่มบน (เป็นสัดส่วนของความกว้าง)
AVATAR_GAP_X    = 0.07   # ระยะห่างระหว่าง avatar

# ===== UTILS =====
def load_first_existing(paths):
    for p in paths if isinstance(paths, (list, tuple)) else [paths]:
        if Path(p).exists():
            return pygame.image.load(p)
    return None

def scale_fit(img, out_size):
    iw, ih = img.get_size(); W, H = out_size
    s = min(W/iw, H/ih)
    return pygame.transform.smoothscale(img, (int(iw*s), int(ih*s)))

def autoscale_by_width(img, target_w, max_w, max_h):
    iw, ih = img.get_size()
    target_w = min(int(target_w), max_w)
    sc = target_w / iw
    w, h = int(iw*sc), int(ih*sc)
    if h > max_h:
        sc = max_h / ih
        w, h = int(iw*sc), int(ih*sc)
    return pygame.transform.smoothscale(img, (w, h))

def fallback_button(text, w=260, h=90, color=(40,140,200)):
    s = pygame.Surface((w, h), pygame.SRCALPHA); s.fill((*color,255))
    f = pygame.font.SysFont("consolas", 28, bold=True)
    t = f.render(text, True, (255,255,255))
    s.blit(t, t.get_rect(center=(w//2, h//2)))
    return s

def fallback_avatar(label, w=180, h=220):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((0,0,0,0))
    rect = pygame.Rect(0,0,w,h)
    pygame.draw.rect(s, (80,120,200), rect, border_radius=16)
    f = pygame.font.SysFont("consolas", 28, bold=True)
    t = f.render(label, True, (255,255,255))
    s.blit(t, t.get_rect(center=(w//2, h//2)))
    return s

def draw_outline(surface, rect, color=(255, 239, 120), width=4, radius=18):
    pygame.draw.rect(surface, color, rect.inflate(8,8), width=width, border_radius=radius)

def draw_player_tag(surface, midtop, text, color):
    f = pygame.font.SysFont("consolas", 22, bold=True)
    t = f.render(text, True, color)
    tg = t.get_rect(midbottom=(midtop[0], midtop[1]-6))
    surface.blit(t, tg)

# ===== WIDGETS =====
class HoverButton:
    def __init__(self, img: pygame.Surface, center):
        self.normal = img.convert_alpha()
        self.hover  = self._make_hover(img)
        self.center = pygame.Vector2(center)
        self.is_hover = False
        self.is_pressed = False
        self.rect = self.normal.get_rect(center=self.center)

    def _make_hover(self, img):
        w,h = img.get_size()
        hw,hh = int(w*HOVER_SCALE), int(h*HOVER_SCALE)
        return pygame.transform.smoothscale(img, (hw,hh)).convert_alpha()

    def current(self):
        if self.is_hover:
            r = self.hover.get_rect(center=(self.center.x, self.center.y - HOVER_LIFT_PX))
            img = self.hover
        else:
            r = self.normal.get_rect(center=self.center)
            img = self.normal
        if self.is_pressed:
            r.y += PRESS_OFFSET_PX
        return img, r

    def update_hover(self, pos):
        _, r = self.current()
        self.is_hover = r.collidepoint(pos)
        self.rect = self.current()[1]

    def handle(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.update_hover(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.update_hover(event.pos)
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.update_hover(event.pos)
            was = self.is_pressed
            self.is_pressed = False
            if was and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        img, r = self.current()
        self.rect = r
        screen.blit(img, r)

class AvatarTile:
    """ไทล์ตัวละคร: เลือก/ไม่เลือก + hover + lock จำนวนสูงสุด"""
    def __init__(self, img: pygame.Surface, center, label="P", color=(255,210,0)):
        self.base = img.convert_alpha()
        self.center = pygame.Vector2(center)
        self.hover  = self._make_hover(img)
        self.is_hover = False
        self.selected = False
        self.disabled = False
        self.rect = self.base.get_rect(center=self.center)
        self.label = label
        self.label_color = color

    def _make_hover(self, img):
        w,h = img.get_size()
        return pygame.transform.smoothscale(img, (int(w*HOVER_SCALE), int(h*HOVER_SCALE))).convert_alpha()

    def current(self):
        img = self.hover if self.is_hover and not self.disabled else self.base
        y  = -HOVER_LIFT_PX if (self.is_hover and not self.disabled) else 0
        r = img.get_rect(center=(self.center.x, self.center.y + y))
        return img, r

    def update_hover(self, pos):
        _, r = self.current()
        self.is_hover = r.collidepoint(pos)
        self.rect = self.current()[1]

    def toggle(self):
        if not self.disabled:
            self.selected = not self.selected

    def draw(self, screen):
        img, r = self.current()
        self.rect = r
        if self.disabled:
            # ทำจางลง
            tmp = img.copy()
            tmp.fill((0,0,0,120), special_flags=pygame.BLEND_RGBA_SUB)
            screen.blit(tmp, r)
        else:
            screen.blit(img, r)
        # ป้าย P1..P4
        draw_player_tag(screen, r.midtop, self.label, self.label_color)
        # กรอบเมื่อเลือก
        if self.selected:
            draw_outline(screen, r, (255, 238, 120), 4, 20)

# ===== MAIN SCREEN =====
def run_player_select():
    # window
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # BG
    bg = load_first_existing(BG_IMG)
    if bg:
        bg = scale_fit(bg, WINDOW_SIZE).convert()
        bg_canvas = pygame.Surface(WINDOW_SIZE).convert()
        bg_canvas.fill(LETTERBOX_COLOR)
        rect = bg.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))
        bg_canvas.blit(bg, rect)
        bg_final = bg_canvas
    else:
        bg_final = pygame.Surface(WINDOW_SIZE); bg_final.fill(LETTERBOX_COLOR)

    # load buttons top
    def load_scaled(cands, rel_w, mw, mh, fallback_txt):
        img = load_first_existing(cands)
        if img is None:
            img = fallback_button(fallback_txt, w=min(mw, 280), h=min(mh, 100))
        img = autoscale_by_width(img, WINDOW_SIZE[0]*rel_w, mw, mh)
        return img

    two_img   = load_scaled(BTN_2P_CANDIDATES, BTN_TOP_REL_W, BTN_TOP_MAX_W, BTN_TOP_MAX_H, "TWO PLAYER")
    three_img = load_scaled(BTN_3P_CANDIDATES, BTN_TOP_REL_W, BTN_TOP_MAX_W, BTN_TOP_MAX_H, "THREE PLAYER")
    four_img  = load_scaled(BTN_4P_CANDIDATES, BTN_TOP_REL_W, BTN_TOP_MAX_W, BTN_TOP_MAX_H, "FOUR PLAYER")

    # place top buttons
    cx = WINDOW_SIZE[0]//2
    top_y = int(WINDOW_SIZE[1]*TOP_ROW_Y)
    gap_px = int(WINDOW_SIZE[0]*TOP_GAP_X)
    # ตำแหน่งเรียงกลาง
    two_btn   = HoverButton(two_img,   (cx - (two_img.get_width()//2 + gap_px), top_y))
    three_btn = HoverButton(three_img, (cx,                                     top_y))
    four_btn  = HoverButton(four_img,  (cx + (four_img.get_width()//2 + gap_px), top_y))

    # load avatars
    avatars_img = []
    for i, path in enumerate(AVATAR_FILES, start=1):
        img = load_first_existing(path)
        if img is None:
            img = fallback_avatar(f"P{i}")
        img = autoscale_by_width(img, WINDOW_SIZE[0]*AVATAR_REL_W, AVATAR_MAX_W, AVATAR_MAX_H)
        avatars_img.append(img)

    # place avatars evenly
    total = 4
    W = WINDOW_SIZE[0]
    spacing = int(W * AVATAR_GAP_X)
    total_width = sum(img.get_width() for img in avatars_img) + spacing*(total-1)
    start_x = (W - total_width)//2
    y = int(WINDOW_SIZE[1]*BOTTOM_ROW_Y)
    colors = [(210,90,255),(80,220,255),(160,255,80),(255,220,80)]
    tiles = []
    x = start_x
    for i, img in enumerate(avatars_img):
        tiles.append(AvatarTile(img, (x + img.get_width()//2, y), label=f"P{i+1}", color=colors[i%len(colors)]))
        x += img.get_width() + spacing

    # state
    target_players = None  # 2/3/4
    selected_order = []    # เก็บ index ที่เลือกตามลำดับ

    # cursor
    last_hover_any = False
    if USE_HAND_CURSOR:
        try: pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception: pass

    # loop
    while True:
        dt = clock.tick(FPS) / 1000.0
        hover_any = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q):
                pygame.quit(); sys.exit(0)

            # click top buttons
            if two_btn.handle(event):
                target_players = 2
                # reset selections
                for t in tiles: t.selected = False
                selected_order.clear()
            if three_btn.handle(event):
                target_players = 3
                for t in tiles: t.selected = False
                selected_order.clear()
            if four_btn.handle(event):
                target_players = 4
                for t in tiles: t.selected = False
                selected_order.clear()

            # click avatars
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and target_players:
                for idx, t in enumerate(tiles):
                    if t.rect.collidepoint(event.pos):
                        # toggle with cap
                        if t.selected:
                            t.selected = False
                            if idx in selected_order:
                                selected_order.remove(idx)
                        else:
                            if len(selected_order) < target_players:
                                t.selected = True
                                selected_order.append(idx)
                            else:
                                # ถ้าเต็มแล้ว: สลับตัวที่เลือกคนแรกออก แล้วเลือกตัวใหม่แทน
                                out = selected_order.pop(0)
                                tiles[out].selected = False
                                t.selected = True
                                selected_order.append(idx)

            # confirm
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                if target_players and len(selected_order) == target_players:
                    return target_players, selected_order  # เช่น (3, [0,2,3])

            # update hover states from events
            two_btn.handle(event); three_btn.handle(event); four_btn.handle(event)

        # hover update (แม้ไม่มี motion)
        mx,my = pygame.mouse.get_pos()
        two_btn.update_hover((mx,my)); three_btn.update_hover((mx,my)); four_btn.update_hover((mx,my))
        for t in tiles:
            t.update_hover((mx,my))

        hover_any = (two_btn.is_hover or three_btn.is_hover or four_btn.is_hover or any(t.is_hover for t in tiles))
        if USE_HAND_CURSOR and hover_any != last_hover_any:
            try:
                pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND if hover_any else pygame.SYSTEM_CURSOR_ARROW)
            except Exception:
                pass
            last_hover_any = hover_any

        # draw
        screen.blit(bg_final, (0,0))

        # hint text
        font = pygame.font.SysFont("consolas", 22)
        if not target_players:
            hint = "Select number of players (2 / 3 / 4)"
        else:
            if len(selected_order) < target_players:
                hint = f"Select {target_players} player(s): {len(selected_order)}/{target_players}"
            else:
                hint = "Press ENTER to confirm"
        tip = font.render(hint, True, (255,255,255))
        screen.blit(tip, tip.get_rect(center=(WINDOW_SIZE[0]//2, int(WINDOW_SIZE[1]*0.08))))

        # buttons top
        two_btn.draw(screen); three_btn.draw(screen); four_btn.draw(screen)

        # avatars; หากยังไม่เลือกจำนวนผู้เล่น ให้ทำจาง ๆ ทั้งหมดเป็นสัญญาณ
        for t in tiles:
            prev = t.disabled
            t.disabled = (target_players is None)
            t.draw(screen)
            t.disabled = prev

        # footer small help
        small = pygame.font.SysFont("consolas", 18)
        s = small.render("ENTER = confirm • ESC = quit", True, (230,230,230))
        screen.blit(s, s.get_rect(midbottom=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]-10)))

        pygame.display.flip()

# เดโมรันเดี่ยว
if __name__ == "__main__":
    result = run_player_select()
    print("[PLAYER_SELECT] target, order =", result)
