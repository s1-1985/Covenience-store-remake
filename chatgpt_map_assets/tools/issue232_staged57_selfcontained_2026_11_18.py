#!/usr/bin/env python3
"""Issue #232: decode 57 staged PNGs and make nine *diagnostic* 24px fixtures.

Inputs are read-only; outputs must be a NEW directory under chatgpt_map_assets/.
Does not claim original-PS1 fidelity, seam approval, Godot or game integration.
Run: python chatgpt_map_assets/tools/issue232_staged57_selfcontained_2026_11_18.py --repo-root . --output-name output_staged57_2026_11_18
Requires Pillow. No main-branch checkout or network required.
"""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import tempfile
from PIL import Image

BASE = Path('chatgpt_map_assets')
STAGE = BASE / 'staging_connection_57_2026-11-17'
BITS = {'n': 1, 'e': 2, 's': 4, 'w': 8}
OPPOSITE = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
DIRS = [(0, -1, 'N', 1), (1, 0, 'E', 2), (0, 1, 'S', 4), (-1, 0, 'W', 8)]
# All tiles here are from the staged 57; no silent dependency on main/raw.
FIXTURES = {
    'crossing_basic': {(1, 0): 'road_ns', (1, 1): 'map_crossing_basic', (1, 2): 'road_ns', (0, 1): 'rail_ew', (2, 1): 'rail_ew'},
    'crossing_closed': {(1, 0): 'road_ns', (1, 1): 'map_crossing_closed', (1, 2): 'road_ns', (0, 1): 'rail_ew', (2, 1): 'rail_ew'},
    'road_bridge_ew': {(0, 1): 'road_ew', (1, 1): 'map_road_bridge_ew', (2, 1): 'road_ew'},
    'road_bridge_ns': {(1, 0): 'road_ns', (1, 1): 'map_road_bridge_ns', (1, 2): 'road_ns'},
    'rail_bridge_ew': {(0, 1): 'rail_ew', (1, 1): 'map_rail_bridge_ew', (2, 1): 'rail_ew'},
    'rail_bridge_ns': {(1, 0): 'rail_ns', (1, 1): 'map_rail_bridge_ns', (1, 2): 'rail_ns'},
    'river_mouth_s': {(1, 0): 'river_ns', (1, 1): 'map_river_mouth_s'},
    'river_mouth_s_square': {(1, 0): 'river_ns', (1, 1): 'map_river_mouth_s_square'},
    'inlet_w': {(1, 1): 'map_inlet_w'},
}
UNTESTED = {
    'crossing_basic': [], 'crossing_closed': [],
    'road_bridge_ew': ['water N/S not tested: no water tile in 57'],
    'road_bridge_ns': ['water E/W not tested: no water tile in 57'],
    'rail_bridge_ew': ['water N/S not tested: no water tile in 57'],
    'rail_bridge_ns': ['water E/W not tested: no water tile in 57'],
    'river_mouth_s': ['sea S not tested: no sea tile in 57'],
    'river_mouth_s_square': ['sea S not tested: no sea tile in 57'],
    'inlet_w': ['sea W not tested: no sea tile in 57'],
}

def git_blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()

def load_png(data, sha, aid):
    if git_blob_sha(data) != sha:
        raise ValueError('blob SHA mismatch: ' + aid)
    with Image.open(io.BytesIO(data)) as im:
        im.load()  # full IDAT decompression and pixel decode
        if im.format != 'PNG' or im.mode != 'RGBA' or im.size != (64, 64):
            raise ValueError('not 64x64 RGBA PNG: ' + aid)
        return im.copy()

