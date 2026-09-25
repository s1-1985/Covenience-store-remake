"""Writes vertical_slice.json's "guide_starting_store" block from the table below.

Source: strategy guide p.48 「未開の土地に開店するなら!」 (PDF4 page 1), the store
diagram printed from the game's own top-down fixture graphics. Tile positions
below were read off a 137 px grid laid over the page rendered at scale 6
(floor origin x=686, y=1253); see docs/decisions/0160-guide-p48-starting-store.md.

Evidence per column:
- tile position / 1x1 footprint: CONFIRMED_VISUAL (read directly off the diagram).
- category: PROVISIONAL -- this project's own reading of the product pictures
  drawn on each shelf tile; several are uncertain (noted per row).
- fixture catalog_id: analogy from DATA2 (guide p.86-89): the 1x1 shelf whose
  temperature function carries that category (常温/冷蔵/冷凍).
"""
import json
import re
import sys
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / "game" / "data" / "vertical_slice.json"

AMBIENT = "small_ambient_shelf"
COLD = "small_refrigerated_shelf"
FROZEN = "small_frozen_shelf"
SHELF_FOR = {
    "bread": AMBIENT, "snacks": AMBIENT, "instant_food": AMBIENT, "books": AMBIENT,
    "stationery": AMBIENT, "electronics": AMBIENT, "daily_goods": AMBIENT, "underwear": AMBIENT,
    "cold_drink": COLD, "vegetables": COLD, "fish": COLD, "meat": COLD, "bento": COLD,
    "frozen_food": FROZEN, "ice_cream": FROZEN,
}

# (tile_x, tile_y, category, facing, reading note). facing = side customers stand on.
SHELVES = [
    (11, 0, "bread", "left", "round buns and croissant-like bread"),
    (1, 1, "snacks", "up", "heart-shaped packs over boxes; read as sweets (uncertain)"),
    (2, 1, "snacks", "up", "small colourful boxes (uncertain)"),
    (3, 1, "instant_food", "up", "colourful packets (uncertain)"),
    (1, 2, "daily_goods", "down", "tall printed boxes and white bottles"),
    (2, 2, "vegetables", "down", "oranges, lemons and grapes"),
    (3, 2, "vegetables", "down", "green onions and tomatoes"),
    (8, 1, "cold_drink", "left", "blue cans and white cartons"),
    (8, 2, "fish", "left", "whole fish and sliced fish on trays"),
    (8, 3, "meat", "left", "red meat packs"),
    (8, 4, "snacks", "left", "tall striped boxes (uncertain)"),
    (8, 5, "electronics", "left", "small blister packs (uncertain)"),
    (9, 1, "cold_drink", "right", "bottles and blue packs (uncertain)"),
    (9, 2, "meat", "right", "white trays with pink slices (uncertain)"),
    (9, 3, "fish", "right", "same picture as (8,2)"),
    (9, 4, "stationery", "right", "blue/red small packages (uncertain)"),
    (9, 5, "snacks", "right", "same picture as (8,4)"),
    (11, 1, "bread", "left", "bread loaves"),
    (11, 2, "instant_food", "left", "cup-shaped items (uncertain: cup noodles)"),
    (11, 3, "books", "left", "magazine-like covers (uncertain)"),
    (11, 4, "bento", "left", "wrapped triangular rice balls"),
    (11, 5, "cold_drink", "left", "tall bottles that look like liquor; see ALCOHOL_NOTE"),
    (11, 6, "cold_drink", "left", "sake-like bottles; see ALCOHOL_NOTE"),
    (11, 7, "cold_drink", "left", "rows of cans"),
    (1, 4, "vegetables", "up", "oranges, pineapple and onions"),
    (2, 4, "vegetables", "up", "white round items and potatoes (uncertain)"),
    (3, 4, "bread", "up", "beige bagged loaves (uncertain)"),
    (1, 5, "vegetables", "left", "same picture as (2,2)"),
    (3, 5, "daily_goods", "right", "white/blue boxes (uncertain)"),
    (1, 6, "underwear", "down", "striped packs (uncertain: socks/stockings)"),
    (2, 6, "daily_goods", "down", "same picture as (3,5)"),
    (3, 6, "underwear", "down", "same picture as (1,6)"),
    # Half a tile lower than the grid: the diagram offsets the two shelves
    # under the break room by 0.5 tile, which this client's half-tile
    # subcells represent exactly (origin y = 7 subcells).
    (5, 3.5, "frozen_food", "down", "white packs (uncertain)"),
    (6, 3.5, "ice_cream", "down", "purple/red packs (uncertain)"),
]
ALCOHOL_NOTE = (
    "The diagram shows liquor-like bottles at (11,5)/(11,6), but selling 酒類 needs the alcohol "
    "permit (CONFIRMED_OFFICIAL), which a new store does not hold; those shelves start with "
    "cold_drink instead."
)


