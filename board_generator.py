import pygame
import random
import math
import numpy as np
from pathlib import Path

# --- Base Class for Board Items ---
class BoardItem:
    """Base class for items on the board like snakes and ladders."""
    def __init__(self, start_cell, end_cell):
        self.start_cell = start_cell
        self.end_cell = end_cell

    def draw(self, surface, generator):
        """Placeholder for drawing method."""
        raise NotImplementedError

# --- Snake Class ---
class Snake(BoardItem):
    """Represents a single snake on the board."""
    def __init__(self, start_cell, end_cell, definition, curve, pattern):
        super().__init__(start_cell, end_cell)
        self.definition = definition
        self.curve = curve
        self.pattern = pattern
        self.head_image = None

    def draw(self, surface, generator):
        """Draw the snake on the given surface."""
        if not self.head_image:
            self.head_image = generator.load_snake_head(
                self.definition["head_path"], self.definition["colors"][0]
            )
        generator.draw_snake(surface, self.curve, self.definition["colors"], self.head_image, self.pattern)
        if generator.SHOW_START_END_POINTS:
            end_pos = self.curve[-1]
            pygame.draw.circle(surface, (255, 255, 255), end_pos, 8)
            pygame.draw.circle(surface, (255, 200, 0), end_pos, 6)

# --- Ladder Class ---
class Ladder(BoardItem):
    """Represents a single ladder on the board."""
    def __init__(self, start_cell, end_cell, color):
        super().__init__(start_cell, end_cell)
        self.color = color

    def draw(self, surface, generator):
        """Draw the ladder on the given surface."""
        p1 = generator.grid_to_pixel(self.start_cell)
        p2 = generator.grid_to_pixel(self.end_cell)
        generator.draw_solid_ladder(surface, p1, p2, generator.darken(self.color, 0.8), self.color)
        if generator.SHOW_START_END_POINTS:
            pygame.draw.circle(surface, (255, 255, 255), p1, 8)
            pygame.draw.circle(surface, (0, 200, 0), p1, 6)
            pygame.draw.circle(surface, (255, 255, 255), p2, 8)
            pygame.draw.circle(surface, (0, 100, 255), p2, 6)

