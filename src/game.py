# game.py — เมนูเลือกผู้เล่น + แถบเต๋า + เส้นงู/บันได + ป๊อปอัปผู้ชนะ + ทอยเกินเข้าชนะทันที
import os
import pygame
from typing import List, Optional, Tuple
from config import (
    W, H, FPS, COLS, ROWS, SIDEBAR_W,
    COL_PANEL, PLAYER_STYLES
)
from board import Board
from player import Player
from dice import Dice

STATE_MENU = "MENU"
STATE_PLAY = "PLAY"

class Game:
    def __init__(self, snakes_ladders: Optional[dict[int,int]] = None):
        pygame.init()
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Snakes & Ladders — OOP")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(None, 26)
        self.font_big = pygame.font.SysFont(None, 40)
        self.font_small = pygame.font.SysFont(None, 22)

        self.state = STATE_MENU
        self.selected_players = 2  # default in menu

        # Board + snakes/ladders
        self.board = Board(snakes_ladders or self._default_snakes_ladders())

        # Gameplay vars
        self.players: List[Player] = []
        self.turn = 0
        self.dice = Dice()
        self.last_roll: Optional[int] = None
        self.win_cell = COLS * ROWS
        self.winner: Optional[str] = None
        self.running = True

        # Optional dice images (assets/dice-1.png ... dice-6.png)
        self.dice_images = self._load_dice_images()

        # Menu buttons
        self._build_menu_buttons()

    # ---------- MENU ----------
    def _build_menu_buttons(self):
        cx = (W - SIDEBAR_W) // 2
        start_y = H // 3
        bw, bh, gap = 160, 48, 14
        self.btn_players = {
            2: pygame.Rect(cx - bw//2, start_y + 0*(bh+gap), bw, bh),
            3: pygame.Rect(cx - bw//2, start_y + 1*(bh+gap), bw, bh),
            4: pygame.Rect(cx - bw//2, start_y + 2*(bh+gap), bw, bh),
        }
        self.btn_start = pygame.Rect(cx - bw//2, start_y + 3*(bh+gap) + 10, bw, bh)

    def _draw_button(self, rect: pygame.Rect, text: str, active: bool=False):
        base = (230, 235, 250) if active else (214, 220, 240)
        border = (150, 160, 190) if active else (160, 170, 200)
        pygame.draw.rect(self.screen, base, rect, border_radius=10)
        pygame.draw.rect(self.screen, border, rect, 2, border_radius=10)
        label = self.font.render(text, True, (25, 35, 70))
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_menu(self):
        self.screen.fill((242, 246, 255))
        title = self.font_big.render("Snakes & Ladders", True, (35, 45, 80))
        self.screen.blit(title, title.get_rect(center=((W - SIDEBAR_W)//2, H//5)))
        for k, r in self.btn_players.items():
            self._draw_button(r, f"{k} Players", active=(k == self.selected_players))
        self._draw_button(self.btn_start, "Start Game", active=True)
        hint = self.font_small.render("Click players-count, then Start (ESC to quit)", True, (60, 70, 100))
        self.screen.blit(hint, hint.get_rect(center=((W - SIDEBAR_W)//2, H - 60)))

    def _menu_handle_click(self, pos: Tuple[int,int]):
        for k, r in self.btn_players.items():
            if r.collidepoint(pos):
                self.selected_players = k
                return
        if self.btn_start.collidepoint(pos):
            self._start_new_game(self.selected_players)

    # ---------- INIT / RESET ----------
    def _start_new_game(self, n_players: int):
        self.players = []
        for i in range(n_players):
            fill, stroke = PLAYER_STYLES[i]
            self.players.append(Player(f"P{i+1}", fill, stroke))
        self.turn = 0
        self.last_roll = None
        self.winner = None
        self.state = STATE_PLAY

    def _restart_same_players(self):
        n = len(self.players) if self.players else self.selected_players
        if n < 2: n = self.selected_players or 2
        self._start_new_game(n)

    # ---------- utilities ----------
    def _default_snakes_ladders(self) -> dict[int, int]:
        total = COLS * ROWS
        def at(pct: float) -> int:
            return max(1, min(total, int(total * pct)))
        return {
            # ladders
            at(0.05): at(0.18),
            at(0.12): at(0.32),
            at(0.28): at(0.48),
            # snakes
            at(0.62): at(0.41),
            at(0.74): at(0.36),
            at(0.88): at(0.57),
        }

    def _load_dice_images(self):
        imgs = []
        base = "assets"
        for i in range(1, 7):
            path = os.path.join(base, f"dice-{i}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                imgs.append(img)
        return imgs

    # ---------- sidebar / dice ----------
    def _draw_vector_dice(self, x, y, w, h, value: int):
        size = min(w, h) - 10
        dx = x + (w - size) // 2
        dy = y + (h - size) // 2
        pygame.draw.rect(self.screen, (255, 255, 255), (dx, dy, size, size), border_radius=12)
        pygame.draw.rect(self.screen, (180, 185, 200), (dx, dy, size, size), 3, border_radius=12)

        r = max(4, size // 12)
        cx = dx + size // 2
        cy = dy + size // 2
        offset = size // 4
        dots = {
            1: [(cx, cy)],
            2: [(cx - offset, cy - offset), (cx + offset, cy + offset)],
            3: [(cx - offset, cy - offset), (cx, cy), (cx + offset, cy + offset)],
            4: [(cx - offset, cy - offset), (cx + offset, cy - offset),
                (cx - offset, cy + offset), (cx + offset, cy + offset)],
            5: [(cx - offset, cy - offset), (cx + offset, cy - offset),
                (cx, cy),
                (cx - offset, cy + offset), (cx + offset, cy + offset)],
            6: [(cx - offset, cy - offset), (cx, cy - offset), (cx + offset, cy - offset),
                (cx - offset, cy + offset), (cx, cy + offset), (cx + offset, cy + offset)],
        }
        for (px, py) in dots.get(value, dots[1]):
            pygame.draw.circle(self.screen, (35, 35, 35), (px, py), r)

    def draw_sidebar(self):
        panel_x = W - SIDEBAR_W
        pygame.draw.rect(self.screen, COL_PANEL, (panel_x, 0, SIDEBAR_W, H))

        title = self.font.render("DICE", True, (20, 30, 60))
        self.screen.blit(title, (panel_x + 20, 16))

        dice_box_w = SIDEBAR_W - 40
        dice_box_h = dice_box_w
        box_x = panel_x + 20
        box_y = 46
        pygame.draw.rect(self.screen, (210, 216, 236), (box_x, box_y, dice_box_w, dice_box_h), 2)

        if self.last_roll and len(self.dice_images) == 6:
            raw = self.dice_images[self.last_roll - 1]
            img = pygame.transform.smoothscale(raw, (dice_box_w - 8, dice_box_h - 8))
            self.screen.blit(img, (box_x + 4, box_y + 4))
        else:
            self._draw_vector_dice(box_x, box_y, dice_box_w, dice_box_h, self.last_roll or 1)

        turn_txt = f"Turn: {self.players[self.turn].name}" if self.players else "Turn: -"
        self.screen.blit(self.font.render(turn_txt, True, (20, 30, 60)), (panel_x + 20, box_y + dice_box_h + 12))

        roll_txt = f"Roll: {self.last_roll}" if self.last_roll is not None else "Roll: -"
        self.screen.blit(self.font.render(roll_txt, True, (20, 30, 60)), (panel_x + 20, box_y + dice_box_h + 38))

        self.screen.blit(self.font_small.render("SPACE = Roll", True, (30, 40, 70)), (panel_x + 20, box_y + dice_box_h + 64))
        self.screen.blit(self.font_small.render("ESC = Quit",  True, (30, 40, 70)), (panel_x + 20, box_y + dice_box_h + 84))

    # ---------- events ----------
    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if self.state == STATE_MENU:
                        self.running = False
                    else:
                        self.state = STATE_MENU
                        self.winner = None
                elif self.state == STATE_PLAY and self.winner is None:
                    if e.key == pygame.K_SPACE:
                        self._do_turn()
                elif self.state == STATE_PLAY and self.winner is not None:
                    # Win popup controls
                    if e.key == pygame.K_r:
                        self._restart_same_players()
                    elif e.key == pygame.K_m:
                        self.state = STATE_MENU
                        self.winner = None
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.state == STATE_MENU:
                    self._menu_handle_click(e.pos)

    # ---------- gameplay ----------
    def _do_turn(self):
        if not self.players:
            return
        p = self.players[self.turn]
        self.last_roll = self.dice.roll()

        # เดิน และ clamp ถึงเส้นชัย (เช่น 100) ทันทีถ้าเกิน
        p.move(self.last_roll, self.win_cell)

        # ถึงเส้นชัยแล้ว: ชนะเลย ไม่ต้องเช็คงู/บันได
        if p.pos == self.win_cell:
            self.winner = p.name
            return

        # ยังไม่ถึงเส้นชัย ค่อยเช็คงู/บันได
        jumped_to = self.board.apply_snake_ladder(p.pos)
        if jumped_to != p.pos:
            p.jump_to(jumped_to)

        # เผื่อบันไดพาขึ้นถึงเส้นชัยพอดี
        if p.pos == self.win_cell:
            self.winner = p.name
        else:
            self.turn = (self.turn + 1) % len(self.players)

    # ---------- draw players ----------
    def draw_players(self):
        if not self.players:
            return
        offsets = [(-int(self.board.cell*0.28), 0),
                   ( int(self.board.cell*0.28), 0),
                   (0, -int(self.board.cell*0.28)),
                   (0,  int(self.board.cell*0.28))]
        for i, p in enumerate(self.players):
            off = offsets[i] if i < len(offsets) else (0, 0)
            p.draw(self.screen, self.board, offset=off)

    # ---------- win popup ----------
    def draw_win_popup(self):
        if not self.winner:
            return
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        self.screen.blit(overlay, (0, 0))

        pw, ph = 420, 200
        rect = pygame.Rect((W - pw)//2, (H - ph)//2, pw, ph)
        pygame.draw.rect(self.screen, (255, 255, 255), rect, border_radius=16)
        pygame.draw.rect(self.screen, (160, 170, 200), rect, 2, border_radius=16)

        title = self.font_big.render("🏆 Winner!", True, (35, 45, 80))
        name  = self.font_big.render(self.winner, True, (35, 45, 80))
        hint1 = self.font.render("R = Restart   M = Menu   ESC = Quit", True, (60, 70, 100))

        self.screen.blit(title, title.get_rect(center=(rect.centerx, rect.top + 55)))
        self.screen.blit(name,  name.get_rect(center=(rect.centerx, rect.top + 95)))
        self.screen.blit(hint1, hint1.get_rect(center=(rect.centerx, rect.bottom - 40)))

    # ---------- loop ----------
    def run(self):
        while self.running:
            self.handle_events()

            if self.state == STATE_MENU:
                self.draw_menu()
            else:
                self.board.draw(self.screen)         # กระดานชิดซ้าย
                if hasattr(self.board, "draw_links"):
                    self.board.draw_links(self.screen)  # งู/บันได
                self.draw_players()
                self.draw_sidebar()
                self.draw_win_popup()                # ป๊อปอัปผู้ชนะ

            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()