def check_registry(entries):
    if len(entries) != 57 or len({r['asset_id'] for r in entries}) != 57:
        raise ValueError('expected 57 unique staged assets')
    for role in ('road', 'rail', 'river'):
        found = [r for r in entries if r['kind'] == 'directional' and r['role'] == role]
        masks = []
        for r in found:
            suffix = r['asset_id'][len(role)+1:]
            expected = sum(BITS[c] for c in suffix)
            actual = r['ports'].get(role)
            if r['asset_id'] != role + '_' + suffix or expected != actual or len(set(suffix)) != len(suffix):
                raise ValueError('direction mask mismatch: ' + r['asset_id'])
            masks.append(actual)
        if sorted(masks) != list(range(1, 16)):
            raise ValueError('missing/duplicate directional masks: ' + role)
    if sum(r['kind'] == 'cross_type' for r in entries) != 12:
        raise ValueError('expected 12 cross-type assets')
    return True

def edge_stats(a, b, side):
    if side == 'E':
        px = [(a.getpixel((23, y)), b.getpixel((0, y))) for y in range(24)]
    elif side == 'S':
        px = [(a.getpixel((x, 23)), b.getpixel((x, 0))) for x in range(24)]
    else:
        raise ValueError('only E/S used for unique seams')
    return {'rgb_mae': round(sum(abs(x[i]-y[i]) for x,y in px for i in range(3))/72, 3),
            'alpha_mismatch_px': sum(x[3] != y[3] for x,y in px)}

def fixture_report(positions, entries, images):
    # Check *actual connected* same-type ports. Water/sea neighbors are deliberately absent.
    seams = []
    for (x, y), aid in positions.items():
        for dx, dy, side, bit in [(1, 0, 'E', 2), (0, 1, 'S', 4)]:
            other = positions.get((x+dx, y+dy))
            if other is None:
                continue
            opposite_bit = 8 if bit == 2 else 1
            ports_a, ports_b = entries[aid]['ports'], entries[other]['ports']
            shared = [kind for kind in ('road', 'rail', 'river')
                      if ports_a.get(kind, 0) & bit and ports_b.get(kind, 0) & opposite_bit]
            dangling = [kind for kind in ('road', 'rail', 'river')
                        if bool(ports_a.get(kind, 0) & bit) != bool(ports_b.get(kind, 0) & opposite_bit)]
            if dangling or not shared:
                raise ValueError(f'fixture port mismatch: {aid} {side} {other}; dangling={dangling}')
            seams.append({'from': aid, 'to': other, 'side': side, 'connected': shared,
                          **edge_stats(images[aid], images[other], side)})
    return seams

