#!/usr/bin/env python3
"""Stage the committed main-16 parent after restore-latest.py restores main-17."""
import hashlib
import json
import shutil
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
name = 'TOWN0001-ci-main-16-single'
source = ROOT.parent/'20261105-view-controls/evidence/source/opened-snapshots-20261028'
metadata = json.loads((source/(name+'.json')).read_text())
ram = zlib.decompress((source/(name+'.ram.zlib')).read_bytes())
assert len(ram) == 2097152
assert hashlib.sha256(ram).hexdigest() == metadata['ram_sha256'] == 'd5edcf5c0adf1e3f53c66e71be32a56af16dcb6be301482e29988f8244dd8cfb'
assert hashlib.sha256((algo/'source/SLPS_007.82').read_bytes()).hexdigest() == metadata['source_executable_sha256']
destination = algo/'source/opened-snapshots-20261028'
destination.mkdir(parents=True, exist_ok=True)
for suffix in ('.json', '.ram.zlib'):
    old, new = source/(name+suffix), destination/(name+suffix)
    if new.exists():
        assert new.read_bytes() == old.read_bytes()
    else:
        shutil.copy2(old, new)
print('main-16 input verified and staged')
