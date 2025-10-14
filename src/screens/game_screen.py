# -*- coding: utf-8 -*-
import pygame
import config as C
import resources as R
from ui import draw_background, draw_card, draw_button
from board import draw_board, draw_players
from dice_utils import draw_dice

def draw_right_panel(screen, gs):
    x0 = (C.W - C.RIGHT_PANEL_W) + 12
    y = 16
    gap = 14

    # รายชื่อผู้เล่น
    card_players = pygame.Rect(x0, y, C.RIGHT_PANEL_W - 24, 240)
    inner = draw_card(screen, card_players, "ผู้เล่น", R.font_md())
    yy = inner.y
    for i, n in enumerate(gs.names):
        line_rect = pygame.Rect(inner.x, yy, inner.w, 44)
        if i == gs.current_turn:
            pygame.draw.rect(screen, (245, 248, 255), line_rect, border_radius=10)
            pygame.draw.rect(screen, C.COL_BORDER, line_rect, width=1, border_radius=10)
        pygame.draw.circle(screen, gs.colors[i], (line_rect.x + 14, line_rect.centery), 8)
        txt = R.font_md().render(n, True, C.COL_TEXT)
        screen.blit(txt, (line_rect.x + 32, line_rect.centery - txt.get_height()//2))
        yy += 46

    y += card_players.h + gap

    # ลูกเต๋า
    card_dice = pygame.Rect(x0, y, C.RIGHT_PANEL_W - 24, 220)
    inner = draw_card(screen, card_dice, "ลูกเต๋า", R.font_md())
    dice_area = pygame.Rect(inner.x, inner.y, inner.w, 120 + 16)

    # วาดลูกเต๋าและได้กล่องเต๋าคืนมา
    dice_box = draw_dice(screen, gs.dice_value, dice_area)

    # ปุ่มทอย: วางใต้กล่องเต๋า
    btn_rect = pygame.Rect(inner.x, dice_box.bottom + 16, inner.w, 48)
    hover = btn_rect.collidepoint(pygame.mouse.get_pos())
    draw_button(screen, btn_rect, "ทอยเต๋า (Space/Enter)", R.font_md(), hover)

    y += card_dice.h + gap

    # สถานะ
    card_msg = pygame.Rect(x0, y, C.RIGHT_PANEL_W - 24, 110)
    inner = draw_card(screen, card_msg, "สถานะ", R.font_md())
    msg = gs.message
    while R.font_md().size(msg)[0] > inner.w and len(msg) > 5:
        msg = msg[:-1]
    screen.blit(R.font_md().render(msg, True, C.COL_TEXT), (inner.x, inner.y))

    return btn_rect

def draw_game_screen(screen, gs, temp_dice=None, moving_override=None):
    draw_background(screen)
    draw_board(screen)
    draw_players(screen, gs.positions, gs.colors, override=moving_override)

    title = R.font_lg().render(f"เทิร์น: {gs.names[gs.current_turn]}  •  บอร์ด: {gs.board_name}", True, C.COL_TEXT)
    screen.blit(title, (20, 12))

    btn_rect = draw_right_panel(screen, gs)

    foot = R.font_xs().render("R = เริ่มใหม่ | Esc = ออก", True, C.COL_SUBT)
    screen.blit(foot, (20, C.H - foot.get_height() - 8))

    if gs.winner is not None:
        ov = pygame.Surface((C.W, C.H), pygame.SRCALPHA); ov.fill(C.COL_WIN_OV)
        screen.blit(ov, (0, 0))
        txt = R.font_xl().render(f"{gs.names[gs.winner]} ชนะ! 🏆", True, (255,255,255))
        sub = R.font_md().render("กด R เพื่อเริ่มใหม่ หรือ Esc เพื่อออก", True, (235,235,235))
        screen.blit(txt, (C.W//2 - txt.get_width()//2, C.H//2 - 40))
        screen.blit(sub, (C.W//2 - sub.get_width()//2, C.H//2 + 12))

    pygame.display.flip()
    return btn_rect
