import pygame
import random
import math
import numpy as np
import os

pygame.init()

# --- Setup ---
CELL_SIZE = 60
GRID_SIZE = 10
MARGIN = 50
WIDTH = CELL_SIZE * GRID_SIZE + MARGIN * 2
HEIGHT = CELL_SIZE * GRID_SIZE + MARGIN * 2

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake & Ladder Board Generator")
clock = pygame.time.Clock()

# --- Colors & Pattern ---
PASTEL_COLORS = [
    (255, 182, 193), (173, 216, 230), (255, 255, 153),
    (152, 251, 152), (221, 160, 221), (255, 204, 153)
]
SNAKE_FIXED_COLOR = (129, 189, 0)
SNAKE_PATTERN_COLOR = (187, 235, 27)
SNAKE_PATTERN_SIZE_MULTIPLIER = 0.95
SNAKE_STRIPE_HEIGHT = 8

# --- NEW: Ladder Thickness Controls ---
LADDER_RAIL_THICKNESS = 6
LADDER_RUNG_THICKNESS = 4

# --- Balance & Distribution Controls ---
EXCLUSION_ZONE_RADIUS = 2
SNAKE_MIN_BODY_DISTANCE = 30 
MAX_CURVE_GENERATION_ATTEMPTS = 10
MIN_SNAKES_TO_GENERATE = 7
MAX_SNAKES_TO_GENERATE = 10
MIN_LADDERS_TO_GENERATE = 7
MAX_LADDERS_TO_GENERATE = 10

# --- Quadrant Constants for Distribution ---
TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT = 0, 1, 2, 3


def darken(color, factor=0.7):
    return tuple(max(0, int(c * factor)) for c in color)

# --- Load Snake Head Image ---
try:
    snake_head_img = pygame.image.load("assets/snake/snake_head_484px_green.png").convert_alpha()
except pygame.error:
    print("Warning: snake_head_484px_green.png not found. Using a placeholder.")
    snake_head_img = pygame.Surface((55, 55), pygame.SRCALPHA)
    pygame.draw.circle(snake_head_img, (0, 255, 0), (27, 27), 27)

BASE_HEAD_SIZE = 55
snake_head_img = pygame.transform.scale(snake_head_img, (BASE_HEAD_SIZE, BASE_HEAD_SIZE))

def colorize_head(head_img, new_color):
    colored_head = head_img.copy()
    arr = pygame.surfarray.pixels3d(colored_head)
    is_green = (
        ((arr[:,:,0] >= 0x4c - 30) & (arr[:,:,0] <= 0x95 + 30)) &
        ((arr[:,:,1] >= 0x76 - 30) & (arr[:,:,1] <= 0xcb + 30)) &
        ((arr[:,:,2] >= 0x27 - 30) & (arr[:,:,2] <= 0x64 + 30))
    )
    green_range = (0xcb - 0x76) if (0xcb - 0x76) > 0 else 1
    brightness = (arr[:,:,1].astype(float) - 0x76) / green_range
    arr[is_green, 0] = np.clip(new_color[0] * (0.6 + 0.8 * brightness[is_green]), 0, 255)
    arr[is_green, 1] = np.clip(new_color[1] * (0.6 + 0.8 * brightness[is_green]), 0, 255)
    arr[is_green, 2] = np.clip(new_color[2] * (0.6 + 0.8 * brightness[is_green]), 0, 255)
    del arr
    return colored_head

# --- Board & Game Logic ---
def draw_board():
    pastel_len = len(PASTEL_COLORS)
    def lighten(color, factor=0.6):
        return tuple(int(c + (255 - c) * factor) for c in color)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x, y = MARGIN + col * CELL_SIZE, MARGIN + row * CELL_SIZE
            base_color = PASTEL_COLORS[(row * GRID_SIZE + col) % pastel_len]
            color = lighten(base_color, 0.6)
            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))
            row_from_bottom = GRID_SIZE - 1 - row
            cell_num = (row_from_bottom * GRID_SIZE) + (col + 1 if row_from_bottom % 2 == 0 else GRID_SIZE - col)
            try: font = pygame.font.SysFont("ArcadeClassic", 28)
            except Exception: font = pygame.font.Font(None, 24)
            text = font.render(str(cell_num), True, (80, 80, 80))
            text_rect = text.get_rect(center=(x + CELL_SIZE/2, y + CELL_SIZE/2))
            screen.blit(text, text_rect)

