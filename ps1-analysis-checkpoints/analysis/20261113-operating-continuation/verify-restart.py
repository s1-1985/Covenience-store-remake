#!/usr/bin/env python3
"""Two diagnostic updates from independently restored latest natural state."""
import hashlib,json,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
from verify_opened_snapshot_play_20261028 import compare
name='TOWN0001-ci-main-25-single'
row=compare(name,2,native_music=True,finance_monitor=True,event_monitor=True,refill_monitor=True,customer_monitor=True,whole_town_monitor=True,staff_loop_monitor=True)
assert row['opening_clock']==20960 and row['steps'][-1]['clock']==20964
assert row['completed_before']==10488 and row['runtime_table_provenance']=='single_conversion'
proof=(json.dumps(row,separators=(',',':'))+'\n').encode()
(ROOT/'restart-proof.json.zlib').write_bytes(zlib.compress(proof,9))
summary=dict(all_passed=True,snapshot=name,snapshot_sha256=row['snapshot_sha256'],diagnostic_updates=2,opening_clock=row['opening_clock'],final_clock=row['steps'][-1]['clock'],proof_sha256=hashlib.sha256(proof).hexdigest(),limits='Diagnostic only; the latest natural checkpoint remains main-25 at clock20960.')
(ROOT/'restart-check.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary))
