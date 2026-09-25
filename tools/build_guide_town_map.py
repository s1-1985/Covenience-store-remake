"""Reads the guide's beginner-map screenshot tile by tile into vertical_slice.json's
"guide_town_map" block.

Source: assets/raw/conveni_guide_town_v1/beginner_map_start.png, the 初級マップ
start screen (1年目1月1日 00:00 ¥200,000,000) printed on guide p.11, cropped at the
scan's own resolution. See docs/decisions/0161-guide-town-map.md.

Grid (measured on that image, CONFIRMED_VISUAL):
- vertical roads repeat every ~98.75 px = 10 tiles  -> tile width 9.875 px
- the orange 5x5 lot is ~52 px tall, horizontal roads 76.5 -> 285.5 px = 20 tiles
                                                    -> tile height 10.45 px
- roads/railway are single straight lines at tile centres: vertical roads at
  columns 12, 22, 32; horizontal roads at rows 6, 19, 26; railway at row 12.
Per-tile class (PROVISIONAL, colour classification of a halftone print):
  G grass, D bare ground, R road, T railway, B building, O the orange lot.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "game" / "data" / "vertical_slice.json"
SOURCE = ROOT / "assets" / "raw" / "conveni_guide_town_v1" / "beginner_map_start.png"

TILE_W, TILE_H = 9.875, 10.45
X0, Y0 = 120.0 - 12.5 * TILE_W, 76.5 - 6.5 * TILE_H
FIRST_COL, COLS, ROWS = 1, 41, 35
ROAD_COLS = (12, 22, 32)
ROAD_ROWS = (6, 19, 26)
RAIL_ROW = 12


def classify(image_path=SOURCE):
    im = np.array(Image.open(image_path).convert("RGB")).astype(int)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    gray = (abs(r - g) < 20) & (abs(g - b) < 24) & (r > 85) & (r < 200)
    green = (g > r + 15) & (g > b)
    brown = (r > g + 5) & (r < 200) & (g < 150) & (b < 110)
    orange = (r > 200) & (g > 90) & (g < 170) & (b < 80)

    def box(col, row):
        x0 = int(round(X0 + col * TILE_W))
        y0 = int(round(Y0 + row * TILE_H))
        x1 = int(round(X0 + (col + 1) * TILE_W))
        y1 = int(round(Y0 + (row + 1) * TILE_H))
        return slice(y0, y1), slice(x0, x1), (y1 - y0) * (x1 - x0)

    rows = []
    for row in range(ROWS):
        line = ""
        for col in range(FIRST_COL, FIRST_COL + COLS):
            ys, xs, n = box(col, row)

            def share(mask):
                return mask[ys, xs].sum() / n

            if row == RAIL_ROW:
                line += "T"
                continue
            on_line = (col in ROAD_COLS) or (row in ROAD_ROWS)
            if on_line and share(gray) > 0.15:
                line += "R"
            elif share(orange) > 0.4:
                line += "O"
            elif 1 - share(green) - share(brown) - share(gray) > 0.35:
                line += "B"
            elif share(brown) > share(green):
                line += "D"
            else:
                line += "G"
        rows.append(line)
    return rows


def build():
    rows = classify()
    # The lot is one solid 5x5 block on screen; print noise leaves a few of
    # its edge tiles unclassified, so it is restored to its bounding box.
    lot = [(x, y) for y, line in enumerate(rows) for x, c in enumerate(line) if c == "O"]
    lot_min = [min(x for x, _ in lot), min(y for _, y in lot)]
    lot_max = [max(x for x, _ in lot), max(y for _, y in lot)]
    assert (lot_max[0] - lot_min[0], lot_max[1] - lot_min[1]) == (4, 4)
    rows = [
        "".join(
            "O" if lot_min[0] <= x <= lot_max[0] and lot_min[1] <= y <= lot_max[1] else c
            for x, c in enumerate(line)
        )
        for y, line in enumerate(rows)
    ]
    return {
        "evidence_note": (
            "Task #90. The town around the player's first store: the visible part of the "
            "beginner map (初級マップ) at the start of a game, read tile by tile from the "
            "guide p.11 screenshot (assets/raw/conveni_guide_town_v1). Road/railway positions "
            "and the grid are CONFIRMED_VISUAL (straight lines measured on the image); each "
            "tile's grass/bare-ground/building class is PROVISIONAL (automatic colour "
            "classification of a halftone print, tools/build_guide_town_map.py). The orange "
            "5x5 lot is drawn where the screenshot shows it; that it marks the player's store "
            "site is PROVISIONAL (the screen is taken before any store opens). "
            "REMAKE_BALANCED_DEFAULT: building tiles are drawn with this project's own "
            "generated house sprites (assets/raw/conveni_map_assets_v2 is new art, not "
            "original graphics); which sprite goes on which building tile is this project's "
            "own choice."
        ),
        "source_image": "assets/raw/conveni_guide_town_v1/beginner_map_start.png",
        "legend": {"G": "grass", "D": "bare_ground", "R": "road", "T": "railway", "B": "building", "O": "store_lot"},
        "width_tiles": COLS,
        "height_tiles": ROWS,
        "tile_rows": rows,
        "store_lot_origin_tile": lot_min,
    }


def main():
    text = CONFIG.read_text(encoding="utf-8")
    config = json.loads(text)
    config.pop("guide_town_map", None)
    block = build()
    start = text.find('\n  "guide_town_map": ')
    if start != -1:
        text = text[:start].rstrip().rstrip(",") + "\n}\n"
    body = json.dumps(block, ensure_ascii=False, indent=2)
    body = re.sub(r"\[\s*(-?[\d.]+),\s*(-?[\d.]+)\s*\]", r"[\1, \2]", body)
    body = "\n".join("  " + line for line in body.splitlines()).lstrip()
    head = text.rstrip()
    assert head.endswith("}")
    text = head[:-1].rstrip() + ',\n  "guide_town_map": ' + body + "\n}\n"
    json.loads(text)
    CONFIG.write_text(text, encoding="utf-8")
    for line in block["tile_rows"]:
        print(line)
    print("lot", block["store_lot_origin_tile"])


if __name__ == "__main__":
    sys.exit(main())
