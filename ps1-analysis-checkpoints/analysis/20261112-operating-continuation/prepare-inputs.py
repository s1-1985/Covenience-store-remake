#!/usr/bin/env python3
"""Stage committed main-20 to repeat the four natural continuation segments."""
import hashlib,json,shutil,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve()
source=ROOT.parent/'20261111-operating-continuation/evidence/source/opened-snapshots-20261028'
name='TOWN0001-ci-main-20-single'
meta=json.loads((source/(name+'.json')).read_text());ram=zlib.decompress((source/(name+'.ram.zlib')).read_bytes())
assert len(ram)==2097152 and hashlib.sha256(ram).hexdigest()==meta['ram_sha256']=='3c7127719ccd416adf702ba902ed67a094ca486805b5cb54489c193dbd927ac0'
assert hashlib.sha256((algo/'source/SLPS_007.82').read_bytes()).hexdigest()==meta['source_executable_sha256']
for suffix in ('.json','.ram.zlib'):
    target=algo/'source/opened-snapshots-20261028'/(name+suffix)
    if target.exists():assert target.read_bytes()==(source/(name+suffix)).read_bytes()
    else:shutil.copy2(source/(name+suffix),target)
print('original main-20 verified and staged')
