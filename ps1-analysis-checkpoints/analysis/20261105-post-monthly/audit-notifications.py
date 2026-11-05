#!/usr/bin/env python3
"""Reconcile reached monthly screen values and notice/menu gating with raw history."""
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
algo = Path(sys.argv[1]).resolve()
initial = ROOT.parent / '20261105-resumed-daily-close/evidence/source/opened-snapshots-20261028/TOWN0001-ci-main-13-single.ram.zlib'
ram = zlib.decompress(initial.read_bytes())
proof = json.loads((ROOT / 'evidence/opened-snapshot-TOWN0001-ci-main-14-single-verification-20261103.json').read_text())
assert proof['all_passed']
row = proof['cases'][0]
dequeues = [c for c in row['event_consumer_checks'] if c['slot'] is not None]
assert [(c['clock'],c['slot'],c['kind'],c['mode']) for c in dequeues] == [(17282,1,3,1),(17318,2,0,2)]
initial_requests = []
for slot in (1,2):
    p = 0x137970 + slot * 160
    assert ram[p] == 1
    kind,param,sound = struct.unpack_from('<3i',ram,p+132)
    initial_requests.append(dict(slot=slot,kind=kind,parameter=param,sound=sound,mode=ram[p+2]))
assert initial_requests == [dict(slot=1,kind=3,parameter=6,sound=28,mode=1),dict(slot=2,kind=0,parameter=0,sound=100,mode=2)]
word = lambda a:struct.unpack_from('<I',ram,a)[0]
signed = lambda x:(x+0x80000000)%0x100000000-0x80000000
expected = [word(0xe3c28),signed(word(0xe3c28)-word(0xe3c2c)),
            word(0xda974),signed(word(0xda974)-word(0xda978)),
            word(0xe36a8),signed(word(0xe36a8)-word(0xe36ac))]
own_profit = 0
for slot in range(10):
    p=0x12b2f8+slot*5080
    if ram[p] and not struct.unpack_from('<H',ram,p+4)[0]&0x8000:
        ledger=struct.unpack_from('<5i',ram,p+0xd4c)
        own_profit=signed(own_profit+signed(ledger[4]-sum(ledger[:4])))
assert expected[0] == own_profit == 325976
screens=row['monthly_screen_checks']
assert len(screens)==17 and [s['clock'] for s in screens]==list(range(17318,17352,2))
assert all(s['values']==expected for s in screens)
for screen in screens:
    numbers=[q for q in screen['requests'] if q['address']==0x8004e494]
    assert [q['value'] for q in numbers]==expected
    assert [q['slot'] for q in numbers]==[0x800e4000]*4+[0x800cd938]*2
notice=json.loads((ROOT/'notice-menu.json').read_text())
assert notice['all_passed'] and notice['initial_notice_active']==1 and notice['initial_notice_kind']==3
assert notice['supplied_raw_action']==128 and not notice['menu_reached'] and not notice['native_calls']
assert all(s['processed_input']==0 for s in notice['request_play']['steps'])
exe=(algo/'source/SLPS_007.82').read_bytes()
mask_sites=[]
for offset in range(2048,len(exe)-3,4):
    instruction=struct.unpack_from('<I',exe,offset)[0]
    if instruction>>26==12 and instruction&65535==0xf00c:
        mask_sites.append(dict(pc=hex(0x80010000+offset-2048),instruction=hex(instruction)))
assert mask_sites and (128&0xf00c)==0
out=dict(all_passed=True,source_ram_sha256=hashlib.sha256(ram).hexdigest(),
         initial_queued_requests=initial_requests,dequeues=dequeues,
         monthly_screen_values=expected,own_profit_from_previous_month_ledgers=own_profit,
         monthly_screen_calls=17,monthly_screen_clock_first=17318,monthly_screen_clock_last=17350,
         final_notice_active=row['event_consumer_checks'][-1]['active'],
         active_notice_menu_request=dict(raw=128,processed=0,menu_reached=False,source_andi_f00c_sites=mask_sites),
         source_executable_sha256=hashlib.sha256(exe).hexdigest(),new_natural_updates_counted=0,
         limits=['Logical original draw/number/sound requests and data, not GPU pixels or physical audio.',
                 'Original SDK confirmation input plans remain those of the archived runner; 17 calls is not a real-time duration.',
                 'One notice kind in town view tested; other notice types, views and frame timings are not generalized.'])
(ROOT/'notification-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(all_passed=True,monthly_values=expected,monthly_calls=17,active_notice_menu_blocked=True)))
