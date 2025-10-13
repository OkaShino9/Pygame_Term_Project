import os, math
import pygame
from typing import Dict, Tuple, Optional, List
from config import (
    W, H, COLS, ROWS, CELL, MARGIN,
    COL_BG, COL_A, COL_B, COL_GRID, COL_TEXT,
    COL_SNAKE, COL_LADDER
)


class Board:
    """กระดาน + mapping ช่อง + วาดงูเป็นตัว (รูปภาพ) และบันไดเป็นเส้น"""
    def __init__(self, snakes_ladders: Optional[Dict[int, int]] = None):
        self.cols, self.rows = COLS, ROWS
        self.cell, self.margin = CELL, MARGIN
        self.map: Dict[int, Tuple[int, int]] = self._build_places()
        self.snakes_ladders = snakes_ladders or {}
        font_px = max(14, int(self.cell * 0.22))
        self.font = pygame.font.SysFont(None, font_px)

        # โหลดรูปงู (ไม่มีก็ fallback เป็นเส้นสี)
        self.snake_body_img, self.snake_head_img = self._load_snake_assets()

    # ---------- assets ----------
    def _load_snake_assets(self):
        body = head = None
        body_path = os.path.join("assets", "snake_body.png")
        head_path = os.path.join("assets", "snake_head.png")
        if os.path.exists(body_path):
            body = pygame.image.load(body_path).convert_alpha()
        if os.path.exists(head_path):
            head = pygame.image.load(head_path).convert_alpha()
        return body, head

    # ---------- core mapping ----------
    def _build_places(self) -> Dict[int, Tuple[int, int]]:
        places: Dict[int, Tuple[int, int]] = {}
        n = 1
        for r in range(self.rows):  # r=0 แถวล่าง
            y = H - self.margin - self.cell - r * self.cell
            cols_range = range(self.cols) if r % 2 == 0 else range(self.cols - 1, -1, -1)
            for c in cols_range:
                x = self.margin + c * self.cell
                places[n] = (x, y)
                n += 1
        return places

    def get_xy(self, cell: int) -> Tuple[int, int]:
        return self.map[cell]

    def _cell_center(self, cell: int) -> Tuple[int, int]:
        x, y = self.map[cell]
        return x + self.cell // 2, y + self.cell // 2

    def apply_snake_ladder(self, cell: int) -> int:
        return self.snakes_ladders.get(cell, cell)

    # ---------- drawing board ----------
    def draw(self, surface: pygame.Surface):
        surface.fill(COL_BG)
        total = self.rows * self.cols
        for n in range(1, total + 1):
            x, y = self.map[n]
            c = (x - self.margin) // self.cell
            r = (H - self.margin - self.cell - y) // self.cell
            fill = COL_A if (r + c) % 2 == 0 else COL_B
            pygame.draw.rect(surface, fill,  (x, y, self.cell, self.cell))
            pygame.draw.rect(surface, COL_GRID, (x, y, self.cell, self.cell), 2)
            surface.blit(self.font.render(str(n), True, COL_TEXT), (x + 6, y + 6))

    # ---------- drawing snakes/ladders ----------
    def draw_links(self, surface: pygame.Surface):
        for start, end in self.snakes_ladders.items():
            if start not in self.map or end not in self.map or start == end:
                continue
            p0 = self._cell_center(start)
            p2 = self._cell_center(end)
            is_ladder = end > start

            # control point สำหรับความโค้ง (ตั้งฉากจากเส้นหลัก)
            mx, my = (p0[0] + p2[0]) / 2, (p0[1] + p2[1]) / 2
            vx, vy = (p2[0] - p0[0]), (p2[1] - p0[1])
            nx, ny = -vy, vx
            length = math.hypot(nx, ny) or 1.0
            nx, ny = nx / length, ny / length
            curve = 0.18 * math.hypot(vx, vy)
            p1 = (mx + nx * curve, my + ny * curve)

            pts = self._quadratic_bezier(p0, p1, p2, steps=36)

            if is_ladder:
                # วาดบันไดแบบเส้นสีเขียว (เหมือนเดิม)
                pygame.draw.lines(surface, (0, 0, 0), False, pts, 8)
                pygame.draw.lines(surface, COL_LADDER, False, pts, 6)
                self._arrow_head(surface, pts[-2], pts[-1], COL_LADDER)
            else:
                # วาดงูเป็นตัว: ถ้ามีรูป ใช้รูป; ไม่งั้นวาดเส้นสีแดงเดิม
                if self.snake_body_img and self.snake_head_img:
                    self._draw_snake(surface, pts)
                else:
                    pygame.draw.lines(surface, (0, 0, 0), False, pts, 8)
                    pygame.draw.lines(surface, COL_SNAKE, False, pts, 6)
                    self._arrow_head(surface, pts[-2], pts[-1], COL_SNAKE)

    # ---------- snake drawing helpers ----------
    def _draw_snake(self, surface: pygame.Surface, pts: List[Tuple[int, int]]):
        """
        วาดงูด้วยการวางชิ้นส่วนลำตัว (snake_body.png) ทีละช่วง
        ตามทิศทางของเส้นโค้ง และวางหัวงู (snake_head.png) ที่ปลายทาง
        """
        # ขนาดเป้าหมายของชิ้นลำตัวสัมพันธ์กับขนาดช่อง
        target_h = max(12, int(self.cell * 0.35))  # ความหนาลำตัว
        # ระยะห่างระหว่างชิ้นลำตัว (ยิ่งน้อยยิ่งถี่)
        spacing = max(10, int(self.cell * 0.30))

        # เตรียมลิสต์ "จุดตามระยะทาง" บนเส้น
        samples = self._sample_along_polyline(pts, step=spacing)

        # วาดเงางูเบา ๆ ก่อน
        for i in range(len(samples) - 1):
            (x1, y1), (x2, y2) = samples[i], samples[i + 1]
            ang = math.atan2(y2 - y1, x2 - x1)
            seg_len = max(1, int(math.hypot(x2 - x1, y2 - y1)))
            # สร้างสี่เหลี่ยมเป็นเงา
            rect_surf = pygame.Surface((seg_len, target_h), pygame.SRCALPHA)
            pygame.draw.rect(rect_surf, (0, 0, 0, 70), (0, 0, seg_len, target_h), border_radius=target_h // 2)
            rot = pygame.transform.rotate(rect_surf, -math.degrees(ang))
            surface.blit(rot, rot.get_rect(center=((x1 + x2)//2 + 2, (y1 + y2)//2 + 3)))

        # วาดลำตัวงูจากรูป
        for i in range(len(samples) - 1):
            (x1, y1), (x2, y2) = samples[i], samples[i + 1]
            ang = math.atan2(y2 - y1, x2 - x1)
            seg_len = max(1, int(math.hypot(x2 - x1, y2 - y1)))

            # ปรับขนาดรูป body ให้ยาวเท่าช่วง และสูง = target_h
            body_scaled = pygame.transform.smoothscale(self.snake_body_img, (seg_len, target_h))
            body_rot = pygame.transform.rotate(body_scaled, -math.degrees(ang))
            surface.blit(body_rot, body_rot.get_rect(center=((x1 + x2)//2, (y1 + y2)//2)))

        # วางหัวงูที่ปลายสุด (ชี้ไปทางทิศปลาย)
        if len(samples) >= 2:
            (px, py), (qx, qy) = samples[-2], samples[-1]
            ang = math.atan2(qy - py, qx - px)
            head_w = int(target_h * 1.2)
            head_h = int(target_h * 1.2)
            head_scaled = pygame.transform.smoothscale(self.snake_head_img, (head_w, head_h))
            head_rot = pygame.transform.rotate(head_scaled, -math.degrees(ang))
            surface.blit(head_rot, head_rot.get_rect(center=(qx, qy)))

    @staticmethod
    def _sample_along_polyline(pts: List[Tuple[int, int]], step: int) -> List[Tuple[int, int]]:
        """คืนชุดจุดตาม polyline โดยคั่นทุกๆ ระยะ step พิกเซล"""
        if not pts:
            return []
        out = [pts[0]]
        acc = 0.0
        for i in range(1, len(pts)):
            x1, y1 = pts[i - 1]
            x2, y2 = pts[i]
            seg = math.hypot(x2 - x1, y2 - y1)
            if seg == 0:
                continue
            dx, dy = (x2 - x1) / seg, (y2 - y1) / seg
            while acc + step <= seg:
                acc += step
                out.append((int(x1 + dx * acc), int(y1 + dy * acc)))
            acc = (acc + 0.0001) - seg  # คงเศษระยะเล็กน้อย
        if out[-1] != pts[-1]:
            out.append(pts[-1])
        return out

    # ---------- math helpers ----------
    @staticmethod
    def _quadratic_bezier(p0, p1, p2, steps=20) -> List[Tuple[int,int]]:
        pts: List[Tuple[int, int]] = []
        for i in range(steps + 1):
            t = i / steps
            a = (1 - t) * (1 - t)
            b = 2 * (1 - t) * t
            c = t * t
            x = a * p0[0] + b * p1[0] + c * p2[0]
            y = a * p0[1] + b * p1[1] + c * p2[1]
            pts.append((int(x), int(y)))
        return pts

    @staticmethod
    def _arrow_head(surface, p_from, p_to, color):
        dx, dy = (p_to[0] - p_from[0], p_to[1] - p_from[1])
        ang = math.atan2(dy, dx)
        size = 12
        left = (p_to[0] - size * math.cos(ang - math.pi/6),
                p_to[1] - size * math.sin(ang - math.pi/6))
        right = (p_to[0] - size * math.cos(ang + math.pi/6),
                 p_to[1] - size * math.sin(ang + math.pi/6))
        pygame.draw.polygon(surface, color, [p_to, left, right])
        pygame.draw.polygon(surface, (0,0,0), [p_to, left, right], 1)
