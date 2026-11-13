#!/usr/bin/env python3
"""Two diagnostic updates from an independently restored complete checkpoint."""
import hashlib,json,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
from verify_opened_snapshot_play_20261028 import compare
latest=json.loads((ROOT.parent.parent/'LATEST-ANALYSIS.json').read_text());name=sys.argv[2] if len(sys.argv)>2 else latest['snapshot'];assert Path(name).name==name
meta=json.loads((algo/'source/opened-snapshots-20261028'/ (name+'.json')).read_text());ram=zlib.decompress((algo/'source/opened-snapshots-20261028'/(name+'.ram.zlib')).read_bytes())
assert hashlib.sha256(ram).hexdigest()==meta['ram_sha256']
row=compare(name,2,native_music=True,finance_monitor=True,event_monitor=True,refill_monitor=True,customer_monitor=True,whole_town_monitor=True,staff_loop_monitor=True)
assert row['completed_before']==meta['completed_iterations'] and row['runtime_table_provenance']=='single_conversion'
assert row['snapshot_sha256']==meta['ram_sha256'] and row['steps'][-1]['clock']==row['opening_clock']+4
raw=(json.dumps(row,separators=(',',':'))+'\n').encode();proof='restart-'+name+'-proof.json.zlib';(ROOT/proof).write_bytes(zlib.compress(raw,9))
out=dict(all_passed=True,snapshot=name,diagnostic_updates=2,completed_before=meta['completed_iterations'],ram_sha256=meta['ram_sha256'],clock_before=row['opening_clock'],clock_after=row['steps'][-1]['clock'],proof=proof,proof_sha256=hashlib.sha256(raw).hexdigest(),limits='Diagnostic only; excluded from all natural trajectory counts and latest CPU checkpoint.')
(ROOT/('restart-'+name+'-check.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
