"""Writes vertical_slice.json's "guide_store_types" block: the six stores of the
original's 「店舗を選んで下さい」 screen and the furnished small store a new game
opens with.

Evidence (details in docs/decisions/0175-small-store-start.md):
- CONFIRMED_VISUAL (PS screenshot, docs/research/ps-store-selection-lock-visual-
  2026-09-05.md): after the land, the player picks one of 6 stores shown 2 rows x
  3 columns; at the start only the left column (the two small stores) can be
  picked, the other four are greyed out; the top-left store costs ¥6,000,000.
- CONFIRMED_OFFICIAL (guide 店舗データ, book pages 106-109; reference_sim
  STORE_VARIANTS): the 6 stores are 3 sizes x 2 orientations with floors 5x8/8x5,
  7x10/10x7, 8x12/12x8 tiles and construction prices 6/12/18 million yen.
- No furnished small store was recovered (the guide's 小規模店作成用おすすめアイテム
  list is unreadable in the scans), so the starting small layouts below are this
  project's own (REMAKE_BALANCED_DEFAULT), with two numbers taken by analogy from
  the guide's only printed store, p.48 (tools/build_guide_p48_store.py):
  * shelf count = p.48's shelves per floor tile (34 / 96) x the small floor (40)
    = 14.2 -> 14;
  * which categories = p.48's shelf share per category, scaled to 14 shelves
    (largest remainder); ties are broken by how much the town's buildings want
    the category (DATA4 wanted x building squares on the guide town map).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_guide_p48_store as p48  # noqa: E402

CONFIG = Path(__file__).resolve().parents[1] / "game" / "data" / "vertical_slice.json"

# (id, icon, size tier, floor tiles, price, pickable at the start, grid cell
# [column, row] on the selection screen). Left column = small (CONFIRMED_VISUAL);
# top row = the guide's 店舗1/3/5, bottom row = 店舗2/4/6 (list order, as in
# reference_sim STORE_VARIANTS -- an inference, see its note).
STORE_TYPES = [
    ("small_top", "store_type_01", "small", [5, 8], 6_000_000, True, [0, 0]),
    ("small_bottom", "store_type_02", "small", [8, 5], 6_000_000, True, [0, 1]),
    ("medium_top", "store_type_03", "medium", [7, 10], 12_000_000, False, [1, 0]),
    ("medium_bottom", "store_type_04", "medium", [10, 7], 12_000_000, False, [1, 1]),
    ("large_top", "store_type_05", "large", [8, 12], 18_000_000, False, [2, 0]),
    ("large_bottom", "store_type_06", "large", [12, 8], 18_000_000, False, [2, 1]),
]

P48_FLOOR_TILES = 12 * 8

# Shelf spots of each small layout: (tile_x, tile_y, facing), and the other
# fixtures. REMAKE_BALANCED_DEFAULT (this project's own arrangement): shelves
# along both side walls and one island, the register near the back with the
# checkout staff behind it, the break room in a corner, every shelf reachable.
LAYOUTS = {
    # 5 wide x 8 deep; entrance in the middle of the front (top) wall.
    "small_top": {
        "entry": [4, 0],
        "exit": [5, 0],
        "shelves": [
            # left wall, customers stand to the right
            (0, 1, "right"), (0, 2, "right"), (0, 3, "right"), (0, 4, "right"), (0, 5, "right"),
            # right wall, customers stand to the left
            (4, 1, "left"), (4, 2, "left"), (4, 3, "left"), (4, 4, "left"), (4, 5, "left"),
            # island down the middle
            (2, 1, "left"), (2, 2, "left"), (2, 3, "right"), (2, 4, "right"),
        ],
        "checkout": {"origin_subcell": [6, 12], "interaction_subcell": [6, 11]},
        "break_room": {"origin_subcell": [0, 12], "interaction_subcell": [4, 13]},
        "staff_start_subcells": {"staff-1": [8, 14], "staff-2": [4, 10], "staff-3": [5, 14]},
    },
    # 8 wide x 5 deep; entrance in the middle of the front (top) wall.
    "small_bottom": {
        "entry": [7, 0],
        "exit": [8, 0],
        "shelves": [
            # left wall
            (0, 0, "right"), (0, 1, "right"), (0, 2, "right"), (0, 3, "right"), (0, 4, "right"),
            # right wall below the break room
            (7, 2, "left"), (7, 3, "left"), (7, 4, "left"),
            # island along the front, customers stand below it
            (2, 1, "down"), (3, 1, "down"), (4, 1, "down"), (5, 1, "down"),
            # island in front of the register, customers stand above it
            (2, 3, "up"), (3, 3, "up"),
        ],
        "checkout": {"origin_subcell": [8, 6], "interaction_subcell": [9, 5]},
        "break_room": {"origin_subcell": [12, 0], "interaction_subcell": [12, 4]},
        "staff_start_subcells": {"staff-1": [9, 8], "staff-2": [3, 8], "staff-3": [12, 8]},
    },
}

# Which category goes on which spot: cold shelves first along one wall, then
# the rest; same order for both layouts (REMAKE_BALANCED_DEFAULT placement).
PLACEMENT_ORDER = [
    "vegetables", "fish", "meat", "bento", "cold_drink", "ice_cream",
    "bread", "snacks", "instant_food", "daily_goods", "underwear",
    "electronics", "stationery", "books", "frozen_food",
]


def town_demand(config):
    """DATA4 wanted x building squares, over the guide town map."""
    town = config["guide_town_map"]
    demand = {}
    for building in town["buildings"]:
        squares = building["size"][0] * building["size"][1]
        for category in town["building_catalog"][building["sprite"]]["wanted"]:
            demand[category] = demand.get(category, 0) + squares
    return demand


def shelf_count(floor_tiles):
    return int(round(len(p48.SHELVES) * floor_tiles / P48_FLOOR_TILES))


def assortment(config, shelves):
    """p.48's per-category shelf share scaled to `shelves` (largest remainder)."""
    counts = {}
    for _x, _y, category, _facing, _note in p48.SHELVES:
        counts[category] = counts.get(category, 0) + 1
    total = len(p48.SHELVES)
    demand = town_demand(config)
    quota = {category: count * shelves / total for category, count in counts.items()}
    result = {category: int(q) for category, q in quota.items()}
    left = shelves - sum(result.values())
    ranked = sorted(
        quota,
        key=lambda category: (-(quota[category] - int(quota[category])), -demand.get(category, 0), category),
    )
    for category in ranked[:left]:
        result[category] += 1
    return {category: n for category, n in result.items() if n > 0}


