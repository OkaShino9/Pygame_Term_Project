# -*- coding: utf-8 -*-
import sys, random
import pygame

import config as C
import resources as R
from boards import load_all_boards, pick_board
from state import GameState, STATE_START, STATE_NAME, STATE_GAME, move_player
from screens.start_screen import draw_start_screen
from screens.name_screen import draw_name_entry, build_name_fields
from screens.game_screen import draw_game_screen
from effects import animate_dice_roll, compute_move_path, animate_token_move

def apply_board_to_runtime(gs: GameState, board_spec):
    R.apply_board(grid=board_spec.grid, image_path=board_spec.image_path, cell_override=board_spec.cell_override)
    gs.board_name = board_spec.name
    gs.ladders = board_spec.ladders
    gs.snakes  = board_spec.snakes

def choose_board_if_needed(gs: GameState, all_boards):
    if not all_boards:
        class _Fallback:
            name="Fallback"; grid=C.GRID_DEFAULT; ladders={}; snakes={}
            image_path=C.BOARD_IMG_FALLBACK; cell_override=None
        apply_board_to_runtime(gs, _Fallback()); return
    b = pick_board(all_boards) if C.SHUFFLE_EACH_GAME or gs.board_name=="Default" else all_boards[0]
    apply_board_to_runtime(gs, b)

def animate_and_apply_roll(clock, screen, gs: GameState):
    final = random.randint(1, 6)
    def frame_cb(temp_dice=None): draw_game_screen(screen, gs, temp_dice=temp_dice)
    animate_dice_roll(clock, frame_cb)
    start_idx = gs.positions[gs.current_turn]
    path = compute_move_path(start_idx, final, gs.ladders, gs.snakes)
    def draw_with_override(override=None): draw_game_screen(screen, gs, moving_override=override)
    animate_token_move(clock, screen, gs, gs.current_turn, path, draw_with_override, fps=60, hop_frames=12)
    newpos = move_player(gs.positions, gs.current_turn, final, gs.ladders, gs.snakes, C.EXACT_WIN)
    gs.positions[gs.current_turn] = newpos
    gs.dice_value = final
    gs.message = f"{gs.names[gs.current_turn]} เดิน {final} ช่อง"
    if newpos == 100: gs.winner = gs.current_turn
    else: gs.current_turn = (gs.current_turn + 1) % gs.player_count

def main():
    pygame.init()
    screen = pygame.display.set_mode((C.W, C.H))
    pygame.display.set_caption("Snakes & Ladders — Multi-Board")
    clock = pygame.time.Clock()

    R.init_resources()
    gs = GameState()

    all_boards = load_all_boards()
    choose_board_if_needed(gs, all_boards)

    start_buttons = []; fields_name = []
    running = True
    while running:
        clock.tick(C.FPS)
        if gs.state == STATE_START:
            start_buttons = draw_start_screen(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for rect, n in start_buttons:
                        if rect.collidepoint(event.pos):
                            gs.player_count = n
                            gs.names = [f"ผู้เล่น {i+1}" for i in range(gs.player_count)]
                            gs.colors = C.COL_P[:gs.player_count]
                            fields_name = build_name_fields(gs.player_count)
                            gs.state = STATE_NAME
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

        elif gs.state == STATE_NAME:
            start_btn = draw_name_entry(screen, gs, fields_name)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                for fld in fields_name: fld.handle(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if start_btn.collidepoint(event.pos):
                        for i in range(gs.player_count):
                            n = fields_name[i].text.strip() or f"ผู้เล่น {i+1}"
                            gs.names[i] = n
                        gs.reset_runtime()
                        if C.SHUFFLE_EACH_GAME: choose_board_if_needed(gs, all_boards)
                        gs.state = STATE_GAME
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    gs.state = STATE_START

        elif gs.state == STATE_GAME:
            btn_rect = draw_game_screen(screen, gs)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                if event.type == pygame.KEYDOWN:
                    if gs.winner is not None:
                        if event.key == pygame.K_r:
                            gs.reset_runtime()
                            if C.SHUFFLE_EACH_GAME: choose_board_if_needed(gs, all_boards)
                        elif event.key == pygame.K_ESCAPE: running = False
                    else:
                        if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                            animate_and_apply_roll(clock, screen, gs)
                    if event.key == pygame.K_r and gs.winner is None:
                        gs.reset_runtime()
                        if C.SHUFFLE_EACH_GAME: choose_board_if_needed(gs, all_boards)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and gs.winner is None:
                    if btn_rect.collidepoint(event.pos): animate_and_apply_roll(clock, screen, gs)
        else:
            gs.state = STATE_START

    pygame.quit(); sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback; traceback.print_exc()
        pygame.quit(); raise
