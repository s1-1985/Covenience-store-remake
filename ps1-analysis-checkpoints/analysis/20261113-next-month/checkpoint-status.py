#!/usr/bin/env python3
"""Report only completed/audited segments; do not count partial live snapshots."""
import json,struct,hashlib,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
rows=[]
for p in sorted(ROOT.glob('TOWN0001-ci-main-*-single.audit.json')):
 a=json.loads(p.read_text());assert a['passed'];rows.append(a)
print(json.dumps(dict(completed_segments=len(rows),verified_updates=sum(a['updates'] for a in rows),latest=(dict(snapshot=rows[-1]['output'],clock=rows[-1]['clock_after'],completed_iterations=rows[-1]['completed_iterations'],cash=rows[-1]['cash_after'],ram_sha256=rows[-1]['final_ram_sha256']) if rows else None)),indent=2))
