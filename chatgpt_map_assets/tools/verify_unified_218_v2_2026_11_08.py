#!/usr/bin/env python3
"""Read-only verification of the 218-record issue #232 registry.
Requires: Python 3.10+, Pillow, local git checkout with main and isolated refs.
No checkout, branch update, or tracked-file write is performed.
"""
import argparse
import hashlib
import io
import json
import pathlib
import re
import struct
import subprocess
import sys
import zlib
from PIL import Image

BRANCH = "chatgpt/map-assets-isolated-20260922"
REGISTRY = "chatgpt_map_assets/manifests/issue232_unified_218_readonly_registry_2026-11-08.json"
COUNTS = {"building": 52, "terrain": 121, "connection_candidate": 45}
MAGIC = b"\x89PNG\r\n\x1a\n"

def git_bytes(root, ref, path):
    if ref not in ("main", BRANCH) or not re.fullmatch(r"[A-Za-z0-9_./-]+", path) or ".." in pathlib.PurePosixPath(path).parts:
        raise ValueError("unsafe git ref/path")
    proc = subprocess.run(["git", "-C", str(root), "show", ref + ":" + path], capture_output=True)
    if proc.returncode:
        raise RuntimeError("git show failed: " + ref + ":" + path)
    return proc.stdout

def check_png(data, expected_sha, expected_size=None):
    sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    if sha != expected_sha or not data.startswith(MAGIC):
        raise ValueError("blob SHA or PNG signature mismatch")
    pos = len(MAGIC)
    ended = False
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError("truncated PNG")
        n = struct.unpack(">I", data[pos:pos+4])[0]
        typ = data[pos+4:pos+8]
        end = pos + n + 12
        if end > len(data):
            raise ValueError("truncated PNG chunk")
        if zlib.crc32(data[pos+4:pos+8+n]) & 0xffffffff != struct.unpack(">I", data[pos+8+n:end])[0]:
            raise ValueError("PNG CRC mismatch")
        if typ == b"IEND":
            ended = True
        pos = end
    if not ended:
        raise ValueError("missing IEND")
    with Image.open(io.BytesIO(data)) as im:
        im.load()
        size = list(im.size)
    if expected_size is not None and size != expected_size:
        raise ValueError("PNG dimensions mismatch")
    return size

def run(root):
    manifest = json.loads((root / REGISTRY).read_text(encoding="utf-8"))
    records = manifest["records"]
    errors = []
    counts = {k: 0 for k in COUNTS}
    ids = set()
    masks = {k: set() for k in ("road", "rail", "river")}
    passed = 0
    for row in records:
        name, group = row["id"], row["group"]
        try:
            if name in ids or group not in COUNTS:
                raise ValueError("duplicate ID or invalid group")
            ids.add(name)
            counts[group] += 1
            if row["ref"] != (BRANCH if group == "connection_candidate" else "main"):
                raise ValueError("wrong source branch")
            if row["display_size_px"] != [n * 24 for n in row["footprint_xy"]]:
                raise ValueError("wrong renderer footprint")
            if row["visual_accepted"] is not False or row["source_original_verified"] is not False:
                raise ValueError("unverified art marked accepted")
            if group == "connection_candidate":
                kind, mask = row["category"], row["direction_bits_nesw"]
                if kind not in masks or mask in masks[kind] or mask not in range(1, 16):
                    raise ValueError("invalid or duplicate direction mask")
                masks[kind].add(mask)
                if row["production_enabled"] is not False:
                    raise ValueError("unapproved art enabled")
            data = git_bytes(root, row["ref"], row["path"])
            check_png(data, row["git_blob_sha"], [row["width_px"], row["height_px"]])
            if group == "connection_candidate":
                source = git_bytes(root, row["source_ref"], row["source_path"])
                check_png(source, row["source_git_blob_sha"])
            passed += 1
        except Exception as exc:
            errors.append(name + ": " + str(exc))
    if len(records) != 218 or counts != COUNTS:
        errors.append("registry count mismatch: " + str(counts))
    for kind, found in masks.items():
        if found != set(range(1, 16)):
            errors.append("incomplete " + kind + " masks")
    return {"issue": 232, "status": "PASS_PNG_DECODE_ONLY_NOT_ART_ACCEPTED" if not errors else "FAIL", "passed": passed, "total": len(records), "errors": errors, "read_only": True, "not_verified": ["original PS1 fidelity", "visual seams", "Godot renderer", "game regression"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=pathlib.Path)
    args = parser.parse_args()
    result = run(args.repo_root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not result["errors"] else 2

if __name__ == "__main__":
    sys.exit(main())
