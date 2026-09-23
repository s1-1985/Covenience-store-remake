#!/usr/bin/env python3
"""Validate ChatGPT-isolated map asset manifest without touching game/ or Claude files.

Expected manifest schema is intentionally small and implementation-oriented:
{
  "assets": [{
    "asset_id": "...", "path": "chatgpt_map_assets/assets/...png",
    "kind": "building|terrain|road|rail|river|junction",
    "width_px": 0, "height_px": 0,
    "footprint": [rows, cols] | null,
    "direction_mask": "N|E|S|W" | null,
    "layer": "terrain|transport|building|overlay",
    "source_status": "verified|candidate|generated",
    "original_verified": true|false
  }]
}

This validator checks metadata only; PNG decode/seam checks require local bytes and are
reported separately by the future binary-asset validation step.
"""
from __future__ import annotations
import argparse, json
from collections import Counter
from pathlib import Path

ALLOWED_KINDS={"building","terrain","road","rail","river","junction"}
ALLOWED_LAYERS={"terrain","transport","building","overlay"}
ALLOWED_STATUS={"verified","candidate","generated"}
MASK_DIRS={"N","E","S","W"}
REQUIRED={"asset_id","path","kind","width_px","height_px","footprint","direction_mask","layer","source_status","original_verified"}

def validate(doc:dict)->list[str]:
    errors=[]; assets=doc.get("assets")
    if not isinstance(assets,list): return ["assets must be a list"]
    ids=[]; paths=[]
    for i,a in enumerate(assets):
        p=f"assets[{i}]"
        if not isinstance(a,dict): errors.append(f"{p}: object required"); continue
        miss=REQUIRED-set(a); errors += [f"{p}: missing {x}" for x in sorted(miss)]
        if miss: continue
        ids.append(a["asset_id"]); paths.append(a["path"])
        if a["kind"] not in ALLOWED_KINDS: errors.append(f"{p}: invalid kind")
        if a["layer"] not in ALLOWED_LAYERS: errors.append(f"{p}: invalid layer")
        if a["source_status"] not in ALLOWED_STATUS: errors.append(f"{p}: invalid source_status")
        if not isinstance(a["original_verified"],bool): errors.append(f"{p}: original_verified must be bool")
        if not (isinstance(a["width_px"],int) and a["width_px"]>0 and isinstance(a["height_px"],int) and a["height_px"]>0): errors.append(f"{p}: positive integer dimensions required")
        fp=a["footprint"]
        if fp is not None and not (isinstance(fp,list) and len(fp)==2 and all(isinstance(x,int) and x>0 for x in fp)): errors.append(f"{p}: footprint must be null or [rows,cols]")
        m=a["direction_mask"]
        if m is not None:
            parts=m.split("|") if m else []
            if not parts or len(parts)!=len(set(parts)) or set(parts)-MASK_DIRS: errors.append(f"{p}: invalid direction_mask")
        if not str(a["path"]).startswith("chatgpt_map_assets/") or ".." in Path(str(a["path"])).parts: errors.append(f"{p}: path escapes isolated root")
    for label,vals in (("asset_id",ids),("path",paths)):
        dup=[x for x,n in Counter(vals).items() if n>1]
        if dup: errors.append(f"duplicate {label}: {dup}")
    return errors

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("manifest",type=Path); ns=ap.parse_args()
    doc=json.loads(ns.manifest.read_text(encoding="utf-8")); errors=validate(doc)
    if errors:
        print("FAIL"); [print("-",e) for e in errors]; raise SystemExit(1)
    print(f"PASS: {len(doc['assets'])} manifest entries")
if __name__=="__main__": main()
