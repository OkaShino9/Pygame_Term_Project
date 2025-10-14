# -*- coding: utf-8 -*-
import pygame
import config as C
import resources as R
from ui import draw_background
from widgets import TextField

def build_name_fields(player_count):
    fields = []
    col_w = 420; total_w = col_w * player_count
    start_x = C.W//2 - total_w//2; top = 150
    for i in range(player_count):
        name_rect  = (start_x + i*col_w + 30, top + 70,  col_w - 60, 56)
        fields.append(TextField(name_rect, R.font_md(), placeholder=f"ชื่อผู้เล่น {i+1}", maxlen=20))
    return fields

def draw_name_entry(screen, gs, fields_name):
    draw_background(screen)
    title = R.font_xl().render("ตั้งชื่อผู้เล่น", True, C.COL_TEXT)
    screen.blit(title, (C.W//2 - title.get_width()//2, 70))

    top = 150; col_w = 420
    total_w = col_w * gs.player_count
    start_x = C.W//2 - total_w//2
    for i in range(gs.player_count):
        card = pygame.Rect(start_x + i*col_w + 10, top, col_w - 20, 160)
        pygame.draw.rect(screen, C.COL_CARD, card, border_radius=16)
        pygame.draw.rect(screen, C.COL_BORDER, card, width=1, border_radius=16)
        label = R.font_lg().render(f"ผู้เล่น {i+1}", True, C.COL_TEXT)
        screen.blit(label, (card.x + 16, card.y + 12))
        pygame.draw.circle(screen, C.COL_P[i], (card.right - 28, card.y + 28), 12)
        fields_name[i].draw(screen)

    btn = pygame.Rect(C.W//2 - 160, C.H - 120, 320, 60)
    from ui import draw_button
    draw_button(screen, btn, "เริ่มเกม", R.font_md(), hover=btn.collidepoint(pygame.mouse.get_pos()))
    pygame.display.flip()
    return btn
