#!/usr/bin/env python3
"""Render three 5x5 topology QA samples at the actual 24px guide-map scale.

Requires a local repository checkout and Pillow. Never writes to existing paths.
These are seam-inspection fixtures, not original-game screenshots or acceptance.
"""
import argparse
import json
from pathlib import Path
from PIL import Image

MANIFEST = 'chatgpt_map_assets/manifests/connection_45_candidate_registry_2026-10-30.json'
SAMPLES = 'chatgpt_map_assets/samples/connection_45_topology_5x5_2026-10-31.json'
DIRS = [(0, -1, 1, 4), (1, 0, 2, 8), (0, 1, 4, 1), (-1, 0, 8, 2)]


def inside(root, relative):
    base = root.resolve()
    p = (base / relative).resolve()
    if not p.is_relative_to(base) or not p.is_file():
        raise ValueError(f'unsafe or missing source: {relative}')
    return p


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('repo_root', type=Path)
    p.add_argument('--out-dir', type=Path, required=True, help='must not exist')
    p.add_argument('--tile-px', type=int, choices=(24, 64), default=24)
    args = p.parse_args()
    manifest = json.loads(inside(args.repo_root, MANIFEST).read_text(encoding='utf-8'))
    samples = json.loads(inside(args.repo_root, SAMPLES).read_text(encoding='utf-8'))
    paths = {a['asset_id']: a['candidate_path'] for a in manifest['assets']}
    images = {}
    for sample in samples['maps']:
        w, h = sample['width'], sample['height']
        positions = {(t['x'], t['y']): t for t in sample['tiles']}
        assert len(positions) == len(sample['tiles'])
        assert {t['direction_bits_nesw'] for t in sample['tiles']} == set(range(1, 16))
        for (x, y), t in positions.items():
            assert 0 <= x < w and 0 <= y < h
            assert t['asset_id'] in paths
            for dx, dy, bit, opposite in DIRS:
                if t['direction_bits_nesw'] & bit:
                    neighbor = positions.get((x + dx, y + dy))
                    assert neighbor and neighbor['direction_bits_nesw'] & opposite
        canvas = Image.new('RGBA', (w * args.tile_px, h * args.tile_px), (0, 0, 0, 0))
        for (x, y), t in positions.items():
            with Image.open(inside(args.repo_root, paths[t['asset_id']])) as im:
                assert im.size == (64, 64) and im.mode == 'RGBA'
                tile = im.resize((args.tile_px, args.tile_px), Image.Resampling.NEAREST)
            canvas.alpha_composite(tile, (x * args.tile_px, y * args.tile_px))
        images[sample['id'] + '.png'] = canvas
    args.out_dir.mkdir(parents=False, exist_ok=False)
    for name, im in images.items():
        with (args.out_dir / name).open('xb') as output:
            im.save(output, format='PNG')
    print(f'created {len(images)} seam-test maps in {args.out_dir}; NOT visually accepted')


if __name__ == '__main__':
    main()
