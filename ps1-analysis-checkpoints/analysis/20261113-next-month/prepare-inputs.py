#!/usr/bin/env python3
"""Restore main-25 plus any complete segment evidence already published here."""
import hashlib,json,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve()
snap=algo/'source/opened-snapshots-20261028';snap.mkdir(parents=True,exist_ok=True)
model=ROOT.parent/'20261103-operating-continuation/source-reference/live_master_oracle_20261028.py'
target_model=algo/model.name
if target_model.read_bytes()!=model.read_bytes():
 assert hashlib.sha256(target_model.read_bytes()).hexdigest()=='24faa3f8bef409fc00bd2c42741cf2dc6d8d5238eea3455f0056ece73fa468d2','Unexpected customized parent oracle'
 target_model.write_bytes(model.read_bytes())

old=ROOT.parent/'20261113-operating-continuation/encoded/evidence/source/opened-snapshots-20261028'
name='TOWN0001-ci-main-25-single'
for suffix in ('.json','.ram.zlib'):
 source=old/(name+suffix+('.zlib' if suffix=='.json' else ''))
 raw=zlib.decompress(source.read_bytes()) if suffix=='.json' else source.read_bytes()
 target=snap/(name+suffix)
 if target.exists():assert target.read_bytes()==raw
 else:target.write_bytes(raw)
meta=json.loads((snap/(name+'.json')).read_text());ram=zlib.decompress((snap/(name+'.ram.zlib')).read_bytes())
assert hashlib.sha256(ram).hexdigest()==meta['ram_sha256']=='236b0a2fffe3a27c229c63565cda9b11228fbdebd3c063e2ec82bb6d011716fe'
manifest=ROOT/'evidence-encoding.json';restored=0
if manifest.exists():
 for e in json.loads(manifest.read_text())['files']:
  rel=Path(e['path']).relative_to('evidence');target=(algo/rel).resolve();assert target.is_relative_to(algo)
  data=(ROOT/e['stored_path']).read_bytes();assert hashlib.sha256(data).hexdigest()==e['stored_sha256']
  raw=zlib.decompress(data) if e['encoding']=='zlib' else data
  assert len(raw)==e['bytes'] and hashlib.sha256(raw).hexdigest()==e['sha256']
  if target.exists():assert target.read_bytes()==raw
  else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
  restored+=1
print(json.dumps(dict(start=name,verified_completed_evidence_files=restored)))
