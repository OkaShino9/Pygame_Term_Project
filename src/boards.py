# -*- coding: utf-8 -*-
from dataclasses import dataclass
from pathlib import Path
import json, random
from typing import Optional, List, Dict, Any
import config as C

@dataclass
class BoardSpec:
    name: str
    grid: int
    ladders: dict[int, int]
    snakes: dict[int, int]
    image_path: Optional[Path] = None
    cell_override: Optional[int] = None

def _parse_mapping(d: Dict[str, Any]) -> dict[int, int]:
    out: dict[int,int] = {}
    for k, v in d.items():
        out[int(k)] = int(v)
    return out

def load_board_file(p: Path) -> Optional[BoardSpec]:
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        name = data.get("name", p.stem)
        grid = int(data.get("grid", C.GRID_DEFAULT))
        ladders = _parse_mapping(data.get("ladders", {}))
        snakes  = _parse_mapping(data.get("snakes", {}))
        img_rel = data.get("image")
        image_path = (C.ROOT / img_rel) if img_rel else None
        cell_override = data.get("cell_override")
        if cell_override is not None: cell_override = int(cell_override)
        return BoardSpec(name=name, grid=grid, ladders=ladders, snakes=snakes,
                         image_path=image_path, cell_override=cell_override)
    except Exception as e:
        print(f"[WARN] อ่านบอร์ดจาก {p} ไม่ได้:", e); return None

def load_all_boards() -> List[BoardSpec]:
    boards: List[BoardSpec] = []
    if not C.BOARDS_DIR.exists(): return boards
    for p in sorted(C.BOARDS_DIR.glob("*.json")):
        spec = load_board_file(p)
        if spec: boards.append(spec)
    return boards

def pick_board(boards: List[BoardSpec]) -> Optional[BoardSpec]:
    if not boards: return None
    return random.choice(boards)
