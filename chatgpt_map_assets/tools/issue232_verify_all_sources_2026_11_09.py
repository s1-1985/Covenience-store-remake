#!/usr/bin/env python3
"""Issue #232 read-only verifier: 218 assets + 121 native crops + 45 source PNGs.

Run: python issue232_verify_all_sources_2026_11_09.py --repo-root /path/to/clone
Requires refs 'main' and 'chatgpt/map-assets-isolated-20260922' locally.
No checkout, tracked-file modification or GitHub writes. This verifies file
integrity, NOT PS1 fidelity, visual seams, Godot or game regression.
"""
import argparse
import json
import pathlib
import re
import struct
import subprocess
import sys
import zlib

BRANCH = "chatgpt/map-assets-isolated-20260922"
MANIFEST = "chatgpt_map_assets/manifests/issue232_unified_218_readonly_registry_2026-11-08.json"
MAGIC = b"\x89PNG\r\n\x1a\n"
SAFE_PATH = re.compile(r"^[A-Za-z0-9_./-]+$")

def git(root, *args):
    p = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if p.returncode:
        raise RuntimeError("git " + " ".join(args[:2]) + ": " + p.stderr.decode("utf-8", "replace")[:250])
    return p.stdout

def tree_map(root, ref):
    result = {}
    for entry in git(root, "ls-tree", "-rz", ref).split(b"\0"):
        if entry:
            header, path = entry.split(b"\t", 1)
            mode, kind, sha = header.split(b" ")
            if kind == b"blob":
                result[path.decode("utf-8")] = sha.decode("ascii")
    return result

def png_info(data):
    if not data.startswith(MAGIC):
        raise ValueError("invalid PNG signature")
    pos, dims, idats, ended = 8, None, [], False
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError("truncated chunk header")
        n = struct.unpack_from(">I", data, pos)[0]
        kind = data[pos + 4:pos + 8]
        end = pos + 12 + n
        if end > len(data):
            raise ValueError("truncated PNG chunk")
        payload = data[pos + 8:pos + 8 + n]
        crc = struct.unpack_from(">I", data, pos + 8 + n)[0]
        if zlib.crc32(kind + payload) & 0xffffffff != crc:
            raise ValueError("PNG CRC mismatch")
        if kind == b"IHDR":
            if dims is not None or n != 13:
                raise ValueError("invalid IHDR")
            w, h, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if not w or not h or compression or filtering or interlace not in (0, 1):
                raise ValueError("invalid IHDR fields")
            dims = [w, h]
        if kind == b"IDAT":
            idats.append(payload)
        if kind == b"IEND":
            if n:
                raise ValueError("invalid IEND")
            ended = True
            if end != len(data):
                raise ValueError("trailing PNG bytes")
        pos = end
    if not (dims and idats and ended):
        raise ValueError("missing IHDR/IDAT/IEND")
    stream = zlib.decompressobj()
    decoded = stream.decompress(b"".join(idats)) + stream.flush()
    if not stream.eof or stream.unused_data:
        raise ValueError("invalid IDAT zlib stream")
    return dims, len(decoded)

def run(root):
    rows = json.loads(git(root, "show", BRANCH + ":" + MANIFEST))["records"]
    trees = {"main": tree_map(root, "main"), BRANCH: tree_map(root, BRANCH)}
    checks = []
    for row in rows:
        checks.append((row["id"], "asset", row["ref"], row["path"], row["git_blob_sha"], [row["width_px"], row["height_px"]]))
        if row["group"] == "terrain":
            checks.append((row["id"], "native_source", "main", row["native_source_path"], row["native_source_sha"], row["native_source_size"]))
        if row["group"] == "connection_candidate":
            checks.append((row["id"], "direction_source", row["source_ref"], row["source_path"], row["source_git_blob_sha"], None))
    errors, counts, verified, cache = [], {}, 0, {}
    for ident, kind, ref, path, sha, dims in checks:
        counts[kind] = counts.get(kind, 0) + 1
        try:
            if ref not in trees or not SAFE_PATH.fullmatch(path) or ".." in pathlib.PurePosixPath(path).parts:
                raise ValueError("unsafe ref/path")
            if trees[ref].get(path) != sha:
                raise ValueError("tree SHA mismatch or missing path")
            if sha not in cache:
                cache[sha] = png_info(git(root, "cat-file", "blob", sha))
            size, _ = cache[sha]
            if dims is not None and size != dims:
                raise ValueError("PNG dimensions mismatch: " + str(size))
            verified += 1
        except Exception as exc:
            errors.append({"id": ident, "kind": kind, "path": path, "error": str(exc)})
    if len(rows) != 218 or counts != {"asset": 218, "native_source": 121, "direction_source": 45}:
        errors.append({"error": "registry count mismatch", "counts": counts})
    return {"issue": 232, "checks": len(checks), "verified": verified, "by_kind": counts,
            "unique_png_blobs_checked": len(cache), "errors": errors,
            "status": "PASS_FILE_INTEGRITY_ONLY" if not errors else "FAIL",
            "not_tested": ["full pixel decode", "visual seams", "PS1 fidelity", "Godot", "game regression"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True, type=pathlib.Path)
    args = ap.parse_args()
    result = run(args.repo_root.resolve())
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if not result["errors"] else 2

if __name__ == "__main__":
    sys.exit(main())
