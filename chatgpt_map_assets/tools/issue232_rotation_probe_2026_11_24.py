#!/usr/bin/env python3
"""Read-only exact-rotation audit for issue #232 unresolved PNG candidates.
Usage: python issue232_rotation_probe_2026_11_24.py MANIFEST REPO_ROOT
Requires Pillow; prints JSON. Does not modify repository files.
"""
import hashlib, json, sys
from pathlib import Path
from PIL import Image, ImageChops

def load(root, path, expected_sha):
    p = (root / path).resolve()
    if not p.is_relative_to(root.resolve()):
        raise ValueError("path escapes repository")
    raw = p.read_bytes()
    sha = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
    if sha != expected_sha:
        raise ValueError("Git blob SHA mismatch")
    with Image.open(p) as im:
        im.load()
        return im.convert("RGBA")

def audit(manifest, root):
    rows = []
    for r in manifest["records"]:
        if not r.get("source_topology_unresolved"):
            continue
        row = {"asset_id": r["asset_id"], "source_id": r["source_id"],
               "declared_mask": r.get("mask_nesw"), "status": "UNVERIFIED"}
        try:
            src = load(root, r["source_path"], r["source_git_blob_sha"])
            dst = load(root, r["path"], r["git_blob_sha"])
            row["exact_ccw_rotations"] = [
                deg for deg in (0, 90, 180, 270)
                if src.size == dst.size and
                ImageChops.difference(src.rotate(deg, expand=False), dst).getbbox() is None
            ]
            row["candidate_size"] = list(dst.size)
            row["status"] = "PIXELS_COMPARED_TOPOLOGY_UNVERIFIED"
        except (OSError, ValueError, KeyError) as e:
            row["error"] = str(e)
        rows.append(row)
    return {"status": "PIXEL_AUDIT_ONLY_NOT_APPROVED", "records": rows,
            "unverified": sum(r["status"] == "UNVERIFIED" for r in rows),
            "limits": ["Exact rotation does not prove topology or original PS1 fidelity",
                       "No seam acceptance, Godot render, or gameplay regression"]}

if __name__ == "__main__":
    manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    report = audit(manifest, Path(sys.argv[2]).resolve())
    print(json.dumps(report, indent=2, ensure_ascii=False))
    sys.exit(2 if report["unverified"] else 0)
