# menu_full_inner_shadow_hover_start_anim.py
import sys
from pathlib import Path
import math
import pygame

pygame.init()

# ===== CONFIG =====
WINDOW_SIZE = (1280, 730)
TITLE = "ComSci Snakes & Ladders"
FPS = 60

BG_IMG    = "assets/bg/bg_main.png"
START_IMG = "assets/button/start.png"
HOW_IMG   = "assets/button/howtoplay.png"
LOGO_IMG  = "assets/logo/icon.png"

# BG โหมด: "fit" (เห็นครบไม่ซูม), "cover" (เติมเต็มอาจครอป), "exact" (ยืดให้พอดี)
BG_MODE = "fit"
LETTERBOX_COLOR = (12, 24, 36)

# ขนาดปุ่ม (HOW เล็กกว่า START)
BUTTON_RELATIVE_SCALE_START = 0.23
BUTTON_RELATIVE_SCALE_HOW   = 0.20
BUTTON_MAX_WIDTH_PX   = 480
BUTTON_MAX_HEIGHT_PX  = 180

# โลโก้ (คงที่)
LOGO_RELATIVE_SCALE = 0.34
LOGO_MAX_WIDTH_PX   = 760
LOGO_MAX_HEIGHT_PX  = 450
LOGO_MARGIN_PX      = 22  # ระยะห่างโลโก้เหนือ START

# ตำแหน่งปุ่ม (สัดส่วนแนวตั้งของหน้าต่าง)
START_POS_Y = 0.62
HOW_POS_Y   = 0.76

# เอฟเฟกต์ Hover
HOVER_SCALE     = 1.06  # ขยายเมื่อ hover
HOVER_LIFT_PX   = 2     # ยกขึ้นเมื่อ hover
PRESS_OFFSET_PX = 2     # ยุบลงตอนกดค้าง
USE_HAND_CURSOR = True  # เปลี่ยนเคอร์เซอร์เป็นมือ

# อนิเมชัน "หายใจ" (pulse) สำหรับ START (เฉพาะตอนไม่ hover)
START_IDLE_PULSE_AMPL    = 0.03  # ±3%
START_IDLE_PULSE_FREQ_HZ = 1.0   # ครั้ง/วินาที

# INNER SHADOW (เงาด้านในพื้นหลัง)
INNER_SHADOW_THICKNESS   = 90    # ความหนาไล่เงา (px)
INNER_SHADOW_MAX_ALPHA   = 150   # ความเข้มที่ขอบ (0-255)
INNER_SHADOW_RADIUS      = 28    # มุมโค้งของเงา

# ===== UTILS =====
def load_img(pathlike):
    p = Path(pathlike)
    if not p.exists():
        return None
    return pygame.image.load(str(p))  # อย่า convert ก่อน set_mode

def scale_fit(img, out_size):
    iw, ih = img.get_size(); W, H = out_size
    s = min(W/iw, H/ih)
    return pygame.transform.smoothscale(img, (int(iw*s), int(ih*s)))

def scale_cover(img, out_size):
    iw, ih = img.get_size(); W, H = out_size
    s = max(W/iw, H/ih)
    surf = pygame.transform.smoothscale(img, (int(iw*s), int(ih*s)))
    x = (surf.get_width() - W)//2; y = (surf.get_height() - H)//2
    return surf.subsurface(pygame.Rect(x, y, W, H)).copy()

def autoscale_by_width(img, target_w, max_w, max_h):
    if img is None:
        return None
    iw, ih = img.get_size()
    target_w = min(target_w, max_w)
    scale = target_w / iw
    tw, th = int(iw*scale), int(ih*scale)
    if th > max_h:
        scale = max_h / ih
        tw, th = int(iw*scale), int(ih*scale)
    return pygame.transform.smoothscale(img, (tw, th))

def autoscale_button(img, window_size, rel_scale):
    W, _ = window_size
    target_w = int(W * rel_scale)
    return autoscale_by_width(img, target_w, BUTTON_MAX_WIDTH_PX, BUTTON_MAX_HEIGHT_PX)

def autoscale_logo(img, window_size):
    W, _ = window_size
    target_w = int(W * LOGO_RELATIVE_SCALE)
    return autoscale_by_width(img, target_w, LOGO_MAX_WIDTH_PX, LOGO_MAX_HEIGHT_PX)

