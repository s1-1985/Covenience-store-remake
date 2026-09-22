#!/usr/bin/env python3
"""Extract REVIEWED crop rectangles, without touching sources or Claude's files.

Requires Pillow. Usage:
  python chatgpt_map_assets/tools/extract_crops.py \
    --plan chatgpt_map_assets/crop_plan.json \
    --sources /path/to/read_only_conversation_images \
    --output /path/to/isolated_chatgpt_png_output

No resampling, guessed slicing, destructive overwrite, or replacement of
transparency. A crop is CANDIDATE until manually reviewed and tested.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from PIL import Image

SAFE_NAME = re.compile(r"^[a-z][a-z0-9_-]{1,79}$")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def within(root: Path, relative: str) -> Path:
    """Reject absolute paths and any traversal outside root."""
    p = Path(relative)
    if p.is_absolute() or not relative or ".." in p.parts:
        raise ValueError(f"unsafe relative path: {relative!r}")
    target = (root / p).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes root: {relative!r}")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--sources", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    sources, output = args.sources.resolve(), args.output.resolve()
    if not sources.is_dir():
        raise ValueError(f"missing source folder: {sources}")
    if sources == output or sources in output.parents or output in sources.parents:
        raise ValueError("source and output directories must be disjoint")
    if not isinstance(plan.get("crops"), list) or not plan["crops"]:
        raise ValueError("plan must contain nonempty reviewed crops array")
    if output.exists() and any(output.iterdir()):
        raise FileExistsError("output must be a NEW empty folder, never overwrite")

    # Preflight ALL items before writing anything. Crops use half-open boxes:
    # [left, upper, right, lower], in SOURCE pixels, not scaled preview pixels.
    tasks = []
    ids = set()
    for item in plan["crops"]:
        asset_id = item["asset_id"]
        if not SAFE_NAME.fullmatch(asset_id) or asset_id in ids:
            raise ValueError(f"invalid or duplicate asset_id: {asset_id!r}")
        ids.add(asset_id)
        source_path = within(sources, item["source_file"])
        if source_path.suffix.lower() != ".png" or not source_path.is_file():
            raise ValueError(f"source must be a local PNG: {source_path}")
        box = item["box_px"]
        if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
            raise ValueError(f"{asset_id}: box_px requires four integer coordinates")
        left, top, right, bottom = box
        with Image.open(source_path) as im:
            size = im.size
            if not (0 <= left < right <= size[0] and 0 <= top < bottom <= size[1]):
                raise ValueError(f"{asset_id}: crop {box} outside {size}")
            # No assumption of square tiles or known town pixels. Footprint
            # is only valid if corroborated; never infer from crop dimensions.
            fp = item.get("footprint_rows_cols")
            if fp is not None and (not isinstance(fp, list) or len(fp) != 2 or
                                any(type(v) is not int or v < 1 for v in fp)):
                raise ValueError(f"{asset_id}: invalid footprint")
        tasks.append((asset_id, source_path, tuple(box), fp, item))

    output.mkdir(parents=True, exist_ok=True)
    entries = []
    for asset_id, source_path, box, footprint, item in tasks:
        result = output / f"{asset_id}.png"
        # use mode 'x' to fail on collision even if another process interferes
        with Image.open(source_path) as im:
            crop = im.crop(box)
            # Preserve the input's exact pixel color/alpha; do NOT invent
            # transparent backgrounds by deleting black/white shared colors.
            with result.open("xb") as fh:
                crop.save(fh, format="PNG", optimize=False)
        entries.append({
            "asset_id": asset_id,
            "file": result.name,
            "size_px": [box[2] - box[0], box[3] - box[1]],
            "footprint_rows_cols": footprint,
            "source_file": item["source_file"],
            "source_sha256": sha256(source_path),
            "crop_box_px": list(box),
            "output_sha256": sha256(result),
            "view": item.get("view", "UNVERIFIED"),
            "quality_status": "CANDIDATE_UNREVIEWED",
            "provenance": "ChatGPT isolated extraction; not source-game capture",
        })
    manifest = output / "manifest.candidates.json"
    with manifest.open("x", encoding="utf-8") as fh:
        json.dump({"schema_version": 1, "tile_px": None, "assets": entries}, fh,
                  ensure_ascii=False, indent=2)
        fh.write("\n")
    print(f"EXTRACTED {len(entries)} candidate PNGs in {output}; no source modified")
    print("NOT ACCEPTED: visual, footprint and adjacency tests still required")


if __name__ == "__main__":
    main()