def build(config):
    catalog = {entry["catalog_id"]: entry for entry in config["fixture_catalog"]}
    pricing = {entry["catalog_id"]: entry for entry in config["product_catalog"]}
    fixtures = [
        {
            "id": "checkout-1",
            "kind": "checkout",
            "rotation_quarter_turns": 0,
            "origin_subcell": [10, 12],
            "footprint_tiles": [2, 1],
            "interaction_subcell": [11, 11],
            "guide_tile": [5, 6],
            "guide_reading": "counter plus register machine across tiles (5,6)-(6,6)",
        },
        {
            "id": "break-room-1",
            "kind": "break_room",
            "catalog_id": "break_room_2",
            "rotation_quarter_turns": 0,
            "origin_subcell": [10, 3],
            "footprint_tiles": [2, 2],
            "interaction_subcell": [9, 4],
            "guide_tile": [5, 1.5],
            "guide_reading": "break room; the diagonal item at its top-left matches DATA2's 職員休憩室2 silhouette (PROVISIONAL)",
        },
        {
            "id": "plant-1",
            "kind": "amenity",
            "catalog_id": "potted_plant",
            "rotation_quarter_turns": 0,
            "origin_subcell": [4, 10],
            "footprint_tiles": [1, 1],
            "interaction_subcell": [0, 10],
            "guide_tile": [2, 5],
            "guide_reading": "potted plant (matches DATA2 観葉植物)",
        },
    ]
    products = []
    counts = {}
    for tile_x, tile_y, category, facing, reading in SHELVES:
        counts[category] = counts.get(category, 0) + 1
        fixture_id = "shelf-%s-%d" % (category.replace("_", "-"), counts[category])
        ox, oy = int(tile_x * 2), int(tile_y * 2)
        interaction = {
            "left": [ox - 1, oy + 1],
            "right": [ox + 2, oy + 1],
            "up": [ox + 1, oy - 1],
            "down": [ox + 1, oy + 2],
        }[facing]
        catalog_id = SHELF_FOR[category]
        fixtures.append({
            "id": fixture_id,
            "kind": "shelf",
            "catalog_id": catalog_id,
            "rotation_quarter_turns": 0,
            "origin_subcell": [ox, oy],
            "footprint_tiles": [1, 1],
            "interaction_subcell": interaction,
            "guide_tile": [tile_x, tile_y],
            "guide_reading": reading,
        })
        products.append({
            "id": "product-%s" % fixture_id[len("shelf-"):],
            "catalog_id": category,
            "fixture_id": fixture_id,
            "initial_stock_units": int(catalog[catalog_id]["capacity"]),
            "sale_price_yen": int(pricing[category]["sale_price_yen"]),
            "restock_unit_cost_yen": int(pricing[category]["restock_unit_cost_yen"]),
        })
    return {
        "scenario_id": "guide-p48-large-store-v1",
        "evidence_note": (
            "Task #89. The store every new game starts in (main.gd applies this block over the "
            "top-level prototype store, which the automated tests keep using). Floor = the "
            "CONFIRMED_OFFICIAL large store 12x8 tiles (STORE_VARIANTS large_bottom); the guide's "
            "p.48 diagram measures exactly 12x8 tiles. Fixture positions and 1x1 footprints: "
            "CONFIRMED_VISUAL from that diagram. Each shelf's product category: PROVISIONAL "
            "(this project's reading of the product pictures; per-fixture guide_reading). Shelf "
            "type: the 1x1 shelf whose DATA2 (p.86-89) temperature function carries the category. "
            "Starting stock = that shelf's CONFIRMED_OFFICIAL capacity (analogy: a newly stocked "
            "shelf starts full). Entrance: the diagram's only opening is a 2-tile walkway into the "
            "top wall at tiles 5-6; the IN/OUT mats sit side by side in it. Not placed: the "
            "diagram's cash dispenser (8,6) and copier (9,6) (no such mechanic in this client), "
            "and the outdoor parking/vending machines/plants (no outdoor lot yet). "
            "REMAKE_BALANCED_DEFAULT: which side of each shelf customers use, the register's "
            "customer side, the break-room door side, the staff posts, and the plant's unused "
            "interaction cell are this project's own choices. " + ALCOHOL_NOTE
        ),
        "store": {
            "width_tiles": 12,
            "height_tiles": 8,
            "subcells_per_tile": 2,
            "entry_subcell": [11, 0],
            "exit_subcell": [12, 0],
            "size_tier": "large",
            "size_tier_evidence_note": "See guide_starting_store.evidence_note.",
        },
        "fixtures": fixtures,
        "products": products,
        "checkout_fixture_id": "checkout-1",
        "staff_start_subcells": {"staff-1": [12, 14], "staff-2": [14, 10], "staff-3": [8, 6]},
        "customer_visit_plan_product_ids": [],
        "max_concurrent_customers": 8,
        "max_concurrent_customers_evidence_note": (
            "CONFIRMED_VISUAL lower bound: the gameplay-video frame "
            "assets/raw/conveni_additional_assets_v1/reference/video_900s.png shows about 8 "
            "customers inside one store at once (this project's count of the figures). "
            "REMAKE_BALANCED_DEFAULT: using that count as a hard cap is this project's own "
            "choice; no source states the original's limit, if any."
        ),
        "provisional_restock_product_id": products[0]["id"],
        "sample_layout_label": "Guide p.48 layout",
        # Task #97: how the staff work in the real game.
        "staff_work": {
            "restock_trigger_share_of_full": round(8 / 9, 6),
            "cleaning_task_enabled": True,
            "stamina_enabled": True,
            "evidence_note": (
                "Task #97. CONFIRMED: staff notice shelves going down and refill them on their "
                "own (docs/research/inventory-restock-boundary-2026-09-05.md section 2, exact "
                "trigger unknown), and clean the store on their own, cleaning growing 清掃 and "
                "セキュリティ (guide p.26). REMAKE_BALANCED_DEFAULT: a staff member goes to refill "
                "a shelf once it is at or below 8/9 of full (the shelf picture shows 9 items per "
                "tile, so: once it has visibly lost an item), and cleans the floor squares "
                "customers have walked on, one at a time, when there is nothing to refill. "
                "Task #99, stamina: CONFIRMED_COMMUNITY that checkout, restocking and cleaning use up "
                "体力, that at 0 a staff member rests in the break room until full, and that 敏捷性 "
                "raises the chance of recovering 2 instead of 1 (about 90% at 100); the maximum is "
                "each candidate's CONFIRMED_OFFICIAL 体力. REMAKE_BALANCED_DEFAULT: 1 per finished "
                "task, one recovery roll per game minute, +2 with chance 0.9 x 敏捷性/100."
            ),
        },
    }


def main():
    text = CONFIG.read_text(encoding="utf-8")
    config = json.loads(text)
    config.pop("guide_starting_store", None)
    block = build(config)
    # Only this one top-level key is (re)written; the rest of the file keeps
    # its hand-maintained formatting.
    start = text.find('\n  "guide_starting_store": ')
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
    text = head[:-1].rstrip() + ',\n  "guide_starting_store": ' + body + "\n}\n"
    json.loads(text)
    CONFIG.write_text(text, encoding="utf-8")
    print("wrote %d fixtures, %d products" % (len(block["fixtures"]), len(block["products"])))


if __name__ == "__main__":
    sys.exit(main())