def fallback_button(label, w=360, h=110):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((70,170,210,255))
    f = pygame.font.SysFont("consolas", 36, bold=True)
    txt = f.render(label, True, (255,255,255))
    surf.blit(txt, txt.get_rect(center=(w//2, h//2)))
    return surf

def make_inner_shadow(size, thickness=80, max_alpha=140, corner_radius=24):
    """
    สร้าง overlay เงาด้านใน (inner shadow/vignette) ขนาด size
    - thickness: ความหนาของเงา (px)
    - max_alpha: ความเข้มสูงสุดที่ขอบ (0-255)
    - corner_radius: มุมโค้งของเงา
    """
    W, H = size
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    steps = max(1, thickness)
    for i in range(steps):
        inset = i
        a = int(max_alpha * (1 - i / steps))
        if a <= 0:
            continue
        rect = pygame.Rect(inset, inset, W - 2*inset, H - 2*inset)
        pygame.draw.rect(
            overlay,
            (0, 0, 0, a // 2),               # //2 เพราะซ้อนหลายชั้น
            rect,
            width=2,
            border_radius=max(0, corner_radius - i // 6)
        )
    return overlay

# ===== BUTTON (hover-only base) =====
class HoverImageButton:
    """ปุ่มใช้รูปเดียว + ทำ hover ด้วยการ scale ภายใน"""
    def __init__(self, base_img: pygame.Surface, center_pos):
        self.img_normal = base_img.convert_alpha()
        self.center = pygame.Vector2(center_pos)
        self.img_hover = self._make_hover_variant(self.img_normal)
        self.is_hover = False
        self.is_pressed = False
        self.rect = self.img_normal.get_rect(center=self.center)

    def _make_hover_variant(self, img: pygame.Surface):
        w, h = img.get_size()
        hw, hh = max(1, int(w * HOVER_SCALE)), max(1, int(h * HOVER_SCALE))
        return pygame.transform.smoothscale(img, (hw, hh)).convert_alpha()

    def _current_image_and_rect(self):
        if self.is_hover:
            img = self.img_hover
            r = img.get_rect(center=(self.center.x, self.center.y - HOVER_LIFT_PX))
        else:
            img = self.img_normal
            r = img.get_rect(center=self.center)
        if self.is_pressed:
            r.y += PRESS_OFFSET_PX
        return img, r

    def update_hover(self, mouse_pos):
        img, r = self._current_image_and_rect()
        self.is_hover = r.collidepoint(mouse_pos)
        self.rect = self._current_image_and_rect()[1]

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.update_hover(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.update_hover(event.pos)
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
            return False
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.update_hover(event.pos)
            was = self.is_pressed
            self.is_pressed = False
            if was and self.rect.collidepoint(event.pos):
                return True
            return False
        return False

    def draw(self, surface):
        img, r = self._current_image_and_rect()
        self.rect = r
        surface.blit(img, r)

# ===== START BUTTON (มีอนิเมชัน idle pulse เมื่อไม่ hover) =====
class AnimatedStartButton(HoverImageButton):
    def __init__(self, base_img: pygame.Surface, center_pos):
        super().__init__(base_img, center_pos)
        self._base_original = self.img_normal.copy()
        self._t = 0.0

    def update_time(self, dt):
        self._t += dt

    def _current_image_and_rect(self):
        # hover: ใช้พฤติกรรม hover ปกติ (หยุด pulse)
        if self.is_hover:
            return super()._current_image_and_rect()

        # idle pulse (ไม่ hover)
        pulse = 1.0 + START_IDLE_PULSE_AMPL * math.sin(2 * math.pi * START_IDLE_PULSE_FREQ_HZ * self._t)
        w, h = self._base_original.get_size()
        sw, sh = max(1, int(w * pulse)), max(1, int(h * pulse))
        img = pygame.transform.smoothscale(self._base_original, (sw, sh)).convert_alpha()
        r = img.get_rect(center=self.center)

        if self.is_pressed:
            r.y += PRESS_OFFSET_PX
        return img, r

# ===== MAIN =====
def run_menu():
    # โหลดภาพ (ยังไม่ convert)
    bg        = load_img(BG_IMG)
    img_start = load_img(START_IMG) or fallback_button("START")
    img_how   = load_img(HOW_IMG)   or fallback_button("HOW TO PLAY", 360, 96)
    logo_base = load_img(LOGO_IMG)  # อาจ None ได้

    # เปิดหน้าต่าง
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # BG
    if bg:
        bg = bg.convert_alpha() if (bg.get_flags() & pygame.SRCALPHA) else bg.convert()
        if BG_MODE == "fit":
            scaled = scale_fit(bg, WINDOW_SIZE)
            bg_canvas = pygame.Surface(WINDOW_SIZE).convert()
            bg_canvas.fill(LETTERBOX_COLOR)
            rect = scaled.get_rect(center=(WINDOW_SIZE[0]//2, WINDOW_SIZE[1]//2))
            bg_canvas.blit(scaled, rect)
            bg_final = bg_canvas
        elif BG_MODE == "cover":
            bg_final = scale_cover(bg, WINDOW_SIZE)
        else:
            bg_final = pygame.transform.smoothscale(bg, WINDOW_SIZE)
    else:
        bg_final = pygame.Surface(WINDOW_SIZE); bg_final.fill(LETTERBOX_COLOR)

    # ===== สร้าง INNER SHADOW overlay หนึ่งครั้ง =====
    inner_shadow = make_inner_shadow(
        WINDOW_SIZE,
        thickness=INNER_SHADOW_THICKNESS,
        max_alpha=INNER_SHADOW_MAX_ALPHA,
        corner_radius=INNER_SHADOW_RADIUS
    )

    # สเกลปุ่ม/โลโก้ แล้ว convert
    img_start = autoscale_button(img_start, WINDOW_SIZE, BUTTON_RELATIVE_SCALE_START).convert_alpha()
    img_how   = autoscale_button(img_how,   WINDOW_SIZE, BUTTON_RELATIVE_SCALE_HOW).convert_alpha()
    if logo_base:
        logo_base = autoscale_logo(logo_base, WINDOW_SIZE).convert_alpha()

    # ปุ่ม (START = มีอนิเมชัน, HOW = ปกติ)
    cx, H = WINDOW_SIZE[0]//2, WINDOW_SIZE[1]
    start_btn = AnimatedStartButton(img_start, (cx, int(H*START_POS_Y)))
    how_btn   = HoverImageButton(img_how,   (cx, int(H*HOW_POS_Y)))

    # โลโก้คงที่
    if logo_base:
        logo_rect = logo_base.get_rect(midbottom=(start_btn.rect.centerx, start_btn.rect.top - LOGO_MARGIN_PX))
        if logo_rect.top < 8:
            logo_rect.top = 8
    else:
        logo_rect = None

    # เคอร์เซอร์
    last_hover_any = False
    if USE_HAND_CURSOR:
        try:
            pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
        except Exception:
            pass

    selected = None
    while True:
        dt = clock.tick(FPS) / 1000.0
        start_btn.update_time(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_q): pygame.quit(); sys.exit(0)
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                selected = "start"

            if start_btn.handle_event(event): selected = "start"
            if how_btn.handle_event(event):   selected = "how_to_play"

        if selected:
            return selected

        # อัปเดต hover (กรณีไม่มี MOUSEMOTION ก็ยังอัปเดต)
        mx, my = pygame.mouse.get_pos()
        start_btn.update_hover((mx, my))
        how_btn.update_hover((mx, my))
        hover_any = start_btn.is_hover or how_btn.is_hover

        if USE_HAND_CURSOR and hover_any != last_hover_any:
            try:
                pygame.mouse.set_system_cursor(
                    pygame.SYSTEM_CURSOR_HAND if hover_any else pygame.SYSTEM_CURSOR_ARROW
                )
            except Exception:
                pass
            last_hover_any = hover_any

        # วาด
        screen.blit(bg_final, (0, 0))
        screen.blit(inner_shadow, (0, 0))  # เงาด้านในบนพื้นหลัง
        if logo_base and logo_rect:
            screen.blit(logo_base, logo_rect)
        start_btn.draw(screen)
        how_btn.draw(screen)

        pygame.display.flip()

if __name__ == "__main__":
    choice = run_menu()
    print("[MENU]", choice)
