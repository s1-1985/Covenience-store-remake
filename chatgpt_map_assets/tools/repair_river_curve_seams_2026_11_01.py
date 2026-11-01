#!/usr/bin/env python3
"""Issue #232: isolated river-curve geometry candidates, NOT approved art.

Read source files only. Write only to a new directory below
chatgpt_map_assets/candidates/. Never overwrite a file or directory.
Requires Pillow. Does not modify main, game code or any source PNG.

Usage:
  python repair_river_curve_seams_2026_11_01.py REPO_ROOT \
    chatgpt_map_assets/candidates/river_seam_warp_second_pass
"""
import hashlib
import json
import math
import sys
from pathlib import Path
from PIL import Image

SOURCE = {
    "river_ne": "generated/native_copies_2026-10-15/river/map_river_ne.png",
    "river_sw": "generated/directional_2026-10-24/river/river_sw.png",
    "river_nw": "generated/directional_2026-10-24/river/river_nw.png",
    "river_es": "generated/native_copies_2026-10-15/river/map_river_es.png",
    "river_ns": "generated/native_copies_2026-10-15/river/map_river_ns.png",
    "river_ew": "generated/native_copies_2026-10-15/river/map_river_ew.png",
}
SIDES = {"river_ne": ("N", "E"), "river_sw": ("S", "W"),
         "river_nw": ("N", "W"), "river_es": ("S", "E")}

def water(p):
    r, g, b, a = p
    return b >= 180 and b > r + 25 and b > g + 8

def edge(im, side):
    coords = []
    for k in range(64):
        x = 63 if side == "E" else 0 if side == "W" else k
        y = 0 if side == "N" else 63 if side == "S" else k
        if water(im.getpixel((x, y))):
            coords.append(k)
    return {"count": len(coords),
            "min": min(coords) if coords else None,
            "max": max(coords) if coords else None,
            "center": (min(coords) + max(coords)) / 2 if coords else None}

def smooth(v):
    t = max(0., min(1., v))
    return t * t * (3. - 2. * t)

def clamp_round(v):
    return max(0, min(63, math.floor(v + 0.5)))

def warp(im, vertical, horizontal, dx, dy):
    out = Image.new("RGBA", (64, 64))
    for y in range(64):
        for x in range(64):
            dv = y if vertical == "N" else 63 - y
            dh = x if horizontal == "W" else 63 - x
            wx = smooth((36 - dv) / 36) * smooth(dh / 18)
            wy = smooth((36 - dh) / 36) * smooth(dv / 18)
            sx = clamp_round(x - dx * wx)
            sy = clamp_round(y - dy * wy)
            out.putpixel((x, y), im.getpixel((sx, sy)))
    return out

def run(repo, relative_output):
    repo = repo.resolve()
    rel = Path(relative_output)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Unsafe output path")
    output = (repo / rel).resolve()
    allowed = (repo / "chatgpt_map_assets/candidates").resolve()
    if not output.is_relative_to(allowed) or output == allowed:
        raise ValueError("Output must be under chatgpt_map_assets/candidates/")
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite: {output}")
    images, hashes = {}, {}
    for key, path in SOURCE.items():
        full = repo / "chatgpt_map_assets" / path
        hashes[key] = hashlib.sha256(full.read_bytes()).hexdigest()
        with Image.open(full) as im:
            if im.format != "PNG" or im.size != (64, 64) or im.mode != "RGBA":
                raise ValueError(f"Unexpected source image: {full}")
            im.load()
            images[key] = im.copy()
            images[key].info.update(im.info)
    outputs, records = {}, []
    for key, (vertical, horizontal) in SIDES.items():
        original = images[key]
        before_v, before_h = edge(original, vertical), edge(original, horizontal)
        target_v = edge(images["river_ns"], vertical)["center"]
        target_h = edge(images["river_ew"], horizontal)["center"]
        if before_v["center"] is None or before_h["center"] is None:
            raise ValueError(f"No water on expected side: {key}")
        dx = target_v - before_v["center"]
        dy = target_h - before_h["center"]
        candidate = warp(original, vertical, horizontal, dx, dy)
        after_v, after_h = edge(candidate, vertical), edge(candidate, horizontal)
        inactive = {s: edge(candidate, s)["count"] for s in "NESW"
                    if s not in (vertical, horizontal)}
        if (abs(after_v["center"] - target_v) > 1.5 or
                abs(after_h["center"] - target_h) > 1.5 or
                any(inactive.values())):
            raise AssertionError(f"Water centroid geometry failed: {key}")
        outputs[key] = candidate
        records.append({"asset_id": key, "source_sha256": hashes[key],
                        "shift_x_px": dx, "shift_y_px": dy,
                        "before": {vertical: before_v, horizontal: before_h},
                        "after": {vertical: after_v, horizontal: after_h},
                        "inactive_water_counts": inactive,
                        "status": "GEOMETRY_ONLY_NOT_VISUALLY_ACCEPTED"})
    output.mkdir(parents=True, exist_ok=False)
    for key, im in outputs.items():
        dest = output / (key + ".png")
        icc = images[key].info.get("icc_profile")
        im.save(dest, format="PNG", **({"icc_profile": icc} if icc else {}))
        with Image.open(dest) as check:
            check.load()
            if check.size != (64, 64) or check.mode != "RGBA" or list(check.getdata()) != list(im.getdata()):
                raise AssertionError(f"PNG roundtrip failed: {key}")
    report = {"issue": 232, "status": "CANDIDATES_NOT_ACCEPTED",
              "source_sha256": hashes, "records": records,
              "not_verified": ["original fidelity", "full scenery seam appearance",
                               "Godot 24px renderer", "functional regression"]}
    (output / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: script.py REPO_ROOT NEW_RELATIVE_OUTPUT_DIR")
    run(Path(sys.argv[1]), sys.argv[2])
