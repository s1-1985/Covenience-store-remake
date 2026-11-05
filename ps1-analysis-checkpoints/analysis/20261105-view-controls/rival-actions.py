#!/usr/bin/env python3
"""Actual rival investigation/reinspection/founding-store guard through raw UI input."""
import hashlib
import json
import shutil
import struct
import sys
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve()
mode=sys.argv[2]
assert mode in ('investigate','reinspect','guard','info-only-confirm')
folder=ROOT/mode
folder.mkdir(exist_ok=True)
sys.path.insert(0,str(algo))
from verify_schedule_selector_frames import seq
import verify_opened_snapshot_play_20261028 as play

source='TOWN0001-view-rival-map-20261105-single' if mode in ('investigate','guard') else 'TOWN0001-rival-investigate-20261105-single'
snapshots=algo/'source/opened-snapshots-20261028'
before=zlib.decompress((snapshots/(source+'.ram.zlib')).read_bytes())
assert struct.unpack_from('<2h',before,0xcda42)==(43,12)
assert struct.unpack_from('<I',before,0xcd97c)[0]==0
assert struct.unpack_from('<H',before,0x12b2f8+5080+4)[0]==0x8001
assert before[0x12b2f8+5080+2]==(0 if mode in ('investigate','guard') else 1)
plans=([seq([0x4000,32])+[0]*150] if mode in ('guard','info-only-confirm') else
       [seq([32])+[0]*150,seq([64])+[0]*150])
name='TOWN0001-rival-'+mode+'-20261105-single'
row=play.compare(source,6,actions={0:32},native_music=True,
                 input_plans={0x8004d6ec:plans},finance_monitor=True,event_monitor=True,
                 refill_monitor=True,customer_monitor=True,whole_town_monitor=True,
                 staff_loop_monitor=True,acquisition_monitor=True,
                 progress_snapshot=name,progress_file=str(folder/'progress.json'))
(folder/'comparison.json').write_text(json.dumps(row,separators=(',',':'))+'\n')
assert len(row['acquisition_checks'])==1
check=row['acquisition_checks'][0]
assert check['slot']==1 and check['fee']==(500000 if mode in ('investigate','guard') else 0)
assert check['result']==('first_store_guard' if mode=='guard' else 'lease' if mode=='investigate' else 'cancel')
charges=[c for c in check['calls'] if c[0]=='0x8001cbc4']
assert [c[1][1] for c in charges]==([500000] if mode=='investigate' else [])
assert struct.unpack_from('<i',before,0xcd9f8)[0]>check['price']
after=zlib.decompress((snapshots/(name+'.ram.zlib')).read_bytes())
assert after[0x12b2f8+5080+2]==(0 if mode=='guard' else 1)
assert [struct.unpack_from('<H',after,0x12b2f8+s*5080+4)[0] for s in range(3)]==[1,0x8001,2]
out=dict(all_passed=True,mode=mode,source_snapshot=source,
         input_ram_sha256=hashlib.sha256(before).hexdigest(),
         output_ram_sha256=hashlib.sha256(after).hexdigest(),
         original_investigation_flag_before=before[0x12b2f8+5080+2],
         original_investigation_flag_after=after[0x12b2f8+5080+2],acquisition=check,play=row,
         new_natural_updates_counted=0,
         limits=['Original town-cursor state was reached by raw navigation; no coordinate, owner, cash, clock, RNG or menu-return injection.',
                 'Logical debit/capital and parent policy are checked by existing reached acquisition monitor.',
                 'Existing model result identifier lease means the investigation-display branch here, not a claim of rental or ownership transfer.',
                 'One actual founding rival store and current affordable price; no generalization to all rivals or scenarios.',
                 'Original child routines/Unicorn are shared by paired parent comparison; SDK/GPU/SPU/IRQ boundaries remain modeled.'])
(folder/'result.json').write_text(json.dumps(out,separators=(',',':'))+'\n')
for ext in ('.json','.ram.zlib'):
    p=snapshots/(name+ext)
    dst=folder/'evidence'/p.relative_to(algo)
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(p,dst)
print(json.dumps(dict(all_passed=True,mode=mode,fee=check['fee'],result=check['result'],price=check['price'])),flush=True)
