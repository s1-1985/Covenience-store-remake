#!/usr/bin/env python3
"""Issue #232: read-only audit of 57 candidate map assets.
Usage: python issue232_candidate_gate_2026_11_23.py MANIFEST.json [REPO_ROOT]
Prints JSON to stdout; never modifies source files. Nonzero exit on structural errors.
"""
import argparse
import collections
import hashlib
import json
import pathlib
import struct
import sys
import zlib

BITS = {"n": 1, "e": 2, "s": 4, "w": 8}
REQUIRED = ("asset_id", "path", "git_blob_sha", "source_id", "source_path",
            "size_px", "footprint_xy", "original_ps1_verified",
            "visual_accepted", "seam_accepted", "godot_render_verified",
            "runtime_integrated", "production_enabled")

def png_size(data):
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not PNG")
    if data[12:16] != b"IHDR" or struct.unpack(">I", data[8:12])[0] != 13:
        raise ValueError("invalid IHDR")
    if zlib.crc32(data[12:29]) & 0xffffffff != struct.unpack(">I", data[29:33])[0]:
        raise ValueError("IHDR CRC mismatch")
    return list(struct.unpack(">II", data[16:24]))

def audit(manifest, root=None):
    records = manifest.get("records", [])
    errors, warnings, verified = [], [], []
    seen = set()
    for r in records:
        ident = r.get("asset_id", "<missing>")
        for field in REQUIRED:
            if field not in r:
                errors.append(f"{ident}: missing {field}")
        if ident in seen:
            errors.append(f"{ident}: duplicate ID")
        seen.add(ident)
        if r.get("kind") == "directional":
            suffix = ident.rsplit("_", 1)[-1].lower()
            expected = sum(BITS.get(c, 0) for c in suffix)
            if not suffix or any(c not in BITS for c in suffix) or expected != r.get("mask_nesw"):
                errors.append(f"{ident}: direction mask mismatch")
            if r.get("ports", {}).get(r.get("role")) != r.get("mask_nesw"):
                errors.append(f"{ident}: port mask mismatch")
        if r.get("source_topology_unresolved"):
            warnings.append(f"{ident}: source topology unresolved")
        if any(not r.get(field, False) for field in
               ("original_ps1_verified", "visual_accepted", "seam_accepted",
                "godot_render_verified", "runtime_integrated")):
            warnings.append(f"{ident}: not production approved")
        if root is not None and "path" in r:
            path = (root / r["path"]).resolve()
            if not path.is_relative_to(root.resolve()):
                errors.append(f"{ident}: path escapes repository")
                continue
            if not path.is_file():
                warnings.append(f"{ident}: candidate PNG not locally available")
                continue
            data = path.read_bytes()
            blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            if blob != r.get("git_blob_sha"):
                errors.append(f"{ident}: Git blob SHA mismatch")
            try:
                size = png_size(data)
                if size != r.get("size_px"):
                    errors.append(f"{ident}: PNG dimensions mismatch {size}")
                else:
                    verified.append(ident)
            except ValueError as exc:
                errors.append(f"{ident}: {exc}")
    by_role = collections.Counter(r.get("role") for r in records)
    for role in ("road", "rail", "river"):
        masks = [r.get("mask_nesw") for r in records if r.get("role") == role and r.get("kind") == "directional"]
        if sorted(masks) != list(range(1, 16)):
            errors.append(f"{role}: masks 1..15 not covered exactly once")
    return {"status": "STRUCTURAL_FAIL" if errors else "CANDIDATE_ONLY_NOT_APPROVED",
            "records": len(records), "by_role": dict(by_role),
            "local_png_header_sha_verified": len(verified),
            "errors": errors, "warnings": warnings,
            "limits": ["PNG IHDR/CRC only; not full-pixel decode",
                       "No visual seam or PS1 comparison",
                       "No Godot render or regression test"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("manifest", type=pathlib.Path)
    p.add_argument("repo_root", type=pathlib.Path, nargs="?")
    a = p.parse_args()
    report = audit(json.loads(a.manifest.read_text(encoding="utf-8")), a.repo_root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0

if __name__ == "__main__":
    sys.exit(main())
