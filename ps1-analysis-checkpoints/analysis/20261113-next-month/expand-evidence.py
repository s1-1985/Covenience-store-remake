#!/usr/bin/env python3
"""Expand committed evidence without overwriting unrelated or changed files."""
import hashlib,json,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'evidence-encoding.json').read_text())
destination=Path(sys.argv[1]).resolve();destination.mkdir(parents=True,exist_ok=True)
for entry in manifest['files']:
    source=(ROOT/entry['stored_path']).resolve();target=(destination/entry['path']).resolve()
    assert source.is_relative_to(ROOT.resolve()) and target.is_relative_to(destination)
    encoded=source.read_bytes();assert hashlib.sha256(encoded).hexdigest()==entry['stored_sha256'] and len(encoded)==entry['stored_bytes']
    assert entry['encoding'] in ('identity','zlib')
    data=zlib.decompress(encoded) if entry['encoding']=='zlib' else encoded
    assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256']
    if target.exists():assert target.read_bytes()==data
    else:target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
print(json.dumps(dict(all_passed=True,files=len(manifest['files']))))
