# -*- coding: utf-8 -*-
import pygame
import resources as R
import config as C

def idx_to_rc(idx):
    i = idx - 1
    row_from_bottom = i // R.GRID
    col_in_row = i % R.GRID
    row = R.GRID - 1 - row_from_bottom
    col = col_in_row if row_from_bottom % 2 == 0 else R.GRID - 1 - col_in_row
    return row, col

def cell_center(row, col):
    x = R.ORIGIN[0] + col * R.CELL + R.CELL//2
    y = R.ORIGIN[1] + row * R.CELL + R.CELL//2
    return x, y

def draw_board(screen):
    pygame.draw.rect(screen, C.COL_CARD, R.BOARD_RECT.inflate(20,20), border_radius=20)
    pygame.draw.rect(screen, C.COL_BORDER, R.BOARD_RECT.inflate(20,20), width=1, border_radius=20)
    if R.BOARD_IMG is not None:
        screen.blit(R.BOARD_IMG, R.BOARD_RECT.topleft)
    else:
        for r in range(R.GRID):
            for c in range(R.GRID):
                rect = pygame.Rect(R.ORIGIN[0]+c*R.CELL, R.ORIGIN[1]+r*R.CELL, R.CELL, R.CELL)
                col = (250,252,255) if (r+c)%2==0 else (235,240,255)
                pygame.draw.rect(screen, col, rect)
                pygame.draw.rect(screen, (210,215,235), rect, width=1)
        for idx in range(1, R.GRID*R.GRID + 1):
            r,c = idx_to_rc(idx)
            screen.blit(R.font_xs().render(str(idx), True, C.COL_SUBT),
                        (R.ORIGIN[0]+c*R.CELL+4, R.ORIGIN[1]+r*R.CELL+3))

def draw_players(screen, positions, colors, override=None):
    offset_map = {
        1: [(0,0)],
        2: [(-R.CELL//6, 0), (R.CELL//6, 0)],
        3: [(-R.CELL//6, -R.CELL//6), (R.CELL//6, -R.CELL//6), (0, R.CELL//6)],
        4: [(-R.CELL//6, -R.CELL//6), (R.CELL//6, -R.CELL//6), (-R.CELL//6, R.CELL//6), (R.CELL//6, R.CELL//6)],
    }
    radius = max(8, R.CELL//3)
    n = len(positions)
    offsets = offset_map.get(n, offset_map[4])
    for i, pos in enumerate(positions):
        if override and i == override.get("i"):
            x, y = override.get("xy")
            pygame.draw.circle(screen, colors[i], (int(x), int(y)), radius)
            continue
        r, c = idx_to_rc(pos)
        cx, cy = cell_center(r, c)
        ox, oy = offsets[i % len(offsets)]
        pygame.draw.circle(screen, colors[i], (cx+ox, cy+oy), radius)
