#!/usr/bin/env python3
"""Build a 52-building *requirements* catalog from Claude's actual TOWN_BUILDINGS.

This is a READ-ONLY parser of reference_sim/conveni_sim/baseline_data.py; it does
not import/execute that module, edit Claude-owned files, generate or accept any
image, or infer a town tile-pixel size. Output is explicitly an UNFULFILLED
asset checklist until individually inspected PNGs are linked and validated.

Run from the repository root, on the ChatGPT-only branch:
  python chatgpt_map_assets/tools/build_building_catalog.py

Creates chatgpt_map_assets/building_requirements.json exactly once (refuses
overwrite). Use --output chatgpt_map_assets/another-new-name.json if needed.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path

EXCLUDED_TILE_IDS = frozenset({
    "own_conveni_lot", "rival_conveni_lot", "vacant_lot", "road",
    "railway", "town_hall_lot", "inducement_lot",
})
EXPECTED_CATEGORIES = {
    "学校": 6, "役場": 3, "アミューズメント": 5, "店": 18,
    "住宅": 7, "会社": 5, "その他施設": 6, "駅": 2,
}


def parse_buildings(source: str) -> list[dict]:
    module = ast.parse(source, filename="baseline_data.py")
    matches = [
        node.value for node in module.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and (any(isinstance(t, ast.Name) and t.id == "TOWN_BUILDINGS"
                 for t in node.targets) if isinstance(node, ast.Assign)
             else isinstance(node.target, ast.Name)
             and node.target.id == "TOWN_BUILDINGS")
    ]
    if len(matches) != 1 or not isinstance(matches[0], (ast.Tuple, ast.List)):
        raise ValueError("Expected exactly one literal TOWN_BUILDINGS table")
    result = []
    for call in matches[0].elts:
        if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Name) or call.func.id != "_sg_building":
            raise ValueError("Unexpected TOWN_BUILDINGS entry; manual review required")
        if len(call.args) < 2:
            raise ValueError("Missing building ID or Japanese name")
        asset_id, label = (ast.literal_eval(arg) for arg in call.args[:2])
        fields = {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords}
        footprint = fields.get("footprint")
        category = fields.get("building_attribute")
        if not isinstance(asset_id, str) or not isinstance(label, str) or not isinstance(footprint, tuple) or len(footprint) != 2 or not all(type(v) is int and v > 0 for v in footprint):
            raise ValueError(f"Invalid record: {asset_id!r}")
        result.append({
            "asset_id": asset_id,
            "name_ja": label,
            "category_ja": category,
            "footprint_rows_cols": list(footprint),
        })
    return result


def build_catalog(source_text: str, source_path: str) -> dict:
    records = parse_buildings(source_text)
    identifiers = [r["asset_id"] for r in records]
    if len(records) != 59 or len(set(identifiers)) != 59:
        raise ValueError(f"Source changed: expected 59 unique entries, got {len(records)}")
    excluded = [r for r in records if r["asset_id"] in EXCLUDED_TILE_IDS]
    buildings = [r for r in records if r["asset_id"] not in EXCLUDED_TILE_IDS]
    if len(excluded) != 7 or len(buildings) != 52:
        raise ValueError("Missing/extra infrastructure type or building; manual review required")
    actual_categories = {name: sum(r["category_ja"] == name for r in buildings)
                         for name in EXPECTED_CATEGORIES}
    if actual_categories != EXPECTED_CATEGORIES or set(r["category_ja"] for r in buildings) != set(EXPECTED_CATEGORIES):
        raise ValueError(f"Building category counts changed: {actual_categories}")
    for row in buildings:
        # A building definition is NOT proof that a matching image exists.
        row.update({"candidate_images": [], "accepted_png": None,
                    "visual_reference_verified": False,
                    "sprite_status": "MISSING_UNVERIFIED"})
    return {
        "schema_version": 1,
        "producer": "ChatGPT",
        "scope": "building asset requirements only; no sprite is completed",
        "source_path": source_path,
        "source_sha256": hashlib.sha256(source_text.encode("utf-8")).hexdigest(),
        "source_entries": 59,
        "building_count": 52,
        "tile_type_count": 7,
        "tile_px": None,
        "categories": actual_categories,
        "buildings": buildings,
        "excluded_map_tile_types": excluded,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=Path("reference_sim/conveni_sim/baseline_data.py"))
    parser.add_argument("--output", type=Path,
                        default=Path("chatgpt_map_assets/building_requirements.json"))
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    destination = args.output.resolve()
    isolated_root = (repo / "chatgpt_map_assets").resolve()
    if not destination.is_relative_to(isolated_root) or destination == isolated_root:
        raise ValueError("Output must be exclusively under chatgpt_map_assets/")
    if args.source.resolve() == destination:
        raise ValueError("Input and output must differ")
    source = args.source.read_text(encoding="utf-8")
    document = build_catalog(source, str(args.source))
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create. Never modify an existing artifact or Claude-owned file.
    with destination.open("x", encoding="utf-8") as fh:
        json.dump(document, fh, ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"Created {destination}: 52 UNFULFILLED building requirements, 7 tile types")
    print("No images were generated, cut out, inspected, or approved.")


if __name__ == "__main__":
    main()
