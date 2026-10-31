#!/usr/bin/env python3
"""Read-only audit of the 45 road/rail/river candidate PNGs for issue #232.

Usage: python verify_45_edge_geometry_2026_10_31.py REPO_ROOT
       python verify_45_edge_geometry_2026_10_31.py REPO_ROOT --manifest PATH --report NEW.json

Only --report writes, using exclusive creation (never overwrites). Requires Pillow.
No numeric seam score is treated as original-game acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
from PIL import Image

MANIFEST = 'chatgpt_map_assets/manifests/connection_45_candidate_registry_2026-10-30.json'
BITS = {'N': 1, 'E': 2, 'S': 4, 'W': 8}
OPPOSITE = {'N': 'S', 'E': 'W', 'S': 'N', 'W': 'E'}
KINDS = ('road', 'rail', 'river')


def safe_file(root, path):
    base = root.resolve()
    file = (base / path).resolve()
    if not file.is_relative_to(base) or not file.is_file():
        raise ValueError(f'missing/unsafe path: {path}')
    return file


def git_blob_sha(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def edge(pixels, side):
    w, h = pixels.size
    if side == 'N':
        return [pixels.getpixel((x, 0)) for x in range(w)]
    if side == 'S':
        return [pixels.getpixel((x, h - 1)) for x in range(w)]
    if side == 'W':
        return [pixels.getpixel((0, y)) for y in range(h)]
    return [pixels.getpixel((w - 1, y)) for y in range(h)]


def mae(a, b, start=0, end=64):
    return round(sum(abs(a[i][c] - b[i][c]) for i in range(start, end)
                     for c in range(3)) / ((end - start) * 3), 3)


def water_profile(samples):
    positions = [i for i, (r, g, b, _) in enumerate(samples)
                 if b >= 180 and b > r + 25 and b > g + 8]
    return {'count': len(positions),
            'min': min(positions) if positions else None,
            'max': max(positions) if positions else None,
            'center': round(sum(positions) / len(positions), 2) if positions else None}


def audit(root, manifest_path):
    manifest = json.loads(safe_file(root, manifest_path).read_text(encoding='utf-8'))
    assets = manifest['assets']
    assert len(assets) == 45, f'expected 45 entries, got {len(assets)}'
    images = {}
    source_checks = []
    for a in assets:
        asset_id, kind, mask = a['asset_id'], a['kind'], a['direction_bits_nesw']
        assert kind in KINDS and asset_id.startswith(kind + '_')
        assert 1 <= mask <= 15 and asset_id == kind + '_' + ''.join(
            d.lower() for d in BITS if mask & BITS[d])
        assert asset_id not in images, f'duplicate {asset_id}'
        data = safe_file(root, a['candidate_path']).read_bytes()
        sha = git_blob_sha(data)
        assert sha == a['git_blob_sha'], f'blob mismatch: {asset_id}'
        with Image.open(safe_file(root, a['candidate_path'])) as im:
            im.verify()
        with Image.open(safe_file(root, a['candidate_path'])) as im:
            assert im.size == (64, 64) and im.mode == 'RGBA', f'bad PNG mode: {asset_id}'
            images[asset_id] = im.copy()
        source_checks.append({'id': asset_id, 'sha': sha, 'png_crc_rgba': 'PASS'})
    for kind in KINDS:
        assert {a['direction_bits_nesw'] for a in assets if a['kind'] == kind} == set(range(1, 16))

    comparisons = []
    channel_offsets = []
    for a in assets:
        kind, asset_id, mask = a['kind'], a['asset_id'], a['direction_bits_nesw']
        for side, bit in BITS.items():
            if not mask & bit:
                continue
            ref = kind + ('_ns' if side in ('N', 'S') else '_ew')
            x, y = edge(images[asset_id], side), edge(images[ref], OPPOSITE[side])
            row = {'id': asset_id, 'side': side, 'reference': ref,
                   'full_rgb_mae': mae(x, y), 'center20_rgb_mae': mae(x, y, 22, 42)}
            comparisons.append(row)
            if kind == 'river':
                px, py = water_profile(x), water_profile(y)
                offset = round(px['center'] - py['center'], 2) if (
                    px['center'] is not None and py['center'] is not None) else None
                channel_offsets.append({'id': asset_id, 'side': side, 'water_pixels': px['count'],
                                        'center': px['center'], 'reference_center': py['center'],
                                        'offset_px': offset})
    assert len(comparisons) == 96, f'expected 96 connected edges, got {len(comparisons)}'
    return {'status': 'DIAGNOSTIC_ONLY_NOT_ACCEPTED', 'pngs_verified': len(images),
            'connected_edges_compared': len(comparisons), 'source_checks': source_checks,
            'edge_comparisons': comparisons, 'river_channel_offsets': channel_offsets,
            'river_offsets_at_least_8px': [x for x in channel_offsets if x['offset_px'] is not None
                                          and abs(x['offset_px']) >= 8],
            'original_game_comparison': 'NOT_RUN', 'godot_render': 'NOT_RUN',
            'note': 'RGB MAE includes scenery; water segmentation is heuristic. Neither establishes acceptance.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo_root', type=Path)
    parser.add_argument('--manifest', default=MANIFEST)
    parser.add_argument('--report', type=Path, help='new report path (exclusive create, no overwrite)')
    args = parser.parse_args()
    result = audit(args.repo_root, args.manifest)
    content = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        with args.report.open('x', encoding='utf-8') as f:
            f.write(content)
        print(f'created {args.report}')
    else:
        print(content)


if __name__ == '__main__':
    main()