def run(root, output_name):
    root = root.resolve()
    if not re.fullmatch(r'output_[A-Za-z0-9_]+', output_name):
        raise ValueError('output directory must be a new output_* name')
    base = root / BASE
    stage = root / STAGE
    out = base / output_name
    if not base.is_dir() or base.is_symlink() or not stage.is_dir() or stage.is_symlink():
        raise ValueError('missing or symlinked isolated asset directory')
    if out.exists() or out.is_symlink():
        raise FileExistsError('refuse overwrite: ' + str(out))
    manifest = json.loads((stage/'manifest.json').read_text(encoding='utf-8'))
    records = manifest['records']
    check_registry(records)
    entries = {r['asset_id']: r for r in records}
    images = {}
    for aid, r in entries.items():
        expected = (STAGE / (aid + '.png')).as_posix()
        if r['staged_path'] != expected or r['footprint_xy'] != [1,1] or r['display_px'] != [24,24]:
            raise ValueError('invalid path/size metadata: ' + aid)
        images[aid] = load_png((root/expected).read_bytes(), r['staged_blob_sha'], aid).resize((24,24), Image.Resampling.NEAREST)
    prepared = []
    for name, positions in FIXTURES.items():
        if any(aid not in entries for aid in positions.values()):
            raise ValueError('unknown fixture asset: ' + name)
        seams = fixture_report(positions, entries, images)
        canvas = Image.new('RGBA', (72,72), (0,0,0,0))
        for (x,y), aid in positions.items():
            canvas.paste(images[aid], (x*24,y*24))
        prepared.append((name, canvas, {'name': name, 'tile_count': len(positions),
                                         'connected_seams': seams, 'not_tested': UNTESTED[name],
                                         'accepted': False}))
    # No output is created until all 57 files and all nine fixture definitions validate.
    out.mkdir(exist_ok=False)
    for name, canvas, _ in prepared:
        canvas.save(out/(name+'.png'))
    report = {'issue':232, 'run_date':'2026-11-18', 'status':'DIAGNOSTIC_NOT_APPROVED',
              'real_pngs_full_decoded':57, 'png_failures':0, 'fixture_pngs':9,
              'all_directional_masks_present':True,
              'source_branch':'chatgpt/map-assets-isolated-20260922',
              'fixtures':[v for _,_,v in prepared],
              'unresolved_topology':[r['asset_id'] for r in records if r.get('source_topology_unresolved')],
              'limitations':['No PS1 reference visual acceptance', 'No Godot or game regression run',
                             'Bridge water and river-mouth sea edges not tested',
                             'RGB edge MAE is diagnostic, not seam acceptance',
                             'All assets remain candidates; no game code or existing file modified']}
    (out/'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
    return report

def self_test():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d); stage = root/STAGE; stage.mkdir(parents=True)
        records = []
        for role in ('road','rail','river'):
            for mask in range(1,16):
                suffix = ''.join(c for c,v in BITS.items() if mask&v)
                records.append({'asset_id':role+'_'+suffix,'kind':'directional','role':role,
                                'ports':{role:mask}})
        cross_ports = {'map_crossing_basic':{'road':5,'rail':10},'map_crossing_closed':{'road':5,'rail':10},
                       'map_road_bridge_ew':{'road':10,'water':5},'map_road_bridge_ns':{'road':5,'water':10},
                       'map_rail_bridge_ew':{'rail':10,'water':5},'map_rail_bridge_ns':{'rail':5,'water':10},
                       'map_grade_separation_cross':{'road':5,'elevated_structure':10},
                       'map_river_mouth_s':{'river':1,'sea':4},'map_river_mouth_s_square':{'river':1,'sea':4},
                       'map_pond_channel_s':{},'map_inlet_w':{'sea':8},'map_concrete':{}}
        for aid, ports in cross_ports.items():
            records.append({'asset_id':aid,'kind':'cross_type','role':'cross_type','ports':ports})
        check_registry(records)
        im = Image.new('RGBA',(64,64),(50,100,150,255)); buf=io.BytesIO(); im.save(buf, format="PNG"); png=buf.getvalue()
        for r in records:
            aid=r['asset_id'];r.update(staged_path=(STAGE/(aid+'.png')).as_posix(),
                                      staged_blob_sha=git_blob_sha(png),footprint_xy=[1,1],display_px=[24,24])
            (stage/(aid+'.png')).write_bytes(png)
        (stage/'manifest.json').write_text(json.dumps({'records':records}))
        result=run(root,'output_synthetic_test')
        assert result['real_pngs_full_decoded']==57 and result['fixture_pngs']==9
        assert len(result['fixtures'][0]['connected_seams'])==4
        try:
            run(root,'output_synthetic_test')
        except FileExistsError: pass
        else: raise AssertionError('overwrite not blocked')
        (stage/'road_ns.png').write_bytes(b'broken')
        try:
            run(root,'output_corrupt_test')
        except ValueError: pass
        else: raise AssertionError('corrupt blob not blocked')
        assert not (root/BASE/'output_corrupt_test').exists()
    return 'PASS synthetic 57 PNG full decode, nine fixture renders, 4 crossing seams, overwrite and corruption rejection'

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repo-root',type=Path)
    p.add_argument('--output-name')
    p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.self_test: print(self_test())
    else:
        if a.repo_root is None or a.output_name is None:
            p.error('--repo-root and --output-name required unless --self-test')
        print(json.dumps(run(a.repo_root,a.output_name),ensure_ascii=False,indent=2))
