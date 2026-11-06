#!/usr/bin/env python3
"""Issue #232: read-only, cross-ref Git blob + real PNG pixel-decode audit.

Requires Python 3 stdlib and a local git repository with both refs available.
Writes no files. Does not check PS1 fidelity, seams, Godot, or game regression.
Usage:
 python3 chatgpt_map_assets/tools/verify_connection_45_cross_ref_2026_11_06.py \
   --repo . --main-ref main \
   --candidate-ref chatgpt/map-assets-isolated-20260922
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
import zlib
from pathlib import Path

PREFIX = "chatgpt_map_assets/"
PROVENANCE = PREFIX + "audits/connection_45_cross_branch_provenance_2026-11-06.json"
PNG_SIG = b"\x89PNG\r\n\x1a\n"


def git_show(repo, ref, path):
    if not path or path.startswith("/") or ".." in Path(path).parts:
        raise ValueError("unsafe repository path: " + path)
    result = subprocess.run(
        ["git", "-C", str(repo), "show", ref + ":" + path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if result.returncode:
        raise ValueError("git show failed for " + ref + ":" + path +
                         ": " + result.stderr.decode("utf-8", "replace")[:300])
    return result.stdout


def blob_sha(data):
    header = b"blob " + str(len(data)).encode("ascii") + b"\0"
    return hashlib.sha1(header + data).hexdigest()


def decode_png(data):
    if not data.startswith(PNG_SIG):
        raise ValueError("not a PNG")
    pos, chunks, idat = len(PNG_SIG), [], bytearray()
    width = height = depth = color = interlace = None
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError("truncated chunk header")
        length = struct.unpack_from(">I", data, pos)[0]
        end = pos + 12 + length
        if end > len(data):
            raise ValueError("truncated chunk data")
        typ = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        stored = struct.unpack_from(">I", data, pos + 8 + length)[0]
        actual = zlib.crc32(typ + payload) & 0xffffffff
        if actual != stored:
            raise ValueError("PNG CRC mismatch: " + repr(typ))
        chunks.append(typ.decode("ascii", "replace"))
        if typ == b"IHDR":
            if length != 13 or width is not None:
                raise ValueError("invalid IHDR")
            width, height, depth, color, comp, filt, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if comp or filt:
                raise ValueError("unsupported compression/filter method")
        elif typ == b"IDAT":
            idat.extend(payload)
        elif typ == b"IEND":
            if length or end != len(data):
                raise ValueError("invalid IEND or trailing bytes")
            break
        pos = end
    if not chunks or chunks[-1] != "IEND":
        raise ValueError("missing IEND")
    if not width or not height or depth != 8 or color not in (2, 6) or interlace:
        raise ValueError("requires noninterlaced 8-bit RGB or RGBA PNG")
    channels = 4 if color == 6 else 3
    stride = width * channels
    raw = zlib.decompress(bytes(idat))
    if len(raw) != height * (stride + 1):
        raise ValueError("decompressed scanline size mismatch")
    prior = bytearray(stride)
    for y in range(height):
        start = y * (stride + 1)
        filt = raw[start]
        row = bytearray(raw[start + 1:start + 1 + stride])
        if filt not in range(5):
            raise ValueError("invalid scanline filter")
        for i in range(stride):
            left = row[i - channels] if i >= channels else 0
            up = prior[i]
            upper_left = prior[i - channels] if i >= channels else 0
            if filt == 1:
                predictor = left
            elif filt == 2:
                predictor = up
            elif filt == 3:
                predictor = (left + up) // 2
            elif filt == 4:
                p = left + up - upper_left
                distances = (abs(p - left), abs(p - up), abs(p - upper_left))
                predictor = (left, up, upper_left)[distances.index(min(distances))]
            else:
                predictor = 0
            row[i] = (row[i] + predictor) & 255
        prior = row
    return {"width": width, "height": height, "channels": channels,
            "decoded_pixels": width * height}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--main-ref", default="main")
    ap.add_argument("--candidate-ref", default="chatgpt/map-assets-isolated-20260922")
    args = ap.parse_args()
    try:
        report = json.loads(git_show(args.repo, args.candidate_ref, PROVENANCE))
        records = report["records"]
        if len(records) != 45 or len({r["asset_id"] for r in records}) != 45:
            raise ValueError("expected 45 unique assets")
        failures, checked = [], 0
        for rec in records:
            for kind, ref, path_key, sha_key in (
                ("source", args.main_ref, "source_path", "source_git_blob_sha"),
                ("candidate", args.candidate_ref, "candidate_path", "candidate_git_blob_sha"),
            ):
                try:
                    data = git_show(args.repo, ref, rec[path_key])
                    sha = blob_sha(data)
                    if sha != rec[sha_key]:
                        raise ValueError("Git blob SHA mismatch")
                    png = decode_png(data)
                    if png["width"] != 64 or png["height"] != 64:
                        raise ValueError("expected 64x64, got " + str(png))
                    checked += 1
                except Exception as exc:
                    failures.append({"asset_id": rec["asset_id"], "kind": kind,
                                     "error": str(exc)})
        print(json.dumps({
            "issue": 232, "status": "PASS" if not failures else "FAIL",
            "source_and_candidate_pngs_checked": checked,
            "expected_pngs": 90, "errors": failures,
            "acceptance": "PNG_DECODE_AND_GIT_BLOB_ONLY_NOT_ART_ACCEPTED",
            "writes": 0
        }, ensure_ascii=False, indent=2))
        return 0 if not failures and checked == 90 else 1
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc),
                          "writes": 0}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
