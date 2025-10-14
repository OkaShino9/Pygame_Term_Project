# -*- coding: utf-8 -*-
import random
import pygame
from board import idx_to_rc, cell_center

def animate_dice_roll(clock, draw_frame, duration_ms=450, fps=25):
    frames = max(6, int(duration_ms*fps/1000))
    for _ in range(frames):
        temp = random.randint(1, 6)
        draw_frame(temp_dice=temp)
        clock.tick(fps)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); raise SystemExit

def compute_move_path(start_idx: int, steps: int, ladders: dict, snakes: dict):
    if steps <= 0: return []
    path = []
    for k in range(1, steps+1):
        nxt = start_idx + k
        if nxt >= 100:
            path.append(100)
            break
        path.append(nxt)
    if path:
        last = path[-1]
        if last in ladders: path.append(ladders[last])
        elif last in snakes: path.append(snakes[last])
    return path

def animate_token_move(clock, screen, gs, player_index: int, path_indices: list, draw_static_frame, fps=60, hop_frames=12):
    if not path_indices: return
    from_idx = gs.positions[player_index]
    seq = [from_idx] + path_indices
    for j in range(1, len(seq)):
        a = seq[j-1]; b = seq[j]
        ar, ac = idx_to_rc(a); br, bc = idx_to_rc(b)
        x0, y0 = cell_center(ar, ac); x1, y1 = cell_center(br, bc)
        frames = hop_frames
        is_jump = (j == len(seq)-1) and (seq[-2] in gs.ladders or seq[-2] in gs.snakes)
        if is_jump: frames = max(8, hop_frames // 2)
        for t in range(frames):
            u = (t + 1) / frames
            uu = 2*u*u if u < 0.5 else -1 + (4 - 2*u)*u
            x = x0 + (x1 - x0) * uu
            y = y0 + (y1 - y0) * uu
            draw_static_frame(override={"i": player_index, "xy": (x, y)})
            clock.tick(fps)
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
