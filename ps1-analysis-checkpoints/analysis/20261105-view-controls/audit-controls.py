#!/usr/bin/env python3
"""Join original UI navigation, independent list policy and card round-trip evidence."""
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parent
algo=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(algo))
from save_codec import SIZE,valid


def result(name):
    data=json.loads((ROOT/name).read_text())
    assert data['all_passed'],name
    return data


own=result('own/result.json')
wrap=result('list-wrap/result.json')
rival=result('rival/result.json')
branches={c['branch'] for d in (own,wrap) for c in d['list_parent_checks']}
assert branches=={'idle','up','down','confirm','cancel'}
assert all(c['order']==[0,2]+[-1]*8 and c['count']==2 for d in (own,wrap) for c in d['list_parent_checks'])
assert own['final_view']==2 and own['final_selected']==2 and own['final_store_flags']==2
assert wrap['final_view']==0 and wrap['final_selected']==0xffffffff
assert any(c['branch']=='up' and c['row_before']==0 and c['row_after']==1 for c in wrap['list_parent_checks'])
assert any(c['branch']=='down' and c['row_before']==1 and c['row_after']==0 for c in wrap['list_parent_checks'])
assert any(c['function']=='0x80060418' for c in own['calls'])
assert not any(c['function']=='0x8005fe54' for c in own['calls'])
old=json.loads((ROOT/'development-own-before-list-monitor.json').read_text())
assert old['play']['steps']==own['play']['steps']
mistarget=result('development-own-list-wrap/result.json')
assert mistarget['final_selected']==0 and mistarget['final_store_flags']==1
assert rival['final_view']==0 and rival['final_selected']==0xffffffff
assert rival['play']['steps'][-1]['town_cursor']==[43,12]
assert any(c['function']=='0x80060d6c' for c in rival['calls'])
assert not any(c['function']=='0x80060418' for c in rival['calls'])
checks=rival['play']['acquisition_checks']
assert len(checks)==1 and checks[0]['slot']==1 and checks[0]['result']=='cancel'
assert checks[0]['fee']==500000 and checks[0]['price']==52704360
assert not any(c[0]=='0x8001cbc4' for c in checks[0]['calls'])
modes={m:result(m+'/result.json') for m in ('investigate','reinspect','guard','info-only-confirm')}
assert modes['investigate']['acquisition']['fee']==500000
assert modes['reinspect']['acquisition']['fee']==modes['info-only-confirm']['acquisition']['fee']==0
assert modes['guard']['acquisition']['fee']==500000
for m in ('reinspect','info-only-confirm'):
    assert modes[m]['acquisition']['result']=='cancel'
    assert [c[2] for c in modes[m]['acquisition']['calls'] if c[0]=='0x8004d6ec']==[2]
assert modes['guard']['acquisition']['result']=='first_store_guard'
for m,d in modes.items():
    charges=[c[1][1] for c in d['acquisition']['calls'] if c[0]=='0x8001cbc4']
    assert charges==([500000] if m=='investigate' else [])
save,load=result('play-save.json'),result('play-load.json')
decoded,tables=result('read-decode.json'),result('loaded-runtime-tables.json')
assert save['play']['steps'][0]['view']==2 and save['play']['steps'][1]['view']==0
assert save['play']['actions']=={'0':64,'2':128}
assert decoded['saved_clock']==17534 and decoded['decoded_regions']==37 and decoded['file_reads']==892
card=(ROOT/'operating-menu-save.card-file.bin').read_bytes()
payload=card[512:512+SIZE]
assert len(card)==114688 and valid(payload)
assert struct.unpack_from('<I',payload,0x50)[0]==0xffffffff
assert hashlib.sha256(payload).hexdigest()==save['encoders'][0]['payload_sha256']==load['decode_checks'][0]['payload_sha256']
loaded=ROOT/'evidence/source/opened-snapshots-20261028/TOWN0001-menu-from-own-load-20261105-single.ram.zlib'
ram=zlib.decompress(loaded.read_bytes())
assert struct.unpack_from('<I',ram,0xcd97c)[0]==0 and struct.unpack_from('<I',ram,0x13796c)[0]==0xffffffff
natural=result('long-continuation-status.json')
assert natural['total_updates']==60 and natural['cases'][-1]['clock_after']==17640
exe=(algo/'source/SLPS_007.82').read_bytes()
assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
start,end=0x8005f500,0x8005f7f8
raw=exe[start-0x80010000+2048:end-0x80010000+2048]
instructions=dict(source_executable_sha256=hashlib.sha256(exe).hexdigest(),start=hex(start),end_exclusive=hex(end),
                  sha256=hashlib.sha256(raw).hexdigest(),words=[hex(w[0]) for w in struct.iter_unpack('<I',raw)])
(ROOT/'list-parent-source.json').write_text(json.dumps(instructions,indent=2)+'\n')
out=dict(all_passed=True,own_list_order=[0,2],list_input_branches=sorted(branches),
         reached_list_parent_checks=sum(len(d['list_parent_checks']) for d in (own,wrap)),
         own_store=dict(slot=2,flags=2,view=2,menu_function='0x80060418'),
         rival_store=dict(slot=1,flags=0x8001,cursor=[43,12],menu_function='0x80060d6c',
                          initial_fee=500000,initial_price=52704360,cancel_charged=False,
                          investigation_debit=500000,reinspection_debit=0,investigated_ui_information_only=True,affordable_founding_store_purchase_guard=True),
         saved_clock=17534,saved_selected=0xffffffff,decoded_regions=37,read_blocks=892,
         runtime_image_tables_verified=True,load_restored_view=0,
         natural_updates_added=60,natural_completed_iterations=8828,natural_clock=17640,
         cases_not_added_to_natural_count=['own','list-wrap','rival-map','investigate','reinspect','guard','menu-save','menu-load','own-list-wrap diagnostic'],
         limits=['List parent/control policy is independent; observed native child results and the previous child monitors remain shared.',
                 'Only reached valid list states with two own stores; no-own-store and invalid-row entry behavior not covered.',
                 'First list attempt named rival actually wrapped to own slot 0; retained under development-own-list-wrap rather than called rival coverage.',
                 'View/control/card claims are original logical execution under archived SDK/BIOS adapters, not hardware display or physical card communication.'])
(ROOT/'controls-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(all_passed=True,list_branches=sorted(branches),natural_clock=17640,decoded_regions=37)))
