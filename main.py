import pygame, sys, math, os
from select_player import run_player_select
from transitions import curtain_transition

# ---------- Mini Button ----------
class Button:
    def __init__(self, img, center, size, pulse=False):
        self.base = pygame.transform.scale(pygame.image.load(img).convert_alpha(), size)
        self.image = self.base; self.rect = self.image.get_rect(center=center)
        self.pulse, self.t, self.size = pulse, 0, size
    def effect(self, dt):
        if not self.pulse: return
        self.t += dt; s = 1 + 0.05 * math.sin(self.t * 3)
        ns = (int(self.size[0]*s), int(self.size[1]*s))
        self.image = pygame.transform.scale(self.base, ns)
        self.rect = self.image.get_rect(center=self.rect.center)
    def draw(self, surf): surf.blit(self.image, self.rect)
    def clicked(self, e): return e.type==pygame.MOUSEBUTTONDOWN and e.button==1 and self.rect.collidepoint(e.pos)

# ---------- Tiny Popup (image + overlay + X) ----------
def make_popup(screen_size, path):
    sw, sh = screen_size
    overlay = pygame.Surface((sw, sh), pygame.SRCALPHA); overlay.fill((0,0,0,140))
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        # scale to fit with 48px margin
        mw, mh = sw-96, sh-96
        k = min(mw/img.get_width(), mh/img.get_height(), 1.0)
        img = pygame.transform.smoothscale(img, (int(img.get_width()*k), int(img.get_height()*k)))
    else:
        img = pygame.Surface((sw-96, sh-96)); img.fill((240,240,240))
    rect = img.get_rect(center=(sw//2, sh//2))
    close = pygame.Rect(rect.right-40, rect.top+10, 30, 30)  # X button area
    return overlay, img, rect, close

def draw_popup(surf, overlay, img, rect, close):
    surf.blit(overlay, (0,0))
    # soft shadow
    sh = pygame.Surface((rect.w+12, rect.h+12), pygame.SRCALPHA)
    pygame.draw.rect(sh, (0,0,0,70), sh.get_rect(), border_radius=12); surf.blit(sh, sh.get_rect(center=rect.center))
    surf.blit(img, rect)
    pygame.draw.rect(surf, (235,235,235), close, border_radius=6)
    pygame.draw.rect(surf, (60,60,60), close, 2, border_radius=6)
    x1,y1,x2,y2 = close.left+7, close.top+7, close.right-7, close.bottom-7
    pygame.draw.line(surf, (60,60,60), (x1,y1), (x2,y2), 2)
    pygame.draw.line(surf, (60,60,60), (x2,y1), (x1,y2), 2)

# ---------- Main Menu ----------
class MainMenu:
    def __init__(self, screen):
        self.screen = screen; self.clock = pygame.time.Clock()
        self.bg  = pygame.transform.scale(pygame.image.load("assets/bg/bg_main.png").convert(), screen.get_size())
        self.logo = pygame.image.load("assets/logo/logo.png").convert_alpha()
        self.logo = pygame.transform.scale(self.logo, (int(self.logo.get_width()*1.2), int(self.logo.get_height()*1.2)))
        self.logo_rect = self.logo.get_rect(center=(screen.get_width()//2, 200))
        self.start = Button("assets/button/button_start.png", (screen.get_width()//2, 450), (300,150), pulse=True)
        self.how   = Button("assets/button/button_how_to_play.png", (screen.get_width()//2, 550), (275,125))
        # popup state
        self.popup_open = False
        self.overlay, self.pop_img, self.pop_rect, self.pop_close = make_popup(screen.get_size(), "assets/howto/how_to_play.png")

    def render(self):
        s = pygame.Surface(self.screen.get_size())
        s.blit(self.bg,(0,0)); s.blit(self.logo,self.logo_rect); self.start.draw(s); self.how.draw(s)
        if self.popup_open: draw_popup(s, self.overlay, self.pop_img, self.pop_rect, self.pop_close)
        return s

    def run(self):
        while True:
            dt = self.clock.tick(60)/1000
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if self.popup_open:
                    if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE: self.popup_open=False
                    if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                        if self.pop_close.collidepoint(e.pos) or not self.pop_rect.collidepoint(e.pos): self.popup_open=False
                    continue
                if self.start.clicked(e): return "start"
                if self.how.clicked(e): self.popup_open=True
            self.start.effect(dt)
            self.screen.blit(self.bg,(0,0)); self.screen.blit(self.logo,self.logo_rect)
            self.start.draw(self.screen); self.how.draw(self.screen)
            if self.popup_open: draw_popup(self.screen, self.overlay, self.pop_img, self.pop_rect, self.pop_close)
            pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ComSci Snakes & Ladders")
    try:
        pygame.mixer.init()
        pygame.mixer.music.load("assets/audio/background.ogg")
        pygame.mixer.music.set_volume(0.05); pygame.mixer.music.play(-1)
    except Exception as e: print("[WARN] BGM:", e)

    menu = MainMenu(screen)
    choice = menu.run()
    if choice == "start":
        snap = menu.render()
        curtain_transition(screen, snap, pygame.Surface((1280,720)), "assets/bg/transitions.png", duration=0.5)
        target_players, order, avatar_paths = run_player_select()
        print("[PLAYER_SELECT]", target_players, order, avatar_paths)
    pygame.quit()

if __name__ == "__main__": main()