# --- Board Generator Class ---
class BoardGenerator:
    def __init__(self, cell_size=60, grid_size=10, margin=50):
        pygame.init()

        # --- Setup ---
        self.CELL_SIZE = cell_size
        self.GRID_SIZE = grid_size
        self.MARGIN = margin
        self.WIDTH = self.CELL_SIZE * self.GRID_SIZE + self.MARGIN * 2
        self.HEIGHT = self.CELL_SIZE * self.GRID_SIZE + self.MARGIN * 2
        self.BASE_DIR = Path(__file__).resolve().parent

        # --- Colors & Pattern ---
        self.PASTEL_COLORS = [
            (255, 182, 193), (173, 216, 230), (255, 255, 153),
            (152, 251, 152), (221, 160, 221), (255, 204, 153)
        ]
        self.SNAKE_DEFINITIONS = [
            {"colors": ((132, 0, 190), (155, 27, 235)), "head_path": "assets/snake/snake_head_484px_purple.png"},
            {"colors": ((0, 121, 190), (27, 176, 235)), "head_path": "assets/snake/snake_head_484px_blue.png"},
            {"colors": ((190, 170, 0), (235, 196, 27)), "head_path": "assets/snake/snake_head_484px_yellow.png"},
            {"colors": ((190, 28, 0), (235, 41, 27)), "head_path": "assets/snake/snake_head_484px_red.png"},
            {"colors": ((129, 189, 0), (187, 235, 27)), "head_path": "assets/snake/snake_head_484px_green.png"},
        ]
        self.SNAKE_PATTERN_SIZE_MULTIPLIER = 0.95
        self.SNAKE_STRIPE_HEIGHT = 8
        self.SNAKE_MAX_OUTLINE = 18
        self.SNAKE_MIN_OUTLINE = 10
        self.SNAKE_MAX_INNER = 14
        self.SNAKE_MIN_INNER = 6
        self.LADDER_RAIL_THICKNESS = 6
        self.LADDER_RUNG_THICKNESS = 4

        # --- Balance & Distribution Controls ---
        self.EXCLUSION_ZONE_RADIUS = 2
        self.SNAKE_MIN_BODY_DISTANCE = 30
        self.MAX_CURVE_GENERATION_ATTEMPTS = 10
        self.MIN_SNAKES_TO_GENERATE = 8
        self.MAX_SNAKES_TO_GENERATE = 10
        self.MIN_LADDERS_TO_GENERATE = 8
        self.MAX_LADDERS_TO_GENERATE = 10
        self.MAX_ITEM_LENGTH_CELLS = 20
        self.MIN_ITEM_LENGTH_CELLS = 10
        self.SNAKE_MAX_X_DISTANCE_CELLS = 5
        self.LADDER_MAX_X_DISTANCE_CELLS = 5

        # --- On/Off Switches ---
        self.SHOW_START_END_POINTS = False
        self.LADDER_ON_TOP = False

        # --- Quadrant Constants for Distribution ---
        self.TOP_LEFT, self.TOP_RIGHT, self.BOTTOM_LEFT, self.BOTTOM_RIGHT = 0, 1, 2, 3
        self.FORBIDDEN_CELLS = {1, 2, 3, 99, 100}

        # --- Caching ---
        self.BASE_HEAD_SIZE = 50
        self.SNAKE_HEAD_CACHE: dict[str, pygame.Surface] = {}

    def darken(self, color, factor=0.7):
        return tuple(max(0, int(c * factor)) for c in color)

    def load_snake_head(self, rel_path: str, fallback_color: tuple[int, int, int]) -> pygame.Surface:
        if rel_path in self.SNAKE_HEAD_CACHE:
            return self.SNAKE_HEAD_CACHE[rel_path]
        abs_path = self.BASE_DIR / rel_path
        try:
            img = pygame.image.load(abs_path.as_posix())
            if pygame.display.get_surface():
                img = img.convert_alpha()
            head = pygame.transform.smoothscale(img, (self.BASE_HEAD_SIZE, self.BASE_HEAD_SIZE))
        except Exception as exc:
            print(f"[snake-head] warning ({abs_path}): {exc}")
            head = pygame.Surface((self.BASE_HEAD_SIZE, self.BASE_HEAD_SIZE), pygame.SRCALPHA)
            head.fill(fallback_color)
        self.SNAKE_HEAD_CACHE[rel_path] = head
        return head

    def draw_board(self, target_surface=None):
        surface = target_surface if target_surface is not None else pygame.Surface((self.WIDTH, self.HEIGHT))
        pastel_len = len(self.PASTEL_COLORS)
        def lighten(color, factor=0.6):
            return tuple(int(c + (255 - c) * factor) for c in color)
        for row in range(self.GRID_SIZE):
            for col in range(self.GRID_SIZE):
                x, y = self.MARGIN + col * self.CELL_SIZE, self.MARGIN + row * self.CELL_SIZE
                base_color = self.PASTEL_COLORS[(row * self.GRID_SIZE + col) % pastel_len]
                color = lighten(base_color, 0.6)
                pygame.draw.rect(surface, color, (x, y, self.CELL_SIZE, self.CELL_SIZE))
                row_from_bottom = self.GRID_SIZE - 1 - row
                cell_num = (row_from_bottom * self.GRID_SIZE) + (col + 1 if row_from_bottom % 2 == 0 else self.GRID_SIZE - col)
                try: font = pygame.font.SysFont("ArcadeClassic", 28)
                except Exception: font = pygame.font.Font(None, 24)
                text = font.render(str(cell_num), True, (80, 80, 80))
                text_rect = text.get_rect(center=(x + self.CELL_SIZE/2, y + self.CELL_SIZE/2))
                surface.blit(text, text_rect)
        return surface

    def grid_to_pixel(self, cell_number):
        cell_number -= 1
        row = self.GRID_SIZE - 1 - (cell_number // self.GRID_SIZE)
        row_from_bottom = self.GRID_SIZE - 1 - row
        col = cell_number % self.GRID_SIZE if row_from_bottom % 2 == 0 else self.GRID_SIZE - 1 - (cell_number % self.GRID_SIZE)
        x = self.MARGIN + col * self.CELL_SIZE + self.CELL_SIZE // 2
        y = self.MARGIN + row * self.CELL_SIZE + self.CELL_SIZE // 2
        return x, y

    def draw_solid_ladder(self, surf, p1, p2, rails_color, rungs_color):
        (x1, y1), (x2, y2) = p1, p2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)
        if dist < 10: return
        offset = 12
        perp = np.array([-dy / dist, dx / dist])
        p1, p2 = np.array(p1), np.array(p2)
        rail1_start, rail1_end = p1 + perp * offset, p2 + perp * offset
        rail2_start, rail2_end = p1 - perp * offset, p2 - perp * offset
        margin_ratio = 0.1
        start_t, end_t = margin_ratio, 1 - margin_ratio
        num_rungs = max(2, int(dist * (end_t - start_t) / 30))
        for i in range(num_rungs):
            t = start_t if num_rungs == 1 else start_t + i * (end_t - start_t) / (num_rungs - 1)
            center_point = p1 + np.array([dx*t, dy*t])
            rung_start, rung_end = center_point - perp * offset, center_point + perp * offset
            pygame.draw.line(surf, rungs_color, rung_start, rung_end, self.LADDER_RUNG_THICKNESS)
        pygame.draw.line(surf, rails_color, rail1_start, rail1_end, self.LADDER_RAIL_THICKNESS)
        pygame.draw.line(surf, rails_color, rail2_start, rail2_end, self.LADDER_RAIL_THICKNESS)

    def cell_to_grid(self, cell_number):
        if not 1 <= cell_number <= 100: return None
        cell_idx = cell_number - 1
        row_from_bottom = cell_idx // self.GRID_SIZE
        row = self.GRID_SIZE - 1 - row_from_bottom
        if row_from_bottom % 2 == 0: col = cell_idx % self.GRID_SIZE
        else: col = self.GRID_SIZE - 1 - (cell_idx % self.GRID_SIZE)
        return (row, col)

    def get_quadrant(self, cell_number):
        row, col = self.cell_to_grid(cell_number)
        is_top, is_left = row < self.GRID_SIZE / 2, col < self.GRID_SIZE / 2
        if is_top and is_left: return self.TOP_LEFT
        if is_top and not is_left: return self.TOP_RIGHT
        if not is_top and is_left: return self.BOTTOM_LEFT
        return self.BOTTOM_RIGHT

    def is_too_close(self, new_start, new_end, existing_items, radius):
        new_start_grid, new_end_grid = self.cell_to_grid(new_start), self.cell_to_grid(new_end)
        for exist_start, exist_end in existing_items:
            exist_start_grid, exist_end_grid = self.cell_to_grid(exist_start), self.cell_to_grid(exist_end)
            points_to_check = [
                (new_start_grid, exist_start_grid), (new_start_grid, exist_end_grid),
                (new_end_grid, exist_start_grid), (new_end_grid, exist_end_grid),
            ]
            for p1, p2 in points_to_check:
                if p1 is None or p2 is None: continue
                (r1, c1), (r2, c2) = p1, p2
                if max(abs(r1 - r2), abs(c1 - c2)) < radius: return True
        return False

    def generate_items_in_quadrants(self, num_items, item_type, all_used_points, existing_items_of_same_type, exclusion_radius):
        items, max_cell = [], self.GRID_SIZE * self.GRID_SIZE
        quadrants = [self.TOP_LEFT, self.TOP_RIGHT, self.BOTTOM_LEFT, self.BOTTOM_RIGHT]
        targets = (quadrants * (num_items // 4 + 1))[:num_items]
        random.shuffle(targets)
        for target_quadrant in targets:
            attempts = 300
            while attempts > 0:
                attempts -= 1
                if item_type == 'snake':
                    start_range, end_range = (20, max_cell - 1), (2, max_cell - 20)
                    start, end = random.randint(*start_range), random.randint(*end_range)
                    if start <= end: continue
                    start_grid, end_grid = self.cell_to_grid(start), self.cell_to_grid(end)
                    if start_grid and end_grid:
                        (r1, c1), (r2, c2) = start_grid, end_grid
                        if abs(c1 - c2) > self.SNAKE_MAX_X_DISTANCE_CELLS:
                            continue
                        if max(abs(r1 - r2), abs(c1 - c2)) < self.EXCLUSION_ZONE_RADIUS:
                            continue
                else: # 'ladder'
                    start_range, end_range = (2, max_cell - 20), (20, 90)
                    start, end = random.randint(*start_range), random.randint(*end_range)
                    if start >= end: continue
                    start_grid, end_grid = self.cell_to_grid(start), self.cell_to_grid(end)
                    if start_grid and end_grid:
                        (r1, c1), (r2, c2) = start_grid, end_grid
                        if abs(c1 - c2) > self.LADDER_MAX_X_DISTANCE_CELLS:
                            continue
                        if max(abs(r1 - r2), abs(c1 - c2)) < self.EXCLUSION_ZONE_RADIUS:
                            continue
                length = abs(start - end)
                if not (self.MIN_ITEM_LENGTH_CELLS <= length <= self.MAX_ITEM_LENGTH_CELLS): continue
                if self.get_quadrant(start) != target_quadrant: continue
                if start in all_used_points or end in all_used_points or start in self.FORBIDDEN_CELLS or end in self.FORBIDDEN_CELLS: continue
                if self.is_too_close(start, end, existing_items_of_same_type, exclusion_radius): continue
                items.append((start, end)); existing_items_of_same_type.append((start, end))
                all_used_points.add(start); all_used_points.add(end)
                break
        return items

    def generate_random_positions(self, num_snakes, num_ladders, exclusion_radius):
        all_used_points = set()
        snakes = []
        ladders = []
        existing_items_of_same_type = []

        top_row_snakes_to_generate = 2
        attempts = 300
        while len(snakes) < top_row_snakes_to_generate and attempts > 0:
            attempts -= 1
            start = random.randint(91, 100)
            end = random.randint(2, 80)

            if start <= end: continue

            start_grid, end_grid = self.cell_to_grid(start), self.cell_to_grid(end)
            if start_grid and end_grid:
                (r1, c1), (r2, c2) = start_grid, end_grid
                if abs(c1 - c2) > self.SNAKE_MAX_X_DISTANCE_CELLS:
                    continue
                if max(abs(r1 - r2), abs(c1 - c2)) < self.EXCLUSION_ZONE_RADIUS:
                    continue
            
            length = abs(start - end)
            if not (self.MIN_ITEM_LENGTH_CELLS <= length <= self.MAX_ITEM_LENGTH_CELLS): continue
            if start in all_used_points or end in all_used_points or start in self.FORBIDDEN_CELLS or end in self.FORBIDDEN_CELLS: continue
            if self.is_too_close(start, end, snakes, exclusion_radius): continue

            snakes.append((start, end))
            all_used_points.add(start)
            all_used_points.add(end)
        
        existing_items_of_same_type.extend(snakes)

        remaining_snakes = num_snakes - len(snakes)
        snakes.extend(self.generate_items_in_quadrants(remaining_snakes, 'snake', all_used_points, existing_items_of_same_type, exclusion_radius))

        if num_ladders > 0:
            attempts = 300
            first_ladder_generated = False
            while attempts > 0 and not first_ladder_generated:
                attempts -= 1
                start = random.randint(4, 10)
                end = random.randint(20, 40)
                
                if start >= end: continue
                
                start_grid, end_grid = self.cell_to_grid(start), self.cell_to_grid(end)
                if start_grid and end_grid:
                    (r1, c1), (r2, c2) = start_grid, end_grid
                    if abs(c1 - c2) > self.LADDER_MAX_X_DISTANCE_CELLS:
                        continue
                else:
                    continue

                length = abs(start - end)
                if not (self.MIN_ITEM_LENGTH_CELLS <= length <= self.MAX_ITEM_LENGTH_CELLS): continue
                if start in all_used_points or end in all_used_points or start in self.FORBIDDEN_CELLS or end in self.FORBIDDEN_CELLS: continue
                if self.is_too_close(start, end, ladders, exclusion_radius): continue

                ladders.append((start, end))
                all_used_points.add(start)
                all_used_points.add(end)
                first_ladder_generated = True

        remaining_ladders = num_ladders - len(ladders)
        if remaining_ladders > 0:
            ladders.extend(self.generate_items_in_quadrants(remaining_ladders, 'ladder', all_used_points, ladders, exclusion_radius))
        
        return snakes, ladders

    def generate_snake_points(self, start_pos, end_pos):
        points = [start_pos]
        mid_x = (start_pos[0] + end_pos[0]) / 2 + random.randint(-self.CELL_SIZE, self.CELL_SIZE)
        mid_y = (start_pos[1] + end_pos[1]) / 2 + random.randint(-self.CELL_SIZE, self.CELL_SIZE)
        mid_x, mid_y = max(self.MARGIN, min(self.WIDTH - self.MARGIN, mid_x)), max(self.MARGIN, min(self.HEIGHT - self.MARGIN, mid_y))
        points.extend([(mid_x, mid_y), end_pos])
        while (len(points) - 1) % 3 != 0:
            t = random.random()
            x = start_pos[0] + (end_pos[0] - start_pos[0]) * t + random.randint(-self.CELL_SIZE//2, self.CELL_SIZE//2)
            y = start_pos[1] + (end_pos[1] - start_pos[1]) * t + random.randint(-self.CELL_SIZE//2, self.CELL_SIZE//2)
            points.insert(-1, (max(self.MARGIN, min(self.WIDTH - self.MARGIN, x)), max(self.MARGIN, min(self.HEIGHT - self.MARGIN, y))))
        return points

    def cubic_bezier(self, points, samples=60):
        if len(points) < 4: return points
        curve = []
        for i in range(0, len(points) - 3, 3):
            p0, p1, p2, p3 = points[i:i + 4]
            for t in np.linspace(0, 1, samples):
                x = (1 - t)**3 * p0[0] + 3*(1 - t)**2 * t * p1[0] + 3*(1 - t) * t**2 * p2[0] + t**3 * p3[0]
                y = (1 - t)**3 * p0[1] + 3*(1 - t)**2 * t * p1[1] + 3*(1 - t) * t**2 * p2[1] + t**3 * p3[1]
                curve.append((x, y))
        return curve if curve else points

    def generate_pattern_positions(self, curve):
        positions = []
        total_length = sum(math.hypot(curve[i+1][0] - curve[i][0], curve[i+1][1] - curve[i][1]) for i in range(len(curve) - 1))
        current_distance = 40 + random.randint(-10, 10)
        while current_distance < total_length - 40:
            positions.append(current_distance)
            current_distance += 25 + random.randint(-5, 10)
        return positions

    def do_curves_intersect(self, curve1, curve2, min_distance):
        for i in range(0, len(curve1), 5):
            for j in range(0, len(curve2), 5):
                p1, p2 = curve1[i], curve2[j]
                if math.hypot(p1[0] - p2[0], p1[1] - p2[1]) < min_distance:
                    return True
        return False

    def draw_snake(self, surf, curve, colors, head_img, pattern_positions):
        if len(curve) < 2: return

        color, pattern_color = colors
        
        n, taper_start_point = len(curve), 0.8 
        for i in range(n - 1):
            progress = i / (n - 1)
            taper_factor = max(0, (progress - taper_start_point) / (1.0 - taper_start_point)) ** 1.5 if progress > taper_start_point else 0.0
            outline_w, inner_w = int(self.SNAKE_MAX_OUTLINE - (self.SNAKE_MAX_OUTLINE - self.SNAKE_MIN_OUTLINE) * taper_factor), int(self.SNAKE_MAX_INNER - (self.SNAKE_MAX_INNER - self.SNAKE_MIN_INNER) * taper_factor)
            p0, p1 = curve[i], curve[i + 1]
            pygame.draw.line(surf, self.darken(color, 0.6), p0, p1, max(1, outline_w))
            pygame.draw.line(surf, color, p0, p1, max(1, inner_w))
        distance_traveled, pattern_idx = 0.0, 0
        for i in range(n - 1):
            p0, p1 = curve[i], curve[i + 1]
            segment_length = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
            while pattern_idx < len(pattern_positions) and distance_traveled < pattern_positions[pattern_idx] < distance_traveled + segment_length:
                ratio = (pattern_positions[pattern_idx] - distance_traveled) / segment_length
                pos_x, pos_y = p0[0] + (p1[0] - p0[0]) * ratio, p0[1] + (p1[1] - p0[1]) * ratio
                progress = i / (n - 1)
                taper_factor = max(0, (progress - taper_start_point) / (1.0 - taper_start_point)) ** 1.5 if progress > taper_start_point else 0.0
                current_inner_w = int(self.SNAKE_MAX_INNER - (self.SNAKE_MAX_INNER - self.SNAKE_MIN_INNER) * taper_factor)
                dx, dy = p1[0] - p0[0], p1[1] - p0[1]
                mag = segment_length if segment_length > 0 else 1
                dir_vec, perp_vec = np.array([dx / mag, dy / mag]), np.array([-dy / mag, dx / mag])
                center = np.array((pos_x, pos_y))
                half_w, half_h = (current_inner_w / 2) * self.SNAKE_PATTERN_SIZE_MULTIPLIER, self.SNAKE_STRIPE_HEIGHT / 2
                pt1, pt2 = center - (dir_vec * half_h) + (perp_vec * half_w), center + (dir_vec * half_h) + (perp_vec * half_w)
                pt3, pt4 = center + (dir_vec * half_h) - (perp_vec * half_w), center - (dir_vec * half_h) - (perp_vec * half_w)
                outline_color = self.darken(color, 0.5)
                pygame.draw.polygon(surf, pattern_color, [pt1, pt2, pt3, pt4])
                pygame.draw.polygon(surf, outline_color, [pt1, pt2, pt3, pt4], 2)
                pattern_idx += 1
            distance_traveled += segment_length
        head_pos, next_pos = curve[0], curve[1]
        dx, dy = next_pos[0] - head_pos[0], next_pos[1] - head_pos[1]
        angle = np.degrees(np.arctan2(-dy, dx)) - 90
        rotated_head = pygame.transform.rotate(head_img, angle)
        rect = rotated_head.get_rect(center=head_pos)
        surf.blit(rotated_head, rect)

    def generate_board_state(self):
        num_snakes_to_generate = np.random.randint(self.MIN_SNAKES_TO_GENERATE, self.MAX_SNAKES_TO_GENERATE + 1)
        num_ladders_to_generate = np.random.randint(self.MIN_LADDERS_TO_GENERATE, self.MAX_LADDERS_TO_GENERATE + 1)

        snake_positions, ladder_positions = self.generate_random_positions(
            num_snakes_to_generate, num_ladders_to_generate, self.EXCLUSION_ZONE_RADIUS
        )

        num_snakes = len(snake_positions)
        ladder_colors = [random.choice(self.PASTEL_COLORS) for _ in ladder_positions]

        snake_defs = []
        if num_snakes > 0:
            guaranteed_defs = list(self.SNAKE_DEFINITIONS)
            random.shuffle(guaranteed_defs)
            snake_defs.extend(guaranteed_defs[:min(num_snakes, len(guaranteed_defs))])
            remaining_slots = num_snakes - len(snake_defs)
            if remaining_slots > 0:
                snake_defs.extend(random.choices(self.SNAKE_DEFINITIONS, k=remaining_slots))
        random.shuffle(snake_defs)

        snakes = []
        snake_curves = []
        for i, (start_cell, end_cell) in enumerate(snake_positions):
            start_pos, end_pos = self.grid_to_pixel(start_cell), self.grid_to_pixel(end_cell)
            final_curve = None
            for _ in range(self.MAX_CURVE_GENERATION_ATTEMPTS):
                is_valid_curve = True
                points = self.generate_snake_points(start_pos, end_pos)
                new_curve = self.cubic_bezier(points)
                for existing_curve in snake_curves:
                    if self.do_curves_intersect(new_curve, existing_curve, self.SNAKE_MIN_BODY_DISTANCE):
                        is_valid_curve = False
                        break
                if is_valid_curve:
                    final_curve = new_curve
                    break
            final_curve = final_curve or new_curve 
            if final_curve:
                snake_curves.append(final_curve)
                pattern = self.generate_pattern_positions(final_curve)
                snakes.append(Snake(start_cell, end_cell, snake_defs[i], final_curve, pattern))

        ladders = [Ladder(start, end, ladder_colors[i]) for i, (start, end) in enumerate(ladder_positions)]

        return snakes, ladders

    def render_board_surface(
        self,
        snakes,
        ladders,
        *,
        draw_background=True,
        ladder_on_top=False,
        background_color=None,
        target_surface=None,
    ):
        surface = target_surface or pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
        if background_color is not None:
            surface.fill(background_color)
        elif target_surface is None:
            surface.fill((0, 0, 0, 0))

        if draw_background:
            self.draw_board(surface)

        if ladder_on_top:
            for snake in snakes:
                snake.draw(surface, self)
            for ladder in ladders:
                ladder.draw(surface, self)
        else:
            for ladder in ladders:
                ladder.draw(surface, self)
            for snake in snakes:
                snake.draw(surface, self)

        return surface

    def generate_space_board_assets(self):
        snakes, ladders = self.generate_board_state()
        board_surface = self.render_board_surface(
            snakes,
            ladders,
            draw_background=True,
            ladder_on_top=self.LADDER_ON_TOP,
            background_color=None,
        ).convert_alpha()

        grid_map = {cell: self.grid_to_pixel(cell) for cell in range(1, self.GRID_SIZE * self.GRID_SIZE + 1)}
        return board_surface, snakes, ladders, grid_map

def main():
    # --- Demo on how to use the BoardGenerator class ---
    GENERATE_BOARD_ON_STARTUP = True
    ENABLE_SPACEBAR_REGENERATION = True
    DRAW_BOARD_BACKGROUND = True
    LADDER_ON_TOP = False

    generator = BoardGenerator()
    pygame.display.set_caption("Snake & Ladder Board Generator")
    screen = pygame.display.set_mode((generator.WIDTH, generator.HEIGHT))
    clock = pygame.time.Clock()
    running = True

    if GENERATE_BOARD_ON_STARTUP:
        snakes, ladders = generator.generate_board_state()
    else:
        snakes, ladders = [], []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_SPACE
                and ENABLE_SPACEBAR_REGENERATION
            ):
                snakes, ladders = generator.generate_board_state()

        generator.render_board_surface(
            snakes,
            ladders,
            draw_background=DRAW_BOARD_BACKGROUND,
            ladder_on_top=LADDER_ON_TOP,
            background_color=(200, 200, 200),
            target_surface=screen,
        )
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
