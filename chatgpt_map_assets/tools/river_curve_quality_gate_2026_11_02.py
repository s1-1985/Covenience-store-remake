#!/usr/bin/env python3
"""Issue #232: read-only PNG quality triage for four 2026-11-01 river curves.
Usage: python river_curve_quality_gate_2026_11_02.py REPO_ROOT [--report NEW.json]
       python river_curve_quality_gate_2026_11_02.py --self-test
Never approves art; never overwrites files. Requires Pillow.
"""
import argparse
import hashlib
import json
from collections import deque
from pathlib import Path
from PIL import Image

BASE = 'chatgpt_map_assets/'
MANIFEST = BASE + 'candidates/river_seam_warp_2026-11-01/candidate_manifest.json'
REF = {s: BASE + 'generated/native_copies_2026-10-15/river/map_river_' + ('ns' if s in 'NS' else 'ew') + '.png' for s in 'NESW'}
BITS = {'N': 1, 'E': 2, 'S': 4, 'W': 8}
OPP = {'N': 'S', 'S': 'N', 'E': 'W', 'W': 'E'}

def file_at(root, rel):
    if not isinstance(rel, str) or not rel.startswith(BASE):
        raise ValueError('not isolated: ' + str(rel))
    p = (root / rel).resolve()
    if not p.is_relative_to((root / 'chatgpt_map_assets').resolve()) or not p.is_file():
        raise ValueError('missing/unsafe: ' + rel)
    return p

def png(path):
    with Image.open(path) as im:
        if im.format != 'PNG':
            raise ValueError('not PNG: ' + str(path))
        im.verify()
    with Image.open(path) as im:
        if im.size != (64, 64) or im.mode != 'RGBA':
            raise ValueError('expected 64x64 RGBA: ' + str(path))
        im.load()
        return im.copy(), bool(im.info.get('icc_profile'))

def water(p):
    r, g, b, a = p
    return a > 0 and b >= 180 and b > r + 25 and b > g + 8

def edge(im, side):
    coords = []
    for k in range(64):
        xy = (k, 0) if side == 'N' else (k, 63) if side == 'S' else (0, k) if side == 'W' else (63, k)
        if water(im.getpixel(xy)):
            coords.append(k)
    return {'count': len(coords), 'center': (min(coords) + max(coords)) / 2 if coords else None}

def water_components(im):
    remaining = {(x, y) for y in range(64) for x in range(64) if water(im.getpixel((x, y)))}
    total = len(remaining)
    sizes = []
    while remaining:
        queue = deque([remaining.pop()]); n = 1
        while queue:
            x, y = queue.popleft()
            for q in ((x-1, y), (x+1, y), (x, y-1), (x, y+1)):
                if q in remaining:
                    remaining.remove(q); queue.append(q); n += 1
        sizes.append(n)
    return total, sorted(sizes, reverse=True)

def check(src, dst, refs, mask):
    sb, db = src.tobytes(), dst.tobytes()
    changed = sum(sb[i:i+4] != db[i:i+4] for i in range(0, len(sb), 4))
    sw = {i for i in range(4096) if water(tuple(sb[i*4:i*4+4]))}
    dw = {i for i in range(4096) if water(tuple(db[i*4:i*4+4]))}
    total, parts = water_components(dst)
    sides, flags = {}, []
    for side, bit in BITS.items():
        a = edge(dst, side); active = bool(mask & bit)
        b = edge(refs[side], OPP[side]) if active else None
        delta = a['center'] - b['center'] if b and a['center'] is not None and b['center'] is not None else None
        sides[side] = {'active': active, 'water_count': a['count'], 'center_offset_px': delta,
                       'width_delta_px': a['count'] - b['count'] if b else None}
        if active and (delta is None or abs(delta) > 1.5):
            flags.append('ACTIVE_EDGE_MISALIGNED_' + side)
        if not active and a['count']:
            flags.append('INACTIVE_EDGE_WET_' + side)
    if changed > 1024:
        flags.append('OVER_25_PERCENT_TRUE_PIXEL_CHANGE_REVIEW')
    if total == 0 or parts[0] < total * .95:
        flags.append('FRAGMENTED_WATER_MASK_REVIEW')
    return {'changed_pixels': changed, 'changed_fraction': round(changed / 4096, 5),
            'water_mask_iou': round(len(sw & dw) / len(sw | dw), 5) if sw | dw else 1.0,
            'water_pixels': total, 'water_components': len(parts), 'largest_component': parts[0] if parts else 0,
            'edges': sides, 'review_flags': flags, 'accepted': False}

