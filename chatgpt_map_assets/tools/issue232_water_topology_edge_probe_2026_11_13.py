#!/usr/bin/env python3
"""Read-only issue #232 water-edge profile for candidate 64px PNGs.

Run in an isolated checkout with local main ref and Pillow:
  python chatgpt_map_assets/tools/issue232_water_topology_edge_probe_2026_11_13.py --repo-root /path/to/repo
No writes. This is palette-based triage, NOT visual or PS1 acceptance.
"""
import argparse
import json
from pathlib import Path
from PIL import Image
from issue232_cross_type_seam_recheck_2026_11_12 import MANIFEST, CONTROLS, read_main

TARGETS = (
    "map_river_ns", "map_water_calm", "map_pond_small", "map_road_ew",
    "map_road_bridge_ew", "map_road_bridge_ns", "map_rail_bridge_ew",
    "map_rail_bridge_ns", "map_river_mouth_s", "map_river_mouth_s_square",
    "map_pond_channel_s", "map_inlet_w",
)
# Hypotheses in the 2026-11-13 fixture; never assume they are correct.
PROPOSED = (
    ("pond_channel_N_to_river_S", "map_pond_channel_s", "N", "map_river_ns", "S"),
    ("pond_channel_S_to_pond_N", "map_pond_channel_s", "S", "map_pond_small", "N"),
    ("river_mouth_N_to_river_S", "map_river_mouth_s", "N", "map_river_ns", "S"),
    ("river_mouth_S_to_sea_N", "map_river_mouth_s", "S", "map_water_calm", "N"),
    ("inlet_W_to_sea_E", "map_inlet_w", "W", "map_water_calm", "E"),
)

def is_blue_water(pixel):
    """Heuristic for this candidate palette; not a general semantic classifier."""
    r, g, b, a = pixel
    return a >= 200 and b >= r + 25 and b >= g + 12 and b >= 95

def edge_pixels(image, side):
    if image.size != (24, 24):
        raise ValueError("Expected nearest-neighbor 24px image")
    if side == "N":
        return [image.getpixel((x, 0)) for x in range(24)]
    if side == "S":
        return [image.getpixel((x, 23)) for x in range(24)]
    if side == "E":
        return [image.getpixel((23, y)) for y in range(24)]
    if side == "W":
        return [image.getpixel((0, y)) for y in range(24)]
    raise ValueError("Invalid edge")

def profile(image, side):
    bits = [int(is_blue_water(p)) for p in edge_pixels(image, side)]
    runs, start = [], None
    for i, bit in enumerate(bits + [0]):
        if bit and start is None:
            start = i
        elif not bit and start is not None:
            runs.append([start, i - 1])
            start = None
    return {"water_pixels": sum(bits), "water_fraction": round(sum(bits) / 24, 4),
            "water_runs_inclusive": runs, "water_bitmask_24": "".join(map(str, bits))}

def check_pair(images, label, aid, aside, bid, bside):
    left = [is_blue_water(p) for p in edge_pixels(images[aid], aside)]
    right = [is_blue_water(p) for p in edge_pixels(images[bid], bside)]
    overlap = sum(a and b for a, b in zip(left, right))
    disagreement = sum(a != b for a, b in zip(left, right))
    union = sum(a or b for a, b in zip(left, right))
    return {"hypothesis": label, "tile_a": aid, "edge_a": aside,
            "tile_b": bid, "edge_b": bside, "water_overlap_px": overlap,
            "water_disagreement_px": disagreement,
            "water_iou": round(overlap / union, 4) if union else None,
            "warning": "Palette heuristic only; no original-PS1 acceptance"}

def run(root):
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    known = {a["asset_id"]: a["source_git_blob_sha"] for a in manifest["assets"]}
    if len(known) != 12 or set(known).intersection(CONTROLS):
        raise ValueError("Unexpected source manifest")
    known.update(CONTROLS)
    images = {}
    for aid in TARGETS:
        rgba, _ = read_main(root, aid, known[aid])
        images[aid] = rgba.resize((24, 24), Image.Resampling.NEAREST)
    profiles = {aid: {side: profile(im, side) for side in "NESW"}
                for aid, im in images.items()}
    controls = {"water_calm_N": profiles["map_water_calm"]["N"]["water_fraction"],
                "road_ew_N": profiles["map_road_ew"]["N"]["water_fraction"]}
    calibrated = controls["water_calm_N"] >= 0.75 and controls["road_ew_N"] <= 0.25
    return {"issue": 232, "status": "DIAGNOSTIC_NOT_APPROVED",
            "read_only": True, "verified_png_count": len(images),
            "tile_px": 24, "water_rule": "a>=200 and b>=r+25 and b>=g+12 and b>=95",
            "palette_control_values": controls, "palette_controls_pass": calibrated,
            "profiles": profiles,
            "hypotheses": [check_pair(images, *p) for p in PROPOSED],
            "limitations": ["Water-color threshold may miss foam, shadows or blue non-water",
                            "Pair hypotheses are from fixtures, not proven topology",
                            "No Godot render, original PS1 comparison, or regression test"]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo_root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result["palette_controls_pass"] else 2)