def build_layout(config, type_id, size):
    spec = LAYOUTS[type_id]
    catalog = {entry["catalog_id"]: entry for entry in config["fixture_catalog"]}
    pricing = {entry["catalog_id"]: entry for entry in config["product_catalog"]}
    spots = spec["shelves"]
    assert len(spots) == shelf_count(size[0] * size[1]), type_id
    counts = assortment(config, len(spots))
    categories = []
    for category in PLACEMENT_ORDER:
        categories.extend([category] * counts.get(category, 0))
    assert len(categories) == len(spots)
    fixtures = [
        {
            "id": "checkout-1",
            "kind": "checkout",
            "rotation_quarter_turns": 0,
            "origin_subcell": spec["checkout"]["origin_subcell"],
            "footprint_tiles": [2, 1],
            "interaction_subcell": spec["checkout"]["interaction_subcell"],
        },
        {
            "id": "break-room-1",
            "kind": "break_room",
            # Same break room as the guide's p.48 store (analogy).
            "catalog_id": "break_room_2",
            "rotation_quarter_turns": 0,
            "origin_subcell": spec["break_room"]["origin_subcell"],
            "footprint_tiles": [2, 2],
            "interaction_subcell": spec["break_room"]["interaction_subcell"],
        },
    ]
    products = []
    seen = {}
    for (tile_x, tile_y, facing), category in zip(spots, categories):
        seen[category] = seen.get(category, 0) + 1
        fixture_id = "shelf-%s-%d" % (category.replace("_", "-"), seen[category])
        ox, oy = tile_x * 2, tile_y * 2
        interaction = {
            "left": [ox - 1, oy + 1],
            "right": [ox + 2, oy + 1],
            "up": [ox + 1, oy - 1],
            "down": [ox + 1, oy + 2],
        }[facing]
        catalog_id = p48.SHELF_FOR[category]
        fixtures.append({
            "id": fixture_id,
            "kind": "shelf",
            "catalog_id": catalog_id,
            "rotation_quarter_turns": 0,
            "origin_subcell": [ox, oy],
            "footprint_tiles": [1, 1],
            "interaction_subcell": interaction,
        })
        products.append({
            "id": "product-%s" % fixture_id[len("shelf-"):],
            "catalog_id": category,
            "fixture_id": fixture_id,
            # A newly stocked shelf starts full (same analogy as p.48).
            "initial_stock_units": int(catalog[catalog_id]["capacity"]),
            "sale_price_yen": int(pricing[category]["sale_price_yen"]),
            "restock_unit_cost_yen": int(pricing[category]["restock_unit_cost_yen"]),
        })
    guide = config["guide_starting_store"]
    return {
        "store": {
            "width_tiles": size[0],
            "height_tiles": size[1],
            "subcells_per_tile": 2,
            "entry_subcell": spec["entry"],
            "exit_subcell": spec["exit"],
            "size_tier": "small",
            "size_tier_evidence_note": "See guide_store_types.evidence_note.",
        },
        "fixtures": fixtures,
        "products": products,
        "checkout_fixture_id": "checkout-1",
        "staff_start_subcells": spec["staff_start_subcells"],
        # REMAKE_BALANCED_DEFAULT: p.48's cap (8) scaled by floor area.
        "max_concurrent_customers": max(1, int(round(
            guide["max_concurrent_customers"] * size[0] * size[1] / P48_FLOOR_TILES
        ))),
        "provisional_restock_product_id": products[0]["id"],
        "sample_layout_label": "開店時の配置",
    }


