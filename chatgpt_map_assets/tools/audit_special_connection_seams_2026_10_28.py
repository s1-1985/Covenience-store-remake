#!/usr/bin/env python3
"""Read-only 64px PNG edge diagnostics for issue #232 special connection candidates.
Usage: python audit_special_connection_seams_2026_10_28.py REPO_ROOT
Requires Pillow. Outputs JSON to stdout; does not write to the repository.
A numerical edge comparison is NOT a visual or Godot acceptance test.
"""
import json
import sys
from pathlib import Path
from PIL import Image

PREFIX = "chatgpt_map_assets/"
CANDIDATE_MANIFEST = PREFIX + "candidates/special_connections_2026-10-28/candidate_manifest.json"
REFERENCE = {
    "road_ew": PREFIX + "generated/native_copies_2026-10-15/road/map_road_ew.png",
    "road_ns": PREFIX + "generated/native_copies_2026-10-15/road/map_road_ns.png",
    "rail_ew": PREFIX + "generated/native_copies_2026-10-15/rail/map_rail_ew.png",
    "rail_ns": PREFIX + "generated/native_copies_2026-10-15/rail/map_rail_ns.png",
    "river_ns": PREFIX + "generated/native_copies_2026-10-15/river/map_river_ns.png",
}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}

def load_png(root, rel):
    if not rel.startswith(PREFIX) or ".." in Path(rel).parts:
        raise ValueError(f"Unsafe asset path: {rel}")
    path = root / rel
    with Image.open(path) as im:
        if im.format != "PNG" or im.size != (64, 64) or im.mode != "RGBA":
            raise ValueError(f"Unexpected PNG format/size/mode: {rel}")
        im.load()
        return im.copy()

def edge(im, side):
    if side == "N":
        return [im.getpixel((i, 0)) for i in range(64)]
    if side == "S":
        return [im.getpixel((i, 63)) for i in range(64)]
    if side == "E":
        return [im.getpixel((63, i)) for i in range(64)]
    return [im.getpixel((0, i)) for i in range(64)]

def compare(a, b):
    def mae(rows):
        return round(sum(abs(x[c] - y[c]) for x, y in rows for c in range(3)) / (len(rows) * 3), 3)
    return {
        "rgb_mae_full64": mae(list(zip(a, b))),
        "rgb_mae_center20": mae(list(zip(a[22:42], b[22:42]))),
        "alpha_mismatch_pixels": sum(x[3] != y[3] for x, y in zip(a, b)),
        "candidate_opaque_center20": sum(x[3] == 255 for x in a[22:42]),
        "reference_opaque_center20": sum(x[3] == 255 for x in b[22:42]),
    }

def run(root):
    manifest = json.loads((root / CANDIDATE_MANIFEST).read_text(encoding="utf-8"))
    refs = {name: load_png(root, rel) for name, rel in REFERENCE.items()}
    result = []
    for item in manifest["items"]:
        im = load_png(root, item["candidate_path"])
        kind = item["kind"]
        if kind == "road_bridge":
            ref = "road_ns" if item["provisional_direction_mask"] == "N|S" else "road_ew"
            sides = item["provisional_direction_mask"].split("|")
        elif kind == "rail_bridge":
            ref = "rail_ns" if item["provisional_direction_mask"] == "N|S" else "rail_ew"
            sides = item["provisional_direction_mask"].split("|")
        elif kind.startswith("river_"):
            ref, sides = "river_ns", list("NESW")
        elif kind == "rail_junction_y":
            ref, sides = None, list("NESW")
        else:
            raise ValueError(f"Unrecognized candidate kind: {kind}")
        checks = []
        for side in sides:
            target = ref or ("rail_ns" if side in "NS" else "rail_ew")
            checks.append({"candidate_side": side, "reference": target,
                           "reference_side": OPPOSITE[side],
                           **compare(edge(im, side), edge(refs[target], OPPOSITE[side]))})
        result.append({"asset_id": item["asset_id"], "status": "DIAGNOSTIC_ONLY", "checks": checks})
    return {"checked_pngs": len(result) + len(refs), "candidate_pngs": len(result),
            "edge_comparisons": sum(len(x["checks"]) for x in result),
            "results": result,
            "acceptance": "NOT_ACCEPTED: compare edge metrics with visual/original/Godot tests"}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python audit_special_connection_seams_2026_10_28.py REPO_ROOT")
    print(json.dumps(run(Path(sys.argv[1]).resolve()), ensure_ascii=False, indent=2))
