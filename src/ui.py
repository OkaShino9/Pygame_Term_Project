# -*- coding: utf-8 -*-
import pygame
import config as C

def draw_vertical_gradient(surface, top, bot):
    h = surface.get_height()
    for y in range(h):
        t = y/(h-1 if h>1 else 1)
        c = (
            int(top[0]+(bot[0]-top[0])*t),
            int(top[1]+(bot[1]-top[1])*t),
            int(top[2]+(bot[2]-top[2])*t)
        )
        pygame.draw.line(surface, c, (0,y), (surface.get_width(), y))

def draw_background(screen):
    bg = pygame.Surface((C.W, C.H))
    draw_vertical_gradient(bg, C.COL_BG_TOP, C.COL_BG_BOT)
    screen.blit(bg, (0,0))

def draw_button(screen, rect, text, font, hover=False):
    color = C.COL_BTN_H if hover else C.COL_BTN
    pygame.draw.rect(screen, color, rect, border_radius=12)
    pygame.draw.rect(screen, (255,255,255,30), rect, width=2, border_radius=12)
    label = font.render(text, True, C.COL_BTN_TX)
    screen.blit(label, (rect.centerx - label.get_width()//2,
                        rect.centery - label.get_height()//2))

def draw_card(screen, rect, title=None, title_font=None, pad=16):
    shadow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA); shadow.fill(C.COL_SHADOW)
    screen.blit(shadow, (rect.x + 2, rect.y + 3))
    pygame.draw.rect(screen, C.COL_CARD, rect, border_radius=14)
    pygame.draw.rect(screen, C.COL_BORDER, rect, width=1, border_radius=14)
    if title and title_font:
        cap = title_font.render(title, True, C.COL_TEXT)
        screen.blit(cap, (rect.x + pad, rect.y + pad))
        return pygame.Rect(rect.x + pad, rect.y + pad + 28, rect.w - pad*2, rect.h - (pad*2 + 28))
    return pygame.Rect(rect.x + pad, rect.y + pad, rect.w - pad*2, rect.h - pad*2)

def draw_input_box(screen, rect, text, font, active=False, placeholder=""):
    pygame.draw.rect(screen, C.COL_CARD, rect, border_radius=10)
    pygame.draw.rect(screen, C.COL_BORDER, rect, width=2, border_radius=10)
    show = text if text else placeholder
    col = C.COL_TEXT if text else C.COL_SUBT
    surf = font.render(show, True, col)
    screen.blit(surf, (rect.x + 12, rect.y + (rect.h - surf.get_height())//2))
    if active:
        pygame.draw.rect(screen, C.COL_BTN, rect, width=2, border_radius=10)
