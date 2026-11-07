#!/usr/bin/env python3
"""Issue #232 (v2; fixes Git blob NUL delimiter): read-only real PNG quality triage for the four river T junctions.

Requires Pillow (pip install Pillow) and a local git checkout containing the
isolated branch. Reads Git objects with 'git show'; writes nothing.
Numerical seam diagnostics are NOT original-game or art acceptance.

Usage:
  python3 chatgpt_map_assets/tools/audit_river_t_edges_2026_11_07.py \
    --repo . --ref chatgpt/map-assets-isolated-20260922
  python3 chatgpt_map_assets/tools/audit_river_t_edges_2026_11_07.py --self-test
"""
import argparse
from io import BytesIO
import hashlib
import json
from pathlib import Path
import subprocess
import sys

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required: python3 -m pip install Pillow")

REGISTRY = (
    "chatgpt_map_assets/manifests/"
    "connection_45_candidate_registry_2026-10-30.json"
)
MASKS = {"river_nes": 7, "river_new": 11, "river_nsw": 13, "river_esw": 14}
REQUIRED = (*MASKS, "river_nesw", "river_ns", "river_ew", "river_ne")
SIDES = (("N", 1, "S", "river_ns"),
         ("E", 2, "W", "river_ew"),
         ("S", 4, "N", "river_ns"),
         ("W", 8, "E", "river_ew"))


def git_read(repo, ref, path):
    if not path.startswith("chatgpt_map_assets/") or ".." in Path(path).parts:
        raise ValueError("unsafe asset path: " + path)
    result = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{path}"],
        capture_output=True, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", "replace")[:300])
    return result.stdout


def blob_sha(data):
    return hashlib.sha1(
        b"blob " + str(len(data)).encode() + bytes([0]) + data
    ).hexdigest()


def load_png(data):
    with Image.open(BytesIO(data)) as check:
        if check.format != "PNG" or check.size != (64, 64):
            raise ValueError("expected 64x64 PNG")
        check.verify()  # PNG chunk integrity
    with Image.open(BytesIO(data)) as im:
        return im.convert("RGBA").copy()  # actual pixel decompression


def edge_rgb_mae(first, second, first_side, second_side, size=24):
    def coord(side, k):
        return {"N": (k, 0), "E": (63, k),
                "S": (k, 63), "W": (0, k)}[side]

    total = 0
    for i in range(size):
        k = min(63, int((i + 0.5) * 64 / size))
        a = first.getpixel(coord(first_side, k))
        b = second.getpixel(coord(second_side, k))
        total += sum(abs(a[c] - b[c]) for c in range(3))
    return round(total / (size * 3), 3)


def self_test():
    a = Image.new("RGBA", (64, 64), (10, 20, 30, 255))
    b = a.copy()
    for y in range(64):
        b.putpixel((0, y), (40, 20, 30, 255))
    assert edge_rgb_mae(a, a, "E", "W") == 0
    assert edge_rgb_mae(a, b, "E", "W") == 10
    assert edge_rgb_mae(a, b, "N", "S") == 0
    print(json.dumps({"status": "SELF_TEST_PASS", "writes": 0}))


def run(repo, ref):
    registry = json.loads(git_read(repo, ref, REGISTRY))
    by_id = {a["asset_id"]: a for a in registry["assets"]}
    if len(by_id) != 45 or any(i not in by_id for i in REQUIRED):
        raise ValueError("registry incomplete or duplicate IDs")
    images, details = {}, []
    for asset_id in REQUIRED:
        record = by_id[asset_id]
        if asset_id in MASKS and record["direction_bits_nesw"] != MASKS[asset_id]:
            raise ValueError("wrong direction mask: " + asset_id)
        raw = git_read(repo, ref, record["candidate_path"])
        actual = blob_sha(raw)
        if actual != record["git_blob_sha"]:
            raise ValueError("Git blob SHA mismatch: " + asset_id)
        images[asset_id] = load_png(raw)
        details.append({"id": asset_id, "path": record["candidate_path"],
                        "git_blob_sha": actual, "dimensions": [64, 64]})

    checks = []
    for asset_id, mask in MASKS.items():
        for side, bit, opposite, straight_id in SIDES:
            checks.append({
                "id": asset_id, "side": side, "connected": bool(mask & bit),
                "mae_vs_cross_same_side_24px": edge_rgb_mae(
                    images[asset_id], images["river_nesw"], side, side),
                "mae_vs_straight_opposite_edge_24px": edge_rgb_mae(
                    images[asset_id], images[straight_id], side, opposite),
            })
    result = {
        "issue": 232, "status": "PNG_INTEGRITY_PASS_ART_NOT_ACCEPTED",
        "decoded_pngs": len(images), "edges_checked": len(checks),
        "connected_edges": sum(x["connected"] for x in checks),
        "closed_edges": sum(not x["connected"] for x in checks),
        "assets": details, "edge_checks": checks,
        "limitations": [
            "RGB MAE is a numerical triage metric, not a visual acceptance test",
            "24px nearest-neighbor simulation is not a Godot render",
            "No original-game comparison, production integration or regression test",
        ],
        "writes": 0,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--ref", default="chatgpt/map-assets-isolated-20260922")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
        elif args.repo:
            run(args.repo, args.ref)
        else:
            parser.error("--repo is required unless --self-test is used")
    except Exception as exc:
        print(json.dumps({"status": "FAIL", "error": str(exc), "writes": 0}),
              file=sys.stderr)
        sys.exit(1)
