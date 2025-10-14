# -*- coding: utf-8 -*-
import pygame
import config as C
import resources as R
from ui import draw_background, draw_button

def draw_start_screen(screen):
    draw_background(screen)
    title = R.font_xxl().render("Snakes & Ladders", True, C.COL_TEXT)
    subtitle = R.font_md().render("เลือกจำนวนผู้เล่น", True, C.COL_SUBT)
    screen.blit(title, (C.W//2 - title.get_width()//2, 120))
    screen.blit(subtitle, (C.W//2 - subtitle.get_width()//2, 180))

    btns = []
    btn_w, btn_h, gap = 200, 64, 24
    total_w = btn_w*3 + gap*2
    x0 = C.W//2 - total_w//2; y0 = 260
    labels = ["2 ผู้เล่น", "3 ผู้เล่น", "4 ผู้เล่น"]
    for i, lab in enumerate(labels, start=2):
        rect = pygame.Rect(x0 + (i-2)*(btn_w+gap), y0, btn_w, btn_h)
        hover = rect.collidepoint(pygame.mouse.get_pos())
        draw_button(screen, rect, lab, R.font_md(), hover)
        btns.append((rect, i))
    pygame.display.flip()
    return btns
