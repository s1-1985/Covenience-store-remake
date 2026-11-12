#!/usr/bin/env python3
import hashlib,json,zlib
from pathlib import Path
root=Path(__file__).resolve().parent;rows=[]
for name in ('second-store-results.json','second-store-play-proof.json'):
 p=root/name;raw=p.read_bytes();data=zlib.compress(raw,9);assert zlib.decompress(data)==raw
 target=Path(str(p)+'.zlib');target.write_bytes(data)
 rows.append(dict(path=name,stored_path=target.name,bytes=len(raw),stored_bytes=len(data),sha256=hashlib.sha256(raw).hexdigest(),stored_sha256=hashlib.sha256(data).hexdigest()))
 p.unlink()
(root/'evidence-manifest.json').write_text(json.dumps(dict(all_passed=True,files=rows),indent=2)+'\n')
print(json.dumps(rows))
