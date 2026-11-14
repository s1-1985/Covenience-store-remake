#!/usr/bin/env python3
"""Issue #232: focused 24px fixture PNGs, correcting reversed crossing axes.

Read-only inputs: isolated 12 PNGs + main branch's seven control tiles.
Writes ONLY to a new chatgpt_map_assets/output_* directory. Never edits game code.
Requires Pillow, git, and a checkout containing main and the isolated branch.
This is diagnostic, not PS1, Godot, or seam-quality acceptance.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
from PIL import Image

BASE = Path('chatgpt_map_assets')
INDIVIDUAL = BASE / 'individual_cross_type_2026-11-14'
OVERLAY = BASE / 'manifests/issue232_cross_type_topology_correction_2026-11-15.json'
RAW = 'assets/raw/conveni_map_assets_v2/terrain/tiles_64/'
CONTROLS = {
    'map_road_ew': '96dc9c5f90d134db6096295d649ee88d45b18f3a',
    'map_road_ns': '360c16bfe0c0a874af1ffac34e42eee51ce0e7c1',
    'map_rail_ew': '17ae09cf4b389d22832dc6289804971ff53fb2fa',
    'map_rail_ns': '3ecc57989beab8f74b97a5079d14fc557de15e5b',
    'map_river_ns': 'a5c0b606ce3f2653e3f0c3532eaa52211af59a53',
    'map_water_calm': '7f38c2b355344499172bd89def7b8addc48c34b5',
    'map_pond_small': '2719b0b51ece024a1b26453e73fc415e85c3147a',
}
# Coordinates are (x,y), north is -y. Crossing road is NS, rail EW.
FIXTURES = {
    'crossing_basic_NSroad_EWrail': {(1,0):'map_road_ns',(1,1):'map_crossing_basic',(1,2):'map_road_ns',(0,1):'map_rail_ew',(2,1):'map_rail_ew'},
    'crossing_closed_NSroad_EWrail': {(1,0):'map_road_ns',(1,1):'map_crossing_closed',(1,2):'map_road_ns',(0,1):'map_rail_ew',(2,1):'map_rail_ew'},
    'road_bridge_ew': {(0,1):'map_road_ew',(1,1):'map_road_bridge_ew',(2,1):'map_road_ew',(1,0):'map_water_calm',(1,2):'map_water_calm'},
    'road_bridge_ns': {(1,0):'map_road_ns',(1,1):'map_road_bridge_ns',(1,2):'map_road_ns',(0,1):'map_water_calm',(2,1):'map_water_calm'},
    'rail_bridge_ew': {(0,1):'map_rail_ew',(1,1):'map_rail_bridge_ew',(2,1):'map_rail_ew',(1,0):'map_water_calm',(1,2):'map_water_calm'},
    'rail_bridge_ns': {(1,0):'map_rail_ns',(1,1):'map_rail_bridge_ns',(1,2):'map_rail_ns',(0,1):'map_water_calm',(2,1):'map_water_calm'},
    'river_mouth_s': {(1,0):'map_river_ns',(1,1):'map_river_mouth_s',(1,2):'map_water_calm'},
    'river_mouth_s_square': {(1,0):'map_river_ns',(1,1):'map_river_mouth_s_square',(1,2):'map_water_calm'},
    'inlet_w': {(0,1):'map_water_calm',(1,1):'map_inlet_w'},
}
EXCLUDED = ['map_grade_separation_cross', 'map_pond_channel_s', 'map_concrete']

def git_blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()

def load_png(data, expected_sha, asset_id):
    if git_blob_sha(data) != expected_sha:
        raise ValueError('Git Blob SHA mismatch: ' + asset_id)
    with Image.open(io.BytesIO(data)) as im:
        im.load()  # Full pixel decode, not merely IHDR/CRC
        if im.format != 'PNG' or im.mode != 'RGBA' or im.size != (64,64):
            raise ValueError('Expected 64x64 RGBA PNG: ' + asset_id)
        return im.copy().resize((24,24), Image.Resampling.NEAREST)

def edge_mae(a, b, direction):
    if direction == 'E':
        pairs = [(a.getpixel((23,y)), b.getpixel((0,y))) for y in range(24)]
    elif direction == 'S':
        pairs = [(a.getpixel((x,23)), b.getpixel((x,0))) for x in range(24)]
    else:
        raise ValueError('Only E/S supported')
    return {'rgb_mae': round(sum(abs(p[i]-q[i]) for p,q in pairs for i in range(3))/72,3),
            'alpha_mismatch_px': sum(p[3]!=q[3] for p,q in pairs)}

def run(root, output_name):
    root = root.resolve()
    if not re.fullmatch(r'output_[A-Za-z0-9_]+', output_name):
        raise ValueError('Output name must start output_ and contain only letters/numbers/_')
    target = root / BASE / output_name
    if target.exists() or target.is_symlink():
        raise FileExistsError('No overwriting: ' + str(target))
    manifest = json.loads((root / INDIVIDUAL / 'manifest.json').read_text(encoding='utf-8'))
    overlay = json.loads((root / OVERLAY).read_text(encoding='utf-8'))
    entries = {a['asset_id']:a for a in manifest['assets']}
    topology = {a['asset_id']:a for a in overlay['assets']}
    if len(entries)!=12 or len(topology)!=12 or set(entries)!=set(topology) or set(entries)&set(CONTROLS):
        raise ValueError('Expected same 12 distinct isolated assets in both manifests')
    for aid, a in entries.items():
        if topology[aid]['source_git_blob_sha'] != a['source_git_blob_sha']:
            raise ValueError('Topology SHA mismatch: '+aid)
    for crossing in ('map_crossing_basic','map_crossing_closed'):
        t=topology[crossing]['visual_connectivity']
        if t.get('road') != ['N','S'] or t.get('rail') != ['E','W']:
            raise ValueError('Crossing axes not corrected: '+crossing)
    if sorted(EXCLUDED) != sorted(overlay['excluded_from_connection_fixtures']):
        raise ValueError('Excluded set changed unexpectedly')
    images = {}
    for aid, entry in entries.items():
        expected = (INDIVIDUAL / (aid+'.png')).as_posix()
        if entry['isolated_path'] != expected:
            raise ValueError('Unexpected isolated PNG path: '+aid)
        images[aid] = load_png((root / expected).read_bytes(),entry['source_git_blob_sha'],aid)
    for aid,sha in CONTROLS.items():
        result = subprocess.run(['git','-C',str(root),'show','main:'+RAW+aid+'.png'],
                                check=True,capture_output=True)
        images[aid] = load_png(result.stdout,sha,aid)
    # Validate all inputs BEFORE creating any output directory.
    prepared=[]
    for name,positions in FIXTURES.items():
        canvas=Image.new('RGBA',(72,72),(0,0,0,0))
        for (x,y),aid in positions.items():
            if aid not in images or x not in range(3) or y not in range(3):
                raise ValueError('Invalid fixture tile '+name)
            canvas.paste(images[aid],(24*x,24*y))
        seams=[]
        for (x,y),aid in positions.items():
            for dx,dy,side in [(1,0,'E'),(0,1,'S')]:
                neighbor=(x+dx,y+dy)
                if neighbor in positions:
                    other=positions[neighbor]
                    seams.append({'a':aid,'b':other,'edge':side,**edge_mae(images[aid],images[other],side)})
        prepared.append((name,canvas,{'name':name,'tiles':len(positions),'seams':seams,'accepted':False}))
    if not (root / BASE).is_dir() or (root / BASE).is_symlink():
        raise ValueError('Isolated directory missing or symlinked')
    target.mkdir(exist_ok=False)
    for name,canvas,_ in prepared:
        canvas.save(target/(name+'.png'))
    report={'issue':232,'status':'DIAGNOSTIC_NOT_APPROVED','run_date':'2026-11-15',
            'source_pngs_full_decoded':len(images),'source_png_failures':0,
            'corrected_crossing_axes':'road_NS rail_EW',
            'fixture_pngs':len(prepared),'tile_display_px':24,
            'excluded_pending_review':EXCLUDED,
            'fixtures':[entry for _,_,entry in prepared],
            'limitations':['No PS1 fidelity verification','No Godot viewport or game regression',
                           'RGB edge MAE is diagnostic; does not certify seams',
                           'No source images or existing game files modified']}
    (target/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

def self_test():
    # Synthetic checks only; does not imply the real images were processed.
    import tempfile
    im=Image.new('RGBA',(64,64),(12,20,100,255))
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/'test.png';im.save(p)
        data=p.read_bytes();sha=git_blob_sha(data)
        assert load_png(data,sha,'synthetic').size==(24,24)
        try:
            load_png(data,'0'*40,'synthetic')
        except ValueError:
            pass
        else:
            raise AssertionError('SHA corruption not detected')
    assert edge_mae(Image.new('RGBA',(24,24),(0,0,0,255)),Image.new('RGBA',(24,24),(0,0,0,255)),'E')['rgb_mae']==0
    assert len(FIXTURES)==9 and len(EXCLUDED)==3
    return 'synthetic PNG decode, SHA mismatch, edge and fixture counts PASS'

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo-root',type=Path)
    p.add_argument('--output-name')
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test:
        print(self_test())
    else:
        if not a.repo_root or not a.output_name:
            p.error('--repo-root and --output-name are required')
        print(json.dumps(run(a.repo_root,a.output_name),ensure_ascii=False,indent=2))
