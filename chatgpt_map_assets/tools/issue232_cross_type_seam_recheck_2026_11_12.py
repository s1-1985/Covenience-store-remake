#!/usr/bin/env python3
"""Issue #232: read-only, reproducible PNG decode and 24px seam diagnostics.

Run from isolated-branch checkout with a local main ref and Pillow installed:
  python issue232_cross_type_seam_recheck_2026_11_12.py --repo-root /path/to/repo
Writes only JSON to stdout. Never edits the checkout or Git refs.
Edge RGB MAE is a triage metric, not an acceptance threshold.
"""
import argparse
import hashlib
import io
import json
import pathlib
import subprocess
from PIL import Image

MANIFEST = "chatgpt_map_assets/manifests/issue232_cross_type_existing_12_readonly_2026-11-11.json"
PREFIX = "assets/raw/conveni_map_assets_v2/terrain/tiles_64/"
CONTROLS = {
    "map_road_ew": "96dc9c5f90d134db6096295d649ee88d45b18f3a",
    "map_road_ns": "360c16bfe0c0a874af1ffac34e42eee51ce0e7c1",
    "map_rail_ew": "17ae09cf4b389d22832dc6289804971ff53fb2fa",
    "map_rail_ns": "3ecc57989beab8f74b97a5079d14fc557de15e5b",
    "map_river_ns": "a5c0b606ce3f2653e3f0c3532eaa52211af59a53",
    "map_water_calm": "7f38c2b355344499172bd89def7b8addc48c34b5",
    "map_pond_small": "2719b0b51ece024a1b26453e73fc415e85c3147a",
}
PAIRS = [
    ("road_bridge_E", "map_road_bridge_ew", "E", "map_road_ew", "W"),
    ("road_bridge_W", "map_road_bridge_ew", "W", "map_road_ew", "E"),
    ("road_bridge_N", "map_road_bridge_ns", "N", "map_road_ns", "S"),
    ("road_bridge_S", "map_road_bridge_ns", "S", "map_road_ns", "N"),
    ("rail_bridge_E", "map_rail_bridge_ew", "E", "map_rail_ew", "W"),
    ("rail_bridge_W", "map_rail_bridge_ew", "W", "map_rail_ew", "E"),
    ("rail_bridge_N", "map_rail_bridge_ns", "N", "map_rail_ns", "S"),
    ("rail_bridge_S", "map_rail_bridge_ns", "S", "map_rail_ns", "N"),
    ("river_mouth_s_N", "map_river_mouth_s", "N", "map_river_ns", "S"),
    ("river_mouth_s_S", "map_river_mouth_s", "S", "map_water_calm", "N"),
    ("river_mouth_square_N", "map_river_mouth_s_square", "N", "map_river_ns", "S"),
    ("river_mouth_square_S", "map_river_mouth_s_square", "S", "map_water_calm", "N"),
    ("pond_channel_s_N", "map_pond_channel_s", "N", "map_river_ns", "S"),
    ("pond_channel_s_S", "map_pond_channel_s", "S", "map_pond_small", "N"),
    ("inlet_w_W", "map_inlet_w", "W", "map_water_calm", "E"),
    ("road_EW_self", "map_road_ew", "E", "map_road_ew", "W"),
    ("road_NS_self", "map_road_ns", "N", "map_road_ns", "S"),
    ("rail_EW_self", "map_rail_ew", "E", "map_rail_ew", "W"),
    ("rail_NS_self", "map_rail_ns", "N", "map_rail_ns", "S"),
    ("river_NS_self", "map_river_ns", "N", "map_river_ns", "S"),
]


def read_main(root, asset_id, expected_sha):
    if not asset_id.startswith("map_") or not asset_id.replace("_", "").isalnum():
        raise ValueError("unsafe asset ID")
    source_path = PREFIX + asset_id + ".png"
    data = subprocess.run(["git", "-C", str(root), "show", "main:" + source_path],
                          capture_output=True, check=True).stdout
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if blob != expected_sha:
        raise ValueError("Git blob SHA mismatch: " + asset_id)
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        if image.format != "PNG" or image.size != (64, 64) or image.mode != "RGBA":
            raise ValueError("unexpected PNG format: " + asset_id)
        rgba = image.copy()
    alpha = list(rgba.getchannel("A").getdata())
    return rgba, {"id": asset_id, "sha": blob, "bytes": len(data), "rgba_pixels": 4096,
                  "alpha": {"transparent": alpha.count(0), "partial": sum(0 < a < 255 for a in alpha),
                            "opaque": alpha.count(255)}}


def seam(a, edge_a, b, edge_b):
    def coord(edge, sample):
        return {"N": (sample, 0), "S": (sample, 63), "W": (0, sample), "E": (63, sample)}[edge]
    rgb_sum = alpha_sum = exact = alpha_mismatch = 0
    for i in range(24):
        sample = int((i + 0.5) * 64 / 24)
        pa = a.getpixel(coord(edge_a, sample))
        pb = b.getpixel(coord(edge_b, sample))
        rgb_sum += sum(abs(x-y) for x, y in zip(pa[:3], pb[:3]))
        diff = abs(pa[3]-pb[3])
        alpha_sum += diff
        alpha_mismatch += bool(diff)
        exact += pa == pb
    return {"rgb_mae": round(rgb_sum/72, 3), "alpha_mae": round(alpha_sum/24, 3),
            "exact_rgba_samples": exact, "alpha_mismatched_samples": alpha_mismatch}


def run(root):
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    sources = {a["asset_id"]: a["source_git_blob_sha"] for a in manifest["assets"]}
    if len(sources) != 12 or set(sources).intersection(CONTROLS):
        raise ValueError("expected 12 distinct cross-type assets")
    sources.update(CONTROLS)
    images, assets, failures = {}, [], []
    for asset_id, sha in sources.items():
        try:
            images[asset_id], metadata = read_main(root, asset_id, sha)
            assets.append(metadata)
        except Exception as exc:
            failures.append({"id": asset_id, "error": str(exc)})
    seams = []
    for label, a, ea, b, eb in PAIRS:
        result = seam(images[a], ea, images[b], eb) if a in images and b in images else {"error": "image missing"}
        seams.append({"label": label, "tile_a": a, "edge_a": ea, "tile_b": b, "edge_b": eb, **result})
    return {"issue": 232, "checked": len(assets), "expected": 19, "failures": failures,
            "assets": assets, "seams": seams,
            "limitations": ["Edge MAE is diagnostic, not visual approval",
                            "Some neighbor pairs are filename-derived hypotheses",
                            "PS1 fidelity, Godot rendering and regression remain unverified"]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=pathlib.Path, required=True)
    args = parser.parse_args()
    report = run(args.repo_root.resolve())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    raise SystemExit(0 if not report["failures"] else 1)
