#!/usr/bin/env python3
"""Restore the fixed start plus any fully verified new-store segments."""
import hashlib,json,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve()
snap=algo/'source/opened-snapshots-20261028';snap.mkdir(parents=True,exist_ok=True)
old=ROOT.parent/'20261113-next-month/encoded/evidence/source/opened-snapshots-20261028'
name='TOWN0001-ci-main-31-single'
for suffix in ('.json','.ram.zlib'):
 source=old/(name+suffix+('.zlib' if suffix=='.json' else ''))
 data=zlib.decompress(source.read_bytes()) if suffix=='.json' else source.read_bytes()
 target=snap/(name+suffix)
 if target.exists():assert target.read_bytes()==data
 else:target.write_bytes(data)
meta=json.loads((snap/(name+'.json')).read_text());ram=zlib.decompress((snap/(name+'.ram.zlib')).read_bytes())
assert hashlib.sha256(ram).hexdigest()==meta['ram_sha256']=='f9bba3258b11c921869e0ddfe8a34291a58102ea4023e490ac48f912f96a1971'
count=0
manifest=ROOT/'evidence-encoding.json'
if manifest.exists():
 for row in json.loads(manifest.read_text())['files']:
  target=(algo/Path(row['path']).relative_to('evidence')).resolve();assert target.is_relative_to(algo)
  encoded=(ROOT/row['stored_path']).read_bytes();assert hashlib.sha256(encoded).hexdigest()==row['stored_sha256']
  data=zlib.decompress(encoded) if row['encoding']=='zlib' else encoded
  assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256']
  if target.exists():assert target.read_bytes()==data
  else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
  count+=1
print(json.dumps(dict(start=name,verified_completed_evidence_files=count)))
