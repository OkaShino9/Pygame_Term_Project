import pygame
from typing import Tuple
from config import CELL

class Player:
    def __init__(self, name: str, fill: Tuple[int,int,int], stroke: Tuple[int,int,int]):
        self.name = name
        self.fill = fill
        self.stroke = stroke
        self.pos = 1

    def move(self, steps: int, end_cell: int):
        # เดินไปข้างหน้า และถ้าเกินให้หยุดที่เส้นชัยเลย (เช่น 100)
        self.pos = min(self.pos + steps, end_cell)

    def jump_to(self, cell: int):
        self.pos = cell

    def draw(self, surface: pygame.Surface, board, offset=(0, 0)):
        x, y = board.get_xy(self.pos)
        cx = x + board.cell // 2 + offset[0]
        cy = y + board.cell // 2 + offset[1]
        r = max(10, int(board.cell * 0.28))  # รัศมีตามขนาดช่อง

        pygame.draw.circle(surface, (0, 0, 0), (cx + 2, cy + 3), r, 0)  # เงา
        pygame.draw.circle(surface, self.fill, (cx, cy), r, 0)          # ตัวหมาก
        pygame.draw.circle(surface, self.stroke, (cx, cy), r, 3)        # ขอบ