def grid_to_pixel(cell_number):
    cell_number -= 1
    row = GRID_SIZE - 1 - (cell_number // GRID_SIZE)
    row_from_bottom = GRID_SIZE - 1 - row
    col = cell_number % GRID_SIZE if row_from_bottom % 2 == 0 else GRID_SIZE - 1 - (cell_number % GRID_SIZE)
    x = MARGIN + col * CELL_SIZE + CELL_SIZE // 2
    y = MARGIN + row * CELL_SIZE + CELL_SIZE // 2
    return x, y

# --- NEW LADDER DRAWING FUNCTION ---
def draw_solid_ladder(surf, p1, p2, rails_color, rungs_color):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    if dist < 10: return
    
    offset = 12  # Distance between rails
    perp = np.array([-dy / dist, dx / dist]) # Perpendicular vector
    p1, p2 = np.array(p1), np.array(p2)

    # Draw Rails
    rail1_start = p1 + perp * offset
    rail1_end = p2 + perp * offset
    rail2_start = p1 - perp * offset
    rail2_end = p2 - perp * offset
    pygame.draw.line(surf, rails_color, rail1_start, rail1_end, LADDER_RAIL_THICKNESS)
    pygame.draw.line(surf, rails_color, rail2_start, rail2_end, LADDER_RAIL_THICKNESS)

    # Draw Rungs
    margin_ratio = 0.1
    start_t, end_t = margin_ratio, 1 - margin_ratio
    num_rungs = max(2, int(dist * (end_t - start_t) / 30))
    for i in range(num_rungs):
        t = start_t if num_rungs == 1 else start_t + i * (end_t - start_t) / (num_rungs - 1)
        center_point = p1 + np.array([dx*t, dy*t])
        rung_start = center_point - perp * offset
        rung_end = center_point + perp * offset
        pygame.draw.line(surf, rungs_color, rung_start, rung_end, LADDER_RUNG_THICKNESS)


def cell_to_grid(cell_number):
    if not 1 <= cell_number <= 100: return None
    cell_idx = cell_number - 1
    row_from_bottom = cell_idx // GRID_SIZE
    row = GRID_SIZE - 1 - row_from_bottom
    if row_from_bottom % 2 == 0:
        col = cell_idx % GRID_SIZE
    else:
        col = GRID_SIZE - 1 - (cell_idx % GRID_SIZE)
    return (row, col)

def get_quadrant(cell_number):
    row, col = cell_to_grid(cell_number)
    is_top = row < GRID_SIZE / 2
    is_left = col < GRID_SIZE / 2
    if is_top and is_left: return TOP_LEFT
    if is_top and not is_left: return TOP_RIGHT
    if not is_top and is_left: return BOTTOM_LEFT
    return BOTTOM_RIGHT

def is_too_close(new_start, new_end, existing_items, radius):
    new_start_grid, new_end_grid = cell_to_grid(new_start), cell_to_grid(new_end)
    for exist_start, exist_end in existing_items:
        exist_start_grid, exist_end_grid = cell_to_grid(exist_start), cell_to_grid(exist_end)
        points_to_check = [
            (new_start_grid, exist_start_grid), (new_start_grid, exist_end_grid),
            (new_end_grid, exist_start_grid), (new_end_grid, exist_end_grid),
        ]
        for p1, p2 in points_to_check:
            if p1 is None or p2 is None: continue
            (r1, c1), (r2, c2) = p1, p2
            if max(abs(r1 - r2), abs(c1 - c2)) < radius:
                return True
    return False

def generate_items_in_quadrants(num_items, item_type, all_used_points, existing_items_of_same_type, exclusion_radius):
    items = []
    max_cell, MIN_LENGTH, MAX_LENGTH = GRID_SIZE * GRID_SIZE, 10, 50

    quadrants = [TOP_LEFT, TOP_RIGHT, BOTTOM_LEFT, BOTTOM_RIGHT]
    targets = (quadrants * (num_items // 4 + 1))[:num_items]
    random.shuffle(targets)

    for target_quadrant in targets:
        attempts = 300
        while attempts > 0:
            attempts -= 1
            
            if item_type == 'snake':
                start_range, end_range = (20, max_cell - 1), (2, max_cell - 20)
                start, end = random.randint(start_range[0], start_range[1]), random.randint(end_range[0], end_range[1])
                if start <= end: continue
            else: 
                start_range = (2, max_cell - 20)
                end_range = (20, 90)
                start, end = random.randint(start_range[0], start_range[1]), random.randint(end_range[0], end_range[1])
                if start >= end: continue
            
            if get_quadrant(start) != target_quadrant: continue
            if start in all_used_points or end in all_used_points: continue
            if not (MIN_LENGTH <= abs(start - end) <= MAX_LENGTH): continue
            if is_too_close(start, end, existing_items_of_same_type, exclusion_radius): continue
            
            items.append((start, end))
            existing_items_of_same_type.append((start, end))
            all_used_points.add(start)
            all_used_points.add(end)
            break
            
    return items

def generate_random_positions(num_snakes, num_ladders, exclusion_radius):
    all_used_points = set()
    snakes = generate_items_in_quadrants(num_snakes, 'snake', all_used_points, [], exclusion_radius)
    ladders = generate_items_in_quadrants(num_ladders, 'ladder', all_used_points, [], exclusion_radius)
    return snakes, ladders

def generate_snake_points(start_pos, end_pos):
    points = [start_pos]
    mid_x = (start_pos[0] + end_pos[0]) / 2 + random.randint(-CELL_SIZE, CELL_SIZE)
    mid_y = (start_pos[1] + end_pos[1]) / 2 + random.randint(-CELL_SIZE, CELL_SIZE)
    mid_x, mid_y = max(MARGIN, min(WIDTH - MARGIN, mid_x)), max(MARGIN, min(HEIGHT - MARGIN, mid_y))
    points.extend([(mid_x, mid_y), end_pos])
    while (len(points) - 1) % 3 != 0:
        t = random.random()
        x = start_pos[0] + (end_pos[0] - start_pos[0]) * t + random.randint(-CELL_SIZE//2, CELL_SIZE//2)
        y = start_pos[1] + (end_pos[1] - start_pos[1]) * t + random.randint(-CELL_SIZE//2, CELL_SIZE//2)
        points.insert(-1, (max(MARGIN, min(WIDTH - MARGIN, x)), max(MARGIN, min(HEIGHT - MARGIN, y))))
    return points

def cubic_bezier(points, samples=60):
    if len(points) < 4: return points
    curve = []
    for i in range(0, len(points) - 3, 3):
        p0, p1, p2, p3 = points[i:i + 4]
        for t in np.linspace(0, 1, samples):
            x = (1 - t)**3 * p0[0] + 3*(1 - t)**2 * t * p1[0] + 3*(1 - t) * t**2 * p2[0] + t**3 * p3[0]
            y = (1 - t)**3 * p0[1] + 3*(1 - t)**2 * t * p1[1] + 3*(1 - t) * t**2 * p2[1] + t**3 * p3[1]
            curve.append((x, y))
    return curve if curve else points

def generate_pattern_positions(curve):
    positions = []
    total_length = sum(math.hypot(curve[i+1][0] - curve[i][0], curve[i+1][1] - curve[i][1]) for i in range(len(curve) - 1))
    current_distance = 40 + random.randint(-10, 10)
    while current_distance < total_length - 40:
        positions.append(current_distance)
        current_distance += 25 + random.randint(-5, 10)
    return positions

def do_curves_intersect(curve1, curve2, min_distance):
    for i in range(0, len(curve1), 5):
        for j in range(0, len(curve2), 5):
            p1, p2 = curve1[i], curve2[j]
            if math.hypot(p1[0] - p2[0], p1[1] - p2[1]) < min_distance:
                return True
    return False

def draw_snake(surf, curve, color, head_img, pattern_positions):
    if len(curve) < 2: return
    max_outline, min_outline = 16, 6; max_inner, min_inner = 12, 4
    n, taper_start_point = len(curve), 0.8 
    for i in range(n - 1):
        progress = i / (n - 1)
        taper_factor = max(0, (progress - taper_start_point) / (1.0 - taper_start_point)) ** 1.5 if progress > taper_start_point else 0.0
        outline_w = int(max_outline - (max_outline - min_outline) * taper_factor)
        inner_w = int(max_inner - (max_inner - min_inner) * taper_factor)
        p0, p1 = curve[i], curve[i + 1]
        pygame.draw.line(surf, darken(color, 0.6), p0, p1, max(1, outline_w))
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
            current_inner_w = int(max_inner - (max_inner - min_inner) * taper_factor)
            dx, dy = p1[0] - p0[0], p1[1] - p0[1]
            mag = segment_length if segment_length > 0 else 1
            dir_vec, perp_vec = np.array([dx / mag, dy / mag]), np.array([-dy / mag, dx / mag])
            center = np.array((pos_x, pos_y))
            half_w, half_h = (current_inner_w / 2) * SNAKE_PATTERN_SIZE_MULTIPLIER, SNAKE_STRIPE_HEIGHT / 2
            pt1, pt2 = center - (dir_vec * half_h) + (perp_vec * half_w), center + (dir_vec * half_h) + (perp_vec * half_w)
            pt3, pt4 = center + (dir_vec * half_h) - (perp_vec * half_w), center - (dir_vec * half_h) - (perp_vec * half_w)
            outline_color = darken(color, 0.5)
            pygame.draw.polygon(surf, SNAKE_PATTERN_COLOR, [pt1, pt2, pt3, pt4])
            pygame.draw.polygon(surf, outline_color, [pt1, pt2, pt3, pt4], 2)
            pattern_idx += 1
        distance_traveled += segment_length
    colored_head = colorize_head(head_img, color)
    head_pos, next_pos = curve[0], curve[1]
    dx, dy = next_pos[0] - head_pos[0], next_pos[1] - head_pos[1]
    angle = np.degrees(np.arctan2(-dy, dx)) - 90
    rotated_head = pygame.transform.rotate(colored_head, angle)
    rect = rotated_head.get_rect(center=head_pos)
    surf.blit(rotated_head, rect)

def main():
    running = True
    def regenerate_board():
        num_snakes = np.random.randint(MIN_SNAKES_TO_GENERATE, MAX_SNAKES_TO_GENERATE + 1)
        num_ladders = np.random.randint(MIN_LADDERS_TO_GENERATE, MAX_LADDERS_TO_GENERATE + 1)
        
        snake_positions, ladder_positions = generate_random_positions(num_snakes, num_ladders, EXCLUSION_ZONE_RADIUS)
        
        ladder_colors = [random.choice(PASTEL_COLORS) for _ in ladder_positions]
        snake_colors = [SNAKE_FIXED_COLOR for _ in snake_positions]
        
        snake_curves, snake_patterns = [], []
        for start_cell, end_cell in snake_positions:
            start_pos, end_pos = grid_to_pixel(start_cell), grid_to_pixel(end_cell)
            final_curve = None
            for _ in range(MAX_CURVE_GENERATION_ATTEMPTS):
                is_valid_curve = True
                points = generate_snake_points(start_pos, end_pos)
                new_curve = cubic_bezier(points)
                for existing_curve in snake_curves:
                    if do_curves_intersect(new_curve, existing_curve, SNAKE_MIN_BODY_DISTANCE):
                        is_valid_curve = False
                        break 
                if is_valid_curve:
                    final_curve = new_curve
                    break 
            if final_curve is None: final_curve = new_curve
            if final_curve:
                snake_curves.append(final_curve)
                snake_patterns.append(generate_pattern_positions(final_curve))
        return snake_positions, ladder_positions, snake_colors, ladder_colors, snake_curves, snake_patterns

    snake_pos, ladder_pos, snake_colors, ladder_colors, snake_curves, snake_patterns = regenerate_board()
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                snake_pos, ladder_pos, snake_colors, ladder_colors, snake_curves, snake_patterns = regenerate_board()
        screen.fill((200, 200, 200))
        draw_board()
        for (start, end), color in zip(ladder_pos, ladder_colors):
            p1, p2 = grid_to_pixel(start), grid_to_pixel(end)
            # --- CHANGE: Call the new ladder function ---
            draw_solid_ladder(screen, p1, p2, darken(color, 0.8), color)
            pygame.draw.circle(screen, (255, 255, 255), p1, 8); pygame.draw.circle(screen, (0, 200, 0), p1, 6)
            pygame.draw.circle(screen, (255, 255, 255), p2, 8); pygame.draw.circle(screen, (0, 100, 255), p2, 6)
        for i in range(len(snake_pos)):
            if i < len(snake_curves):
                draw_snake(screen, snake_curves[i], snake_colors[i], snake_head_img, snake_patterns[i])
                end_pos = snake_curves[i][-1]
                pygame.draw.circle(screen, (255, 255, 255), end_pos, 8); pygame.draw.circle(screen, (255, 200, 0), end_pos, 6)
        pygame.display.flip()
        clock.tick(60)
    pygame.quit()

if __name__ == "__main__":
    main()