# -*- coding: utf-8 -*-
from dataclasses import dataclass, field
import config as C

STATE_START = "start"
STATE_NAME  = "name"
STATE_GAME  = "game"

@dataclass
class GameState:
    state: str = STATE_START
    player_count: int = 2
    names: list = field(default_factory=lambda: ["ผู้เล่น 1", "ผู้เล่น 2"])
    colors: list = field(default_factory=lambda: C.COL_P[:2])
    positions: list = field(default_factory=lambda: [1, 1])
    current_turn: int = 0
    dice_value: int | None = None
    message: str = "ยินดีต้อนรับสู่บันไดงู!"
    winner: int | None = None
    # ข้อมูลบอร์ดที่เลือก
    board_name: str = "Default"
    ladders: dict = field(default_factory=dict)
    snakes: dict = field(default_factory=dict)

    def reset_runtime(self):
        self.positions = [1]*self.player_count
        self.colors    = C.COL_P[:self.player_count]
        self.current_turn = 0
        self.dice_value = None
        self.winner = None
        self.message = "กด Space/Enter หรือคลิกปุ่ม เพื่อทอยเต๋า"

def move_player(positions, idx, steps, ladders: dict, snakes: dict, exact_win: bool):
    start = positions[idx]
    target = start + steps
    if exact_win:
        if target > 100: return start
        elif target == 100: return 100
    else:
        if target >= 100: return 100
    dest = target
    if dest in ladders: dest = ladders[dest]
    elif dest in snakes: dest = snakes[dest]
    return dest
