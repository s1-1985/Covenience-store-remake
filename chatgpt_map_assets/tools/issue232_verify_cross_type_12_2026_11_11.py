#!/usr/bin/env python3
"""Read-only integrity/decode gate for issue #232 cross-type source PNGs.

Run from a checkout containing main and chatgpt/map-assets-isolated-20260922:
  python issue232_verify_cross_type_12_2026_11_11.py --repo-root /path/to/repo
No source, checkout, branch, or output file is modified.
"""
import argparse
import hashlib
import io
import json
import pathlib
import subprocess
import sys
from PIL import Image

MANIFEST = "chatgpt_map_assets/manifests/issue232_cross_type_existing_12_readonly_2026-11-11.json"
SOURCE_PREFIX = "assets/raw/conveni_map_assets_v2/terrain/tiles_64/"
RUNTIME_PREFIX = "game/assets/town/"


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def png_dimensions(data):
    with Image.open(io.BytesIO(data)) as image:
        image.load()  # Full-pixel decode, not just IHDR/CRC metadata.
        if image.format != "PNG":
            raise ValueError("not a PNG")
        return list(image.size)


def git_read(root, ref, path):
    if ref != "main" or ".." in pathlib.PurePosixPath(path).parts or path.startswith("/"):
        raise ValueError("unsafe read-only git ref/path")
    result = subprocess.run(["git", "-C", str(root), "show", ref + ":" + path], capture_output=True)
    if result.returncode:
        raise ValueError("git show failed for " + path)
    return result.stdout


def verify(root, manifest):
    failures = []
    checked = 0
    seen = set()
    assets = manifest.get("assets", [])
    for item in assets:
        ident = item.get("asset_id", "<missing>")
        try:
            path = item["source_path"]
            sha = item["source_git_blob_sha"]
            if ident in seen or item["source_ref"] != "main" or not path.startswith(SOURCE_PREFIX):
                raise ValueError("duplicate ID, wrong source ref or unsafe source path")
            seen.add(ident)
            data = git_read(root, "main", path)
            if blob_sha(data) != sha:
                raise ValueError("source Git blob SHA mismatch")
            if png_dimensions(data) != item["size_px"]:
                raise ValueError("source PNG decoded dimensions mismatch")
            if item["runtime_copy_present"]:
                runtime_path = item["runtime_path"]
                if not runtime_path or not runtime_path.startswith(RUNTIME_PREFIX):
                    raise ValueError("bad runtime path")
                runtime_data = git_read(root, "main", runtime_path)
                if blob_sha(runtime_data) != sha:
                    raise ValueError("runtime copy differs from source")
            elif item.get("runtime_path") is not None:
                raise ValueError("unverified runtime path")
            checked += 1
        except Exception as exc:
            failures.append({"id": ident, "error": str(exc)})
    if len(assets) != 12 or len(seen) != 12:
        failures.append({"id": "manifest", "error": "expected 12 distinct assets"})
    return {"issue": 232, "checked": checked, "total": len(assets), "failures": failures,
            "status": "PNG_DECODE_PASS_NOT_ART_ACCEPTED" if not failures else "FAIL",
            "not_verified": ["original PS1 appearance", "interoperability seams", "Godot drawing", "game regression"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=pathlib.Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    report = verify(root, manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report["failures"] else 2


if __name__ == "__main__":
    sys.exit(main())
