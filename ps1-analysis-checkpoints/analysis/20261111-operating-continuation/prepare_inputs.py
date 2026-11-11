#!/usr/bin/env python3
"""Stage unchanged committed main-17 to reproduce this 600-update segment."""
import hashlib,json,shutil,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve()
source=ROOT.parent/'20261105-card-image/evidence/source/opened-snapshots-20261028'
name='TOWN0001-ci-main-17-single'
meta=json.loads((source/(name+'.json')).read_text())
ram=zlib.decompress((source/(name+'.ram.zlib')).read_bytes())
assert len(ram)==2097152 and hashlib.sha256(ram).hexdigest()==meta['ram_sha256']=='8ba3ea71a158260e5015cc6fe70011d14a5169d16e53020874908041f2ef2fa2'
assert hashlib.sha256((algo/'source/SLPS_007.82').read_bytes()).hexdigest()==meta['source_executable_sha256']
for suffix in ('.json','.ram.zlib'):
    dest=algo/'source/opened-snapshots-20261028'/(name+suffix)
    if dest.exists(): assert dest.read_bytes()==(source/(name+suffix)).read_bytes()
    else: shutil.copy2(source/(name+suffix),dest)
print('original main-17 verified and staged')
