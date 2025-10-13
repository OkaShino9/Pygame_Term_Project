# ==== Board geometry (ปรับได้) ====
COLS = 10           # จำนวนคอลัมน์
ROWS = 10           # จำนวนแถว
CELL = 64           # ขนาดช่อง (พิกเซล)
MARGIN = 10         # ระยะขอบรอบกระดาน

# ==== Sidebar (ขวา) ====
SIDEBAR_W = 180     # ความกว้างแถบด้านขวา

# ==== Derived window size (auto) ====
W = MARGIN * 2 + COLS * CELL + SIDEBAR_W
H = MARGIN * 2 + ROWS * CELL
FPS = 60

# ==== Colors ====
COL_BG      = (245, 248, 255)
COL_GRID    = (170, 180, 210)
COL_A       = (255, 255, 255)
COL_B       = (230, 236, 255)
COL_TEXT    = (40, 50, 80)
COL_PANEL   = (235, 238, 250)

# สีงู/บันได
COL_SNAKE   = (204, 62, 62)   # งู (แดง)
COL_LADDER  = (60, 160, 95)   # บันได (เขียว)

# Players (สูงสุด 4 คน: (fill, stroke))
PLAYER_STYLES = [
    ((220, 70, 70),  (120, 30, 30)),   # P1
    ((70, 110, 230), (30, 50, 140)),   # P2
    ((245, 165, 36), (160, 95, 20)),   # P3 (ส้ม)
    ((100, 185, 95), (45, 120, 50)),   # P4 (เขียว)
]
