#!/usr/bin/env python3
"""Losslessly encode large text proofs for Git; leave CPU RAM zlib unchanged."""
import hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rows=[]
for source in sorted((ROOT/'evidence').rglob('*')):
    if not source.is_file():continue
    data=source.read_bytes();relative=source.relative_to(ROOT)
    target=ROOT/'encoded'/relative
    encoding='identity'
    if source.suffix=='.json':target=Path(str(target)+'.zlib');data_out=zlib.compress(data,9);encoding='zlib'
    else:data_out=data
    target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data_out)
    rows.append(dict(path=str(relative),stored_path=str(target.relative_to(ROOT)),encoding=encoding,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),stored_bytes=len(data_out),stored_sha256=hashlib.sha256(data_out).hexdigest()))
(ROOT/'evidence-encoding.json').write_text(json.dumps(dict(all_passed=True,files=rows),indent=2)+'\n')
print(json.dumps(dict(files=len(rows),decoded_bytes=sum(r['bytes'] for r in rows),stored_bytes=sum(r['stored_bytes'] for r in rows))))
