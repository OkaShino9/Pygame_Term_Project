# -*- coding: utf-8 -*-
import pygame
from pygame import Surface
from typing import List, Optional
import config as C

# Runtime geometry (อัปเดตได้เมื่อเปลี่ยนบอร์ด)
GRID = C.GRID_DEFAULT
CELL = C.CELL_DEFAULT
BOARD_W = CELL * GRID
BOARD_H = CELL * GRID
LEFT_W = C.W - C.RIGHT_PANEL_W
ORIGIN = ((LEFT_W - BOARD_W)//2, (C.H - BOARD_H)//2)
BOARD_RECT = pygame.Rect(ORIGIN[0], ORIGIN[1], BOARD_W, BOARD_H)

FONTS = {}
BOARD_IMG: Optional[Surface] = None
DICE_IMGS: Optional[List[Surface]] = None

def _recompute_geometry():
    global BOARD_W, BOARD_H, LEFT_W, ORIGIN, BOARD_RECT
    BOARD_W = CELL * GRID
    BOARD_H = CELL * GRID
    LEFT_W = C.W - C.RIGHT_PANEL_W
    ORIGIN = ((LEFT_W - BOARD_W)//2, (C.H - BOARD_H)//2)
    BOARD_RECT = pygame.Rect(ORIGIN[0], ORIGIN[1], BOARD_W, BOARD_H)

def get_font(size: int) -> pygame.font.Font:
    if size in FONTS: return FONTS[size]
    try:
        if C.FONT_PATH.exists():
            FONTS[size] = pygame.font.Font(str(C.FONT_PATH), size)
        else:
            FONTS[size] = pygame.font.SysFont("arial", size)
    except Exception:
        FONTS[size] = pygame.font.Font(None, size)
    return FONTS[size]

def init_resources():
    """โหลดฟอนต์/เต๋า (ภาพบอร์ดจะ apply ทีหลังตามบอร์ด)"""
    global DICE_IMGS, BOARD_IMG
    BOARD_IMG = None
    DICE_IMGS = None
    if C.DICE_DIR.exists() and C.DICE_DIR.is_dir():
        tmp = []
        ok = True
        for i in range(1,7):
            p = C.DICE_DIR / f"dice{i}.png"
            if not p.exists(): ok=False; break
            try:
                img = pygame.image.load(str(p)).convert_alpha()
                img = pygame.transform.smoothscale(img, (120,120))
                tmp.append(img)
            except:
                ok=False; break
        if ok and len(tmp)==6: DICE_IMGS = tmp

def apply_board(grid: int, image_path=None, cell_override=None):
    """ตั้งค่า GRID/CELL + โหลดภาพบอร์ด (หรือ fallback)"""
    global GRID, CELL, BOARD_IMG
    GRID = int(grid) if grid else C.GRID_DEFAULT
    CELL = int(cell_override) if cell_override else C.CELL_DEFAULT

    BOARD_IMG = None
    candidates = []
    if image_path: candidates.append(image_path)
    candidates.append(C.BOARD_IMG_FALLBACK)
    for p in candidates:
        try:
            if p and p.exists():
                img = pygame.image.load(str(p)).convert()
                side = min(img.get_width(), img.get_height())
                img = pygame.transform.smoothscale(img, (side, side))
                BOARD_IMG = img
                if not cell_override:
                    CELL = side // GRID if GRID>0 else C.CELL_DEFAULT
                break
        except Exception as e:
            print(f"[WARN] โหลดภาพบอร์ดไม่ได้จาก {p}:", e)
            continue

    _recompute_geometry()

# font helpers
def font_xs(): return get_font(C.FONT_SIZES["xs"])
def font_sm(): return get_font(C.FONT_SIZES["sm"])
def font_md(): return get_font(C.FONT_SIZES["md"])
def font_lg(): return get_font(C.FONT_SIZES["lg"])
def font_xl(): return get_font(C.FONT_SIZES["xl"])
def font_xxl(): return get_font(C.FONT_SIZES["xxl"])
