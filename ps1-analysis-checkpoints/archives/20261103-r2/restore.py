#!/usr/bin/env python3
"""Verify or restore a split ZIP using only Python's standard library."""
import argparse
import hashlib
import json
from pathlib import Path

def process(manifest, read_part, output=None):
    if manifest.get("format") != "split-zip-v1":
        raise ValueError("unsupported manifest")
    parts = manifest["parts"]
    if len(parts) != manifest["part_count"]:
        raise ValueError("part count mismatch")
    full, total = hashlib.sha256(), 0
    for index, part in enumerate(parts):
        expected_path = "parts/part-" + str(index).zfill(4) + ".bin"
        if part["index"] != index or part["path"] != expected_path:
            raise ValueError("invalid part order or path")
        data = read_part(part)
        if len(data) != part["bytes"]:
            raise ValueError("part size mismatch: " + part["path"])
        if hashlib.sha256(data).hexdigest() != part["sha256"]:
            raise ValueError("part SHA-256 mismatch: " + part["path"])
        git_sha = hashlib.sha1(("blob " + str(len(data)) + "\0").encode() + data).hexdigest()
        if git_sha != part["git_blob_sha1"]:
            raise ValueError("part Git blob mismatch: " + part["path"])
        full.update(data)
        total += len(data)
        if output is not None:
            output.write(data)
    if total != manifest["bytes"] or full.hexdigest() != manifest["sha256"]:
        raise ValueError("whole archive mismatch")
    return {"bytes": total, "sha256": full.hexdigest(), "parts_verified": len(parts)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restore", metavar="OUTPUT_ZIP",
                        help="restore ZIP to a new file; existing files are never overwritten")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    manifest = json.loads((base / "manifest.json").read_text(encoding="utf-8"))
    def read_part(part):
        return (base / part["path"]).read_bytes()
    output = None
    if args.restore:
        path = Path(args.restore)
        output = path.open("xb")
        try:
            result = process(manifest, read_part, output)
        except BaseException:
            output.close()
            path.unlink()
            raise
        else:
            output.close()
    else:
        result = process(manifest, read_part)
    result["mode"] = "restore" if args.restore else "verify-only"
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