def audit(root):
    root = root.resolve()
    assets = json.loads(file_at(root, MANIFEST).read_text(encoding='utf-8'))['assets']
    if len(assets) != 4 or {a['asset_id'] for a in assets} != {'river_ne', 'river_es', 'river_sw', 'river_nw'}:
        raise ValueError('unexpected candidate manifest')
    refs = {s: png(file_at(root, rel))[0] for s, rel in REF.items()}
    records = []
    for a in assets:
        srcfile, dstfile = file_at(root, a['source_path']), file_at(root, a['candidate_path'])
        src, srcicc = png(srcfile); dst, dsticc = png(dstfile)
        if srcicc and not dsticc:
            raise ValueError('ICC lost: ' + a['asset_id'])
        if a['direction_bits_nesw'] not in (3, 6, 9, 12):
            raise ValueError('invalid curve mask: ' + a['asset_id'])
        row = check(src, dst, refs, a['direction_bits_nesw'])
        row.update({'asset_id': a['asset_id'], 'source_sha256': hashlib.sha256(srcfile.read_bytes()).hexdigest(),
                    'candidate_sha256': hashlib.sha256(dstfile.read_bytes()).hexdigest(),
                    'source_icc': srcicc, 'candidate_icc': dsticc})
        records.append(row)
    return {'issue': 232, 'status': 'NOT_ACCEPTED', 'records': records,
            'review_required': ['human art review', 'original-game comparison', 'Godot 24px', 'game regression'],
            'caveat': 'Water segmentation and 25% pixel-change threshold are triage heuristics, not proof of visual correctness.'}

def self_test():
    bg, blue = (70, 130, 50, 255), (30, 90, 225, 255)
    src = Image.new('RGBA', (64, 64), bg)
    refs = {s: Image.new('RGBA', (64, 64), bg) for s in BITS}
    for y in range(64):
        for x in range(64):
            if (23 <= x <= 40 and y <= 41) or (24 <= y <= 41 and x >= 23):
                src.putpixel((x, y), blue)
            if 23 <= x <= 40:
                refs['N'].putpixel((x, y), blue); refs['S'].putpixel((x, y), blue)
            if 24 <= y <= 41:
                refs['E'].putpixel((x, y), blue); refs['W'].putpixel((x, y), blue)
    good = check(src, src.copy(), refs, 3)
    assert good['changed_pixels'] == 0 and not good['review_flags'], good
    bad = src.copy()
    for y in range(64):
        for x in range(64):
            if (x + y) % 2 == 0:
                bad.putpixel((x, y), (80, 140, 60, 255))
    flagged = check(src, bad, refs, 3)
    assert flagged['changed_pixels'] >= 2048 and 'OVER_25_PERCENT_TRUE_PIXEL_CHANGE_REVIEW' in flagged['review_flags']
    print('SELF_TEST_PASS: unchanged curve and >25% true-pixel-change case')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('repo_root', nargs='?', type=Path)
    ap.add_argument('--report', type=Path)
    ap.add_argument('--self-test', action='store_true')
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if args.repo_root is None:
        ap.error('repo_root required')
    out = json.dumps(audit(args.repo_root), ensure_ascii=False, indent=2) + '\n'
    if args.report:
        with args.report.open('x', encoding='utf-8') as f:
            f.write(out)
        print('created ' + str(args.report))
    else:
        print(out)

if __name__ == '__main__':
    main()
