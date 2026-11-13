#!/usr/bin/env python3
"""Issue #232: make 12 focused 24px cross-type fixture PNGs (candidate-only).

Run from an isolated-branch checkout (local main ref and Pillow required):
  python chatgpt_map_assets/tools/issue232_cross_type_fixtures_2026_11_13.py \
    --repo-root /path/to/repo --output-name output_cross_type_first
All source PNGs are read via git show main:path with Git blob SHA checks.
Writes ONLY to a new chatgpt_map_assets/output_* directory; never overwrites.
"""
import argparse
import json
import pathlib
import re
from PIL import Image
from issue232_cross_type_seam_recheck_2026_11_12 import MANIFEST, CONTROLS, read_main

# (name, {(x,y): asset_id}, [(x,y,edge,x2,y2), ...]); neighbor topology
# is a review hypothesis, not an original-PS1 or in-game behavior claim.
CASES = [
 ("road_bridge_ew",{(0,1):"map_road_ew",(1,1):"map_road_bridge_ew",(2,1):"map_road_ew",(1,0):"map_water_calm",(1,2):"map_water_calm"},[(0,1,"E",1,1),(1,1,"E",2,1)]),
 ("road_bridge_ns",{(1,0):"map_road_ns",(1,1):"map_road_bridge_ns",(1,2):"map_road_ns",(0,1):"map_water_calm",(2,1):"map_water_calm"},[(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("rail_bridge_ew",{(0,1):"map_rail_ew",(1,1):"map_rail_bridge_ew",(2,1):"map_rail_ew",(1,0):"map_water_calm",(1,2):"map_water_calm"},[(0,1,"E",1,1),(1,1,"E",2,1)]),
 ("rail_bridge_ns",{(1,0):"map_rail_ns",(1,1):"map_rail_bridge_ns",(1,2):"map_rail_ns",(0,1):"map_water_calm",(2,1):"map_water_calm"},[(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("crossing_basic",{(0,1):"map_road_ew",(1,1):"map_crossing_basic",(2,1):"map_road_ew",(1,0):"map_rail_ns",(1,2):"map_rail_ns"},[(0,1,"E",1,1),(1,1,"E",2,1),(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("crossing_closed",{(0,1):"map_road_ew",(1,1):"map_crossing_closed",(2,1):"map_road_ew",(1,0):"map_rail_ns",(1,2):"map_rail_ns"},[(0,1,"E",1,1),(1,1,"E",2,1),(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("grade_separation",{(0,1):"map_road_ew",(1,1):"map_grade_separation_cross",(2,1):"map_road_ew",(1,0):"map_rail_ns",(1,2):"map_rail_ns"},[(0,1,"E",1,1),(1,1,"E",2,1),(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("river_mouth_s",{(1,0):"map_river_ns",(1,1):"map_river_mouth_s",(1,2):"map_water_calm"},[(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("river_mouth_square",{(1,0):"map_river_ns",(1,1):"map_river_mouth_s_square",(1,2):"map_water_calm"},[(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("pond_channel_s",{(1,0):"map_river_ns",(1,1):"map_pond_channel_s",(1,2):"map_pond_small"},[(1,0,"S",1,1),(1,1,"S",1,2)]),
 ("inlet_w",{(0,1):"map_water_calm",(1,1):"map_inlet_w"},[(0,1,"E",1,1)]),
 ("concrete_access",{(0,1):"map_road_ew",(1,1):"map_concrete"},[(0,1,"E",1,1)])
]

def edge_mae(a, direction, b):
    if direction == "E":
        pixels = ((a.getpixel((23,y)),b.getpixel((0,y))) for y in range(24))
    elif direction == "S":
        pixels = ((a.getpixel((x,23)),b.getpixel((x,0))) for x in range(24))
    else:
        raise ValueError("Only E/S adjacency supported")
    pairs = list(pixels)
    return {"rgb_mae":round(sum(abs(p[i]-q[i]) for p,q in pairs for i in range(3))/72,3),
            "alpha_mismatches":sum(p[3]!=q[3] for p,q in pairs)}

def run(root, output_name):
    root = root.resolve()
    if not re.fullmatch(r"output_[A-Za-z0-9_]+",output_name):
        raise ValueError("Unsafe output name")
    isolated = root / "chatgpt_map_assets"
    if not isolated.is_dir() or isolated.is_symlink():
        raise ValueError("Isolated directory missing or symlinked")
    output = isolated / output_name
    if output.exists() or output.is_symlink():
        raise FileExistsError("Refusing overwrite: " + str(output))
    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    expected = {a["asset_id"]:a["source_git_blob_sha"] for a in manifest["assets"]}
    if len(expected)!=12 or set(expected).intersection(CONTROLS):
        raise ValueError("Expected 12 distinct cross-type assets")
    expected.update(CONTROLS)
    # All 19 images verified before creating any files.
    images = {key:read_main(root,key,sha)[0].resize((24,24),Image.Resampling.NEAREST)
              for key,sha in expected.items()}
    prepared = []
    for name, positions, edges in CASES:
        canvas = Image.new("RGBA",(72,72),(0,0,0,0))
        for (x,y), key in positions.items():
            canvas.paste(images[key],(x*24,y*24))
        seams=[]
        for x,y,d,nx,ny in edges:
            if d not in ("E","S") or (nx,ny)!=(x+(d=="E"),y+(d=="S")):
                raise ValueError("Invalid fixture seam")
            seams.append({"from":positions[(x,y)],"to":positions[(nx,ny)],"edge":d,
                          **edge_mae(images[positions[(x,y)]],d,images[positions[(nx,ny)]])})
        prepared.append((name,canvas,{"fixture":name,"tiles":len(positions),"seams":seams,
                                      "status":"NOT_VISUALLY_APPROVED"}))
    output.mkdir(exist_ok=False)
    for name, canvas, _ in prepared:
        canvas.save(output / (name+".png"))
    report = {"issue":232,"status":"FIXTURES_RENDERED_NOT_ACCEPTED",
              "source_ref":"main","verified_source_pngs":len(images),"fixture_pngs":len(prepared),
              "tile_display_px":24,"fixtures":[entry for _,_,entry in prepared],
              "limitations":["Pillow render, not Godot runtime",
                "Candidate adjacency from filenames, not confirmed PS1 topology",
                "Edge MAE is not visual or original-fidelity approval",
                "No existing source, main or Claude branch was modified"]}
    (output / "report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--repo-root",type=pathlib.Path,required=True)
    p.add_argument("--output-name",required=True)
    a=p.parse_args()
    print(json.dumps(run(a.repo_root,a.output_name),ensure_ascii=False,indent=2))