def build(config):
    types = []
    for type_id, icon, tier, size, price, pickable, cell in STORE_TYPES:
        entry = {
            "id": type_id,
            "icon": icon,
            "size_tier": tier,
            "floor_tiles": size,
            "construction_price_yen": price,
            "selectable_at_start": pickable,
            "grid_cell": cell,
        }
        if type_id in LAYOUTS:
            entry["layout"] = build_layout(config, type_id, size)
        types.append(entry)
    return {
        "scenario_id": "guide-small-store-start-v1",
        "default_id": "small_top",
        "evidence_note": (
            "Task #104. After buying the land the player picks the store in 「店舗を選んで下さい」: "
            "6 stores in 2 rows x 3 columns, of which only the left column (the two small stores) "
            "can be picked at the start, the other four greyed out (CONFIRMED_VISUAL, PS screenshot, "
            "docs/research/ps-store-selection-lock-visual-2026-09-05.md); the top-left store shows "
            "¥6,000,000 (CONFIRMED_VISUAL). Sizes 5x8/8x5, 7x10/10x7, 8x12/12x8 tiles and prices "
            "6/12/18 million yen: CONFIRMED_OFFICIAL (guide 店舗データ, book pages 106-109, "
            "reference_sim STORE_VARIANTS). Which orientation is 'top'/'bottom' follows the guide's "
            "list order (inference, as in STORE_VARIANTS). The construction price is paid when the "
            "store is built, on top of the land. The furnished small layouts are "
            "REMAKE_BALANCED_DEFAULT (no furnished small store was recovered; the guide's "
            "小規模店作成用おすすめアイテム list is unreadable): this project's own arrangement, "
            "with the shelf count (p.48's 34 shelves per 96 floor tiles x 40 tiles = 14) and the "
            "categories (p.48's shelf share per category scaled to 14 shelves, ties broken by the "
            "town buildings' DATA4 wanted items) taken by analogy from the guide's p.48 store. "
            "Shelf type, starting stock (= capacity) and break room follow p.48 the same way. "
            "The customer cap is p.48's 8 scaled by floor area (REMAKE_BALANCED_DEFAULT)."
        ),
        "types": types,
    }


def main():
    text = CONFIG.read_text(encoding="utf-8")
    config = json.loads(text)
    config.pop("guide_store_types", None)
    block = build(config)
    start = text.find('\n  "guide_store_types": ')
    if start != -1:
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
    text = head[:-1].rstrip() + ',\n  "guide_store_types": ' + body + "\n}\n"
    json.loads(text)
    CONFIG.write_text(text, encoding="utf-8")
    for entry in block["types"]:
        if "layout" in entry:
            layout = entry["layout"]
            print(entry["id"], len(layout["fixtures"]), "fixtures",
                  sorted({p["catalog_id"] for p in layout["products"]}))


if __name__ == "__main__":
    sys.exit(main())
