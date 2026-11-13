#!/usr/bin/env python3
"""Extract customer wait/service masters and the original complaint/growth links."""
import argparse, collections, hashlib, json, runpy, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent
DISC_SHA = '8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA = 'd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'

def write(name, data):
    (ROOT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('disc',type=Path); args=ap.parse_args()
    raw=args.disc.read_bytes(); assert hashlib.sha256(raw).hexdigest()==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))
    files, read=lib['iso'](raw); entry=next(x for x in files if x['path']=='/SLPS_007.82')
    exe=read(entry['lba'],entry['bytes']); assert hashlib.sha256(exe).hexdigest()==EXE_SHA
    def at(a,n): return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    def sb(b,o): return struct.unpack_from('<b',b,o)[0]
    decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    (ROOT/'source').mkdir(exist_ok=True)
    profiles=[]
    for i in range(144):
        b=at(0x800a09d0+24*i,24); group=struct.unpack_from('<h',b)[0]
        label=at(0x800a1750+23*group,21).split(b'\0',1)[0].decode('shift_jis')
        profiles.append(dict(id=i,appearance_group=group,appearance_group_label=label,
                             raw_hex=b.hex(),primary_product=sb(b,8),
                             initial_wait_budget=sb(b,17),service_and_sidestep_gate=sb(b,18)))
    assert min(x['initial_wait_budget'] for x in profiles)==10
    assert max(x['initial_wait_budget'] for x in profiles)==100
    assert [x['id'] for x in profiles if x['service_and_sidestep_gate']==9]==[102]
    write('customer-checkout-data.json',dict(schema_version=1,source_exe_sha256=EXE_SHA,
        table_address='0x800a09d0',stride=24,count=144,profiles=profiles,
        field_meanings={'17':'Copied once into customer+1c at allocation; wait-resolution decrements this budget. Earlier exporter called it stamina.',
                        '18':'Second cashier-success roll and obstruction sidestep/replan threshold. Earlier exporter called it quickness. These are code-derived roles, not original UI labels.'},
        preserve_unusual_value='Profile102 is9, not90; do not repair to a rounded tens value.'))
    messages=[]
    addresses=[0x80098f4c,0x80098f6c,0x80098f80,0x80098fa8,0x80098fc4,0x80098fdc,0x80099000,0x80099024,0x8009903c,0x80099060]
    for a in addresses:
        codes=[]
        for j in range(256):
            v=struct.unpack('<H',at(a+j*2,2))[0]; codes.append(v)
            if v==0x40ff:break
        else: raise AssertionError('unterminated source message')
        messages.append(dict(address=hex(a),codes=codes,text=decode(codes)))
    write('complaint-text-data.json',dict(source_exe_sha256=EXE_SHA,messages=messages,
        decoding='Existing by-eye font transcription reused; fresh source words decoded here, no new OCR.',
        channels=[dict(counter='store+0x12e1',meaning='wait resolution exhaustion/force calls',threshold='trunc((100-manager_academic)/10)+1',low=hex(addresses[0]),high_prefix=hex(addresses[1]),high_suffix=hex(addresses[2])),
                  dict(counter='store+0x12e2',meaning='failed acquisition calls',threshold='trunc((100-manager_academic)/4)+5',low=hex(addresses[3]),high_prefix=hex(addresses[4]),high_suffix=hex(addresses[5])),
                  dict(counter='store+0x12e3',meaning='parking-overflow branch occurrences',threshold='trunc((100-manager_academic)/4)+5',low=hex(addresses[6]),high_prefix=hex(addresses[7]),high_suffix=hex(addresses[8]))],
        gate='Strict counter>threshold; academic<70 uses low-detail text, >=70 inserts the raw counter into the high-detail text. Text says people, but these writers increment once per triggering call/branch, without multiplying by group quantity.',
        cleaning='counter12e4>=4 then one roll1..100<=academic; text0x80099060',
        reset='All4 counters cleared at minute0 with(hour&3)==0; also after queued warning and after rare statistics block. Rival-flag stores return before this reporting path.'))
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    targets={0x80035d58:[],0x8003aa58:[]}
    for off in range(2048,len(exe)-3,4):
        word=struct.unpack_from('<I',exe,off)[0];pc=0x80010000+off-2048
        target=((pc+4)&0xf0000000)|((word&0x3ffffff)<<2)
        if word>>26==3 and target in targets: targets[target].append(pc)
    assert targets[0x80035d58]==[0x8003501c,0x800351d0,0x800352ac,0x8003567c]
    assert targets[0x8003aa58]==[0x80035f9c,0x80037534,0x8003771c,0x80038868]
    write('direct-call-sites.json',{hex(k):[hex(x) for x in v] for k,v in targets.items()})
    spans=[('customer_allocation_wait',0x80031e3c,0x80031f24),
           ('purchase_wait_call',0x80034f4c,0x80035128),
           ('checkout_control',0x80035128,0x80035770),
           ('wait_resolution',0x80035d58,0x800360a4),
           ('cashier_service',0x8003839c,0x80038894),
           ('growth_entry',0x8003aa58,0x8003ab24),
           ('growth_minus_one',0x8003b158,0x8003b278),
           ('advice',0x8003b570,0x8003bf28),
           ('cashier_busy_reset',0x80024a10,0x80024aa0),
           ('revenue_commit',0x8001ca7c,0x8001cbc8)]
    manifest=[]; asm=[]
    for name,a,b in spans:
        data=at(a,b-a);(ROOT/'source'/f'{name}.bin').write_bytes(data)
        manifest.append(dict(name=name,address=hex(a),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
        asm.append(f'\n# {name} {a:#x}..{b:#x}')
        asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(data,a))
    for name,a,n in [('shopping-profiles',0x800a09d0,144*24),('complaint-text',0x80098f4c,0x80099080-0x80098f4c)]:
        data=at(a,n);(ROOT/'source'/f'{name}.bin').write_bytes(data)
        manifest.append(dict(name=name,address=hex(a),bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    write('source-ranges.json',manifest);(ROOT/'checkout-readers.asm').write_text('\n'.join(asm)+'\n')
    write('android-checkout-waiting-bridge.json',dict(schema_version=1,
        customer_fields={'0x1c':'remaining wait budget, initialized from profile+17','0x0a':'signed16 cart amount per group member','0x1e':'signed8 group quantity'},
        wait_order=['Always consume first rand()%100+1 roll, even while patience remains positive.',
                    'Force argument!=0 sets wait budget0. Otherwise positive budget consumes a second RNG; rand()&3==0 decrements1.',
                    'Budget still positive returns1 without payment, penalty or complaint increment.',
                    'Budget<=0 sets event flag0x20. Nonzero cart is paid through8001ca7c(store,cart*group_quantity,1), then cart becomes0.',
                    'Use the saved first roll for both penalty gates. roll%3==0 calls growth(mode=-1) for each occupied slot0..2. roll%10==0 decrements store+C68 only if>=6.',
                    'Increment signed store+12e1 by1 if<127; return0. Counter increment is independent of group quantity and the two penalty gates.'],
        growth_penalty='All assigned employees, not just the current cashier: decrease fields1e,1f,21,22 by1 when>=2. Do not decrease service20 or basic traits. Each growth call still consumes its entry RNG even for mode-1.',
        gate_coupling='There are33 multiples of3 and10 multiples of10 in rolls1..100, with3 overlaps(30,60,90). These are roll bucket counts, not measured independent RNG probabilities.',
        callers=[dict(call='0x8003501c',force=0,context='purchase control: blocked movement after sidestep did not resolve'),
                 dict(call='0x800351d0',force=1,context='checkout with nonzero cart, no goal, destination search returns nonzero'),
                 dict(call='0x800352ac',force=0,context='at checkout goal after cashier service returned failure'),
                 dict(call='0x8003567c',force=0,context='checkout travel blocked after sidestep returned nonzero')],
        cashier='Customer and employee facing cells must resolve to the same fixture anchor. Search assigned slots0..2; employee task1 and busy0 required. Mark busy1 before rolls; first eligible employee is used, and failure does not continue to another employee in this call.',
        service_rolls='First roll1..100<=employee cashier1e; only if passed, second roll1..100<=profile18. Both pass calls growth(mode1). Busy flag remains set even if either roll fails.',
        busy_reset='0x80024a10..80024aa0 clears the three per-store metadata busy words. Preserve this explicit preparation boundary instead of clearing after each customer.',
        success='Checkout parent charges cart*group_quantity through same revenue routine, zeroes cart, sets flag0x200 and returns4. The wait path instead sets0x20 and checkout parent returns5.',
        not_inferred=['No real-time wait seconds measured.','No automatic dropping/restoring stock on complaint inferred.','No purpose/unlock for TOWNPS staff27 ownerFFFF established.']))
    write('source-derived-examples.json',dict(scope='Arithmetic examples from original formulas, not runtime observations.',
        group_charge=dict(cart=1200,group_quantity=5,revenue=6000,wait_complaint_increment=1),
        coupled_rolls=[dict(roll=r,all_staff_penalty=r%3==0,rating_penalty_when_ge6=r%10==0) for r in [3,10,30,31]],
        thresholds=[dict(manager_academic=a,wait_threshold=(100-a)//10+1,first_wait_complaint_count=(100-a)//10+2,stock_parking_threshold=(100-a)//4+5,first_stock_parking_count=(100-a)//4+6,high_detail=a>=70) for a in [0,69,70,100]]))
    write('summary.json',dict(profiles=144,wait_initial_range=[10,100],service_gate_range=[9,100],
        wait_budget_histogram=dict(sorted(collections.Counter(x['initial_wait_budget'] for x in profiles).items())),
        service_gate_histogram=dict(sorted(collections.Counter(x['service_and_sidestep_gate'] for x in profiles).items())),
        profile102_gate=9,direct_wait_calls=4,direct_growth_calls=4,source_complaint_strings=len(messages),original_cpu_updates=0,
        known_before='Isolated wait_resolution, cashier service and store_advice models existed. This work links them to all144 original profile records, original text, caller contexts and the full occupied-staff penalty scope.',
        unresolved='TOWNPS staff27 ownerFFFF purpose remains unestablished.'))
    print(json.dumps(dict(profiles=len(profiles),messages=len(messages),wait_calls=len(targets[0x80035d58])),ensure_ascii=False))

if __name__=='__main__': main()
