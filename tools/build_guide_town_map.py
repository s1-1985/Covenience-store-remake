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
Task #95: the orange 5x5 block is read as the land-selection cursor of the
start screen, not as land that belongs to the player (the screen is taken
before any store exists, and the player's store is 2x2 on the map, DATA4).
Its tiles are written as grass, and the player picks any 2x2 site instead
(see STORE_SITE below).
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

sys.path.insert(0, str(ROOT / "reference_sim"))
sys.path.insert(0, str(ROOT / "tools"))
from conveni_sim.baseline_data import TOWN_BUILDINGS  # noqa: E402
from guide_store_site import RIVAL_ACTIONS, place_rivals, store_site_rules  # noqa: E402

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


# REMAKE_BALANCED_DEFAULT (task #93): which generated sprite
# (assets/raw/conveni_map_assets_v2, new art) stands for each building tile.
# Roof colour follows that package's own brief (house_small_a = blue roof,
# house_small_b = red roof, house_small_c = green roof); the screenshot is too
# small to tell shops from offices, so white/grey single tiles cycle through
# the brief's 1x1 shop sprites and 2x2 blocks of building tiles use its 2x2
# office/house sprites.
SHOP_SPRITES = (
    "bookstore", "electronics_store", "clothing_store", "toy_store", "soba_shop", "ramen_shop",
    "fast_food_a", "fast_food_b", "izakaya_a", "izakaya_b", "izakaya_c", "game_center",
)
HOUSE_SPRITES = ("house_small_c", "house_small_a", "house_small_b")
OFFICE_SPRITES = ("company_small_a", "company_small_b", "company_small_c")
MEDIUM_HOUSE_SPRITES = ("house_medium_a", "house_medium_b")
# Tiles of the generated terrain package drawn for each map class.
TERRAIN_TILES = {
    "G": "map_grass_plain",
    "g": "map_trees_sparse",
    "D": "map_dirt_sparse",
    "B": "map_grass_plain",
    "T": "map_rail_ew",
    "R": "map_road_ew",
}
DARK_GRASS_TONE = 135



def _tile_shares(im, col, row):
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    x0 = int(round(X0 + col * TILE_W))
    y0 = int(round(Y0 + row * TILE_H))
    x1 = int(round(X0 + (col + 1) * TILE_W))
    y1 = int(round(Y0 + (row + 1) * TILE_H))
    ys, xs = slice(y0, y1), slice(x0, x1)
    n = (y1 - y0) * (x1 - x0)
    green = ((g > r + 15) & (g > b))[ys, xs]
    return {
        "green_tone": float(g[ys, xs][green].mean()) if green.any() else 0.0,
        "red": float(((r > 160) & (g < 120) & (b < 120))[ys, xs].sum() / n),
        "blue": float(((b > 150) & (r < 130))[ys, xs].sum() / n),
        "white": float(((r > 190) & (g > 190) & (b > 190))[ys, xs].sum() / n),
    }


def _buildings(rows, im):
    used = set()
    placed = []
    offices = houses = 0
    height, width = len(rows), len(rows[0])
    for y in range(height - 1):
        for x in range(width - 1):
            block = [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
            if any(rows[by][bx] != "B" or (bx, by) in used for bx, by in block):
                continue
            white = sum(_tile_shares(im, bx + FIRST_COL, by)["white"] for bx, by in block) / 4
            if white > 0.2:
                sprite = OFFICE_SPRITES[offices % len(OFFICE_SPRITES)]
                offices += 1
            else:
                sprite = MEDIUM_HOUSE_SPRITES[houses % len(MEDIUM_HOUSE_SPRITES)]
                houses += 1
            used.update(block)
            placed.append({"tile": [x, y], "size": [2, 2], "sprite": sprite})
    shops = 0
    for y, line in enumerate(rows):
        for x, c in enumerate(line):
            if c != "B" or (x, y) in used:
                continue
            shares = _tile_shares(im, x + FIRST_COL, y)
            if shares["red"] > max(shares["blue"], 0.08) and shares["red"] >= shares["white"] * 0.5:
                sprite = "house_small_b"
            elif shares["blue"] > 0.08 and shares["blue"] >= shares["white"] * 0.5:
                sprite = "house_small_a"
            elif shares["white"] > 0.15:
                sprite = SHOP_SPRITES[shops % len(SHOP_SPRITES)]
                shops += 1
            else:
                sprite = HOUSE_SPRITES[(x * 7 + y * 3) % len(HOUSE_SPRITES)]
            placed.append({"tile": [x, y], "size": [1, 1], "sprite": sprite})
    return placed


def build():
    rows = classify()
    # Task #95: the orange 5x5 block is the start screen's selection cursor;
    # what lies under it is not visible, so it is written as grass
    # (REMAKE_BALANCED_DEFAULT).
    lot = [(x, y) for y, line in enumerate(rows) for x, c in enumerate(line) if c == "O"]
    lot_min = [min(x for x, _ in lot), min(y for _, y in lot)]
    lot_max = [max(x for x, _ in lot), max(y for _, y in lot)]
    assert (lot_max[0] - lot_min[0], lot_max[1] - lot_min[1]) == (4, 4)
    rows = [
        "".join(
            "G" if lot_min[0] <= x <= lot_max[0] and lot_min[1] <= y <= lot_max[1] else c
            for x, c in enumerate(line)
        )
        for y, line in enumerate(rows)
    ]
    im = np.array(Image.open(SOURCE).convert("RGB")).astype(int)
    rows = [
        "".join(
            "g" if c == "G" and _tile_shares(im, x + FIRST_COL, y)["green_tone"] < DARK_GRASS_TONE else c
            for x, c in enumerate(line)
        )
        for y, line in enumerate(rows)
    ]
    buildings = _buildings(rows, im)
    catalog = {}
    for profile in TOWN_BUILDINGS:
        if any(b["sprite"] == profile.id for b in buildings):
            catalog[profile.id] = {
                "name": profile.display_name_ja,
                "price": profile.building_price_yen.value,
            }
    site = store_site_rules(rows, buildings)
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
            "Task #93: the town is drawn with the generated terrain tiles and building sprites "
            "of assets/raw/conveni_map_assets_v2 (new art, not original graphics). Grass tiles "
            "darker than the screenshot's lower quartile are drawn as trees (the original map "
            "is dotted with round trees, video_155s/189s). The player's store is drawn as the "
            "flat 本店 mark cut from the gameplay video (CONFIRMED_VISUAL, "
            "assets/raw/conveni_remaining_assets_v1 map_blue_hq). "
            "Task #95: the orange 5x5 block is read as the start screen's land-selection cursor "
            "(inference: the screen is taken before any store exists); its tiles are grass "
            "(REMAKE_BALANCED_DEFAULT, what lies under it is not visible) and the player picks "
            "a 2x2 site anywhere (store_site). building_catalog: each building sprite's DATA4 "
            "name and printed price (CONFIRMED_OFFICIAL, guide p.92-95). "
            "Task #98: rival_stores -- the beginner map starts with the rival's 本店 and 2号店 "
            "(CONFIRMED_OFFICIAL, the beginner map's DATA block, quick reference guide book pages 66-83; guide_data "
            "copies its figures), drawn as the red 本/02 marks (CONFIRMED_VISUAL, gameplay video). "
            "Their positions are not recorded anywhere: REMAKE_BALANCED_DEFAULT, each takes in turn "
            "the vacant site with the most customers left to it (tools/guide_store_site.py "
            "place_rivals). "
            "REMAKE_BALANCED_DEFAULT: which building sprite stands on which building tile "
            "(roof colour -> house A/B/C per the sprite brief, white -> shops/offices, 2x2 "
            "blocks -> 2x2 sprites) and which terrain tile stands for each class are this "
            "project's own choices."
        ),
        "source_image": "assets/raw/conveni_guide_town_v1/beginner_map_start.png",
        "legend": {"G": "grass", "g": "trees", "D": "bare_ground", "R": "road", "T": "railway", "B": "building"},
        "terrain_tiles": TERRAIN_TILES,
        "buildings": buildings,
        "building_catalog": catalog,
        "store_site": site,
        "rival_stores": place_rivals(rows, buildings),
        "rival_actions": RIVAL_ACTIONS,
        "store_mark_sprite": "map_blue_hq",
        "width_tiles": COLS,
        "height_tiles": ROWS,
        "tile_rows": rows,
    }


def main():
    text = CONFIG.read_text(encoding="utf-8")
    config = json.loads(text)
    config.pop("guide_town_map", None)
    block = build()
    start = text.find('\n  "guide_town_map": ')
    if start != -1:
        # Cut out only this block: up to the next top-level key, or the
        # closing brace when it is the last one.
        following = re.search(r'\n  "[^"]+": ', text[start + 1:])
        if following is None:
            text = text[:start].rstrip().rstrip(",") + "\n}\n"
        else:
            text = text[:start] + text[start + 1 + following.start():]
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
    print("store_site", {k: v for k, v in block["store_site"].items() if k != "evidence_note"})


if __name__ == "__main__":
    sys.exit(main())
