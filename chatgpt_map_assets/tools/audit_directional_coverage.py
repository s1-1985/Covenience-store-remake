#!/usr/bin/env python3
"""Audit directional coverage of map connection tiles without modifying source assets.

Reads the existing map_assets_manifest.json and derives *name-based candidate*
N/E/S/W masks from asset IDs. This is structural coverage only; it deliberately
does not claim pixel-edge/seam correctness. Output is JSON for issue #232 tasks 5/6/8.
"""
import argparse, json, re
from pathlib import Path

DIRS="nesw"
FAMILIES=("road","rail","sidewalk")
TOKEN_MASK={
 "ns":"NS","ew":"EW","ne":"NE","nw":"NW","es":"ES","se":"ES","ws":"SW","sw":"SW",
 "cross":"NESW","t_new":"NEW","t_nes":"NES","t_nsw":"NSW","t_sew":"ESW","t_wes":"ESW",
 "end_n":"N","end_e":"E","end_s":"S","end_w":"W",
 "stop_n":"N","stop_e":"E","stop_s":"S","stop_w":"W",
}
CANONICAL={
 "straight":{"NS","EW"},
 "curve":{"NE","NW","ES","SW"},
 "t":{"NES","NEW","NSW","ESW"},
 "cross":{"NESW"},
 "end":{"N","E","S","W"},
}
def mask_from_id(asset_id):
    s=asset_id.lower()
    for k in sorted(TOKEN_MASK,key=len,reverse=True):
        if re.search(r"(?:^|_)"+re.escape(k)+r"(?:_|$)",s):
            return TOKEN_MASK[k],k
    return None,None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("manifest",type=Path)
    ap.add_argument("-o","--output",type=Path,required=True)
    args=ap.parse_args()
    data=json.loads(args.manifest.read_text(encoding="utf-8"))
    rows=[]; coverage={f:set() for f in FAMILIES}
    for a in data["assets"]:
        aid=a["id"]
        fam=next((f for f in FAMILIES if aid.startswith("map_"+f+"_")),None)
        if not fam: continue
        mask,token=mask_from_id(aid)
        rows.append({"asset_id":aid,"family":fam,"candidate_mask":mask,
                     "derived_from_token":token,"visual_verified":False})
        if mask: coverage[fam].add(mask)
    gaps={}
    for fam,masks in coverage.items():
        gaps[fam]={k:sorted(v-masks) for k,v in CANONICAL.items() if v-masks}
    out={
      "schema_version":1,
      "status":"STRUCTURAL_ONLY_NOT_VISUALLY_VERIFIED",
      "warning":"Masks are inferred only from filenames. Pixel seams, actual openings, bridges/crossings and renderer behavior remain unverified.",
      "assets":rows,
      "coverage":{k:sorted(v) for k,v in coverage.items()},
      "canonical_gaps":gaps,
      "acceptance":{"task5_complete":False,"task6_complete":False,"task8_complete":False}
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"audited":len(rows),"canonical_gaps":gaps},ensure_ascii=False))
if __name__=="__main__": main()
