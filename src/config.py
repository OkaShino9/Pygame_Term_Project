# -*- coding: utf-8 -*-
from pathlib import Path
from settings import load_settings

ROOT = Path(__file__).resolve().parent.parent  # project root
SET = load_settings(ROOT)

# Window & timing
W: int   = SET["window"]["width"]
H: int   = SET["window"]["height"]
FPS: int = SET["window"]["fps"]

# Board defaults (จริงจะถูก apply จากบอร์ด JSON ผ่าน resources.apply_board)
GRID_DEFAULT: int   = SET["board"]["grid"]
CELL_DEFAULT: int   = SET["board"]["cell_default"]
RIGHT_PANEL_W: int  = SET["board"]["right_panel_w"]

# Assets
ASSETS_DIR        = ROOT / "assets"
BOARD_IMG_FALLBACK= ROOT / SET["assets"]["board_img"]
DICE_DIR          = ROOT / SET["assets"]["dice_dir"]
FONT_PATH         = ROOT / SET["assets"]["font_path"]

# Fonts
FONT_SIZES = SET["fonts"]

# Colors
COL_BG_TOP   = tuple(SET["colors"]["bg_top"])
COL_BG_BOT   = tuple(SET["colors"]["bg_bottom"])
COL_TEXT     = tuple(SET["colors"]["text"])
COL_SUBT     = tuple(SET["colors"]["subt"])
COL_BORDER   = tuple(SET["colors"]["border"])
COL_CARD     = tuple(SET["colors"]["card"])
COL_BTN      = tuple(SET["colors"]["btn"])
COL_BTN_H    = tuple(SET["colors"]["btn_hover"])
COL_BTN_TX   = tuple(SET["colors"]["btn_text"])
COL_SHADOW   = tuple(SET["colors"]["shadow"])
COL_WIN_OV   = tuple(SET["colors"]["win_overlay"])
COL_P        = [tuple(rgb) for rgb in SET["colors"]["players"]]

# Rules (ทั่วไป)
EXACT_WIN: bool = bool(SET["rules"]["exact_win"])

# Boards multi-json
BOARDS_DIR = ROOT / SET.get("boards", {}).get("dir", "assets/boards")
SHUFFLE_EACH_GAME: bool = bool(SET.get("boards", {}).get("shuffle_each_game", True))
