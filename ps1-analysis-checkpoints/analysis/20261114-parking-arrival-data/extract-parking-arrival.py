#!/usr/bin/env python3
"""Static parking fixtures, layouts, map populations and arrival-group contracts."""
import argparse, collections, hashlib, json, runpy, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    helper=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))
    files,read=helper['iso'](raw);files={r['path']:r for r in files}
    def payload(name):r=files[name];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    def sb(b,o):return struct.unpack_from('<b',b,o)[0]
    decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    msg=payload(next(k for k in files if k.endswith('/MSG00.OBJ')))
    def name(index):
        pos=struct.unpack_from('<I',msg,index*4)[0];codes=[]
        for j in range(256):
            c=struct.unpack_from('<H',msg,pos+j*2)[0];codes.append(c)
            if c==0x40ff:return dict(message_index=index,offset=pos,codes=codes,text=decode(codes))
        raise AssertionError('no terminator')
    (ROOT/'source').mkdir(exist_ok=True)
    fixtures={}
    for i in range(53):
        words=list(struct.unpack('<49i',at(0x80099f0c+196*i,196)))
        if words[0]&255==10:
            fixtures[i]=dict(id=i,address=hex(0x80099f0c+196*i),raw_words=words,
                category=words[0]&255,capacity=words[3],logical_footprint=words[9:11],label=name(387+i))
    assert list(fixtures)==[50,51,52]
    assert [x['capacity'] for x in fixtures.values()]==[2,4,20]
    assert [x['label']['text'] for x in fixtures.values()]==['駐車場','2階建駐車場','タワー駐車場']
    max_groups=list(struct.unpack('<6i',at(0x80099db8,24)));assert max_groups==[10,10,15,15,20,20]
    def scan(data,w,h,grid_offset):
        anchors=[]
        for y in range(h):
            for x in range(w):
                off=grid_offset+y*112+x*4;v=struct.unpack_from('<I',data,off)[0];kind=v>>12&1023
                if v&0x80000000 and kind in fixtures:
                    f=fixtures[kind];rot=v>>22&3;fw,fh=f['logical_footprint']
                    if rot>=2:fw,fh=fh,fw
                    anchors.append(dict(x=x,y=y,fixture=kind,rotation=rot,raw_word=f'{v:08x}',
                        source_offset=off,footprint_subcells=[2*fw,2*fh],capacity=f['capacity']))
        return anchors
    layouts=[];layout_blob=at(0x800a2074,30*3108)
    for i in range(30):
        b=layout_blob[i*3108:(i+1)*3108];w,h=struct.unpack_from('<2i',b);anchors=scan(b,w,h,196)
        layouts.append(dict(id=i,address=hex(0x800a2074+i*3108),sha256=sha(b),size_subcells=[w,h],
            parking_anchors=anchors,own_parking_capacity=sum(a['capacity'] for a in anchors)))
    assert [x['id'] for x in layouts if x['own_parking_capacity']==0]==[0,5,10,15,20,25]
    external=payload('/DAT/SHOP0302.BIN');assert external[:194]+b'\0\0'+external[194:]==layout_blob[16*3108:17*3108]
    profiles=[];mode_by_id=[];all_modes=collections.Counter()
    for i in range(144):
        b=at(0x800a09d0+i*24,24);mode=sb(b,12);mode_by_id.append(mode);all_modes[mode]+=1
        if mode==3:
            g,hour,stay,budget=struct.unpack_from('<4h',b)
            label=at(0x800a1750+23*g,21).split(b'\0',1)[0].decode('shift_jis')
            profiles.append(dict(id=i,address=hex(0x800a09d0+i*24),raw_hex=b.hex(),appearance_group=g,
                group_label=label,arrival_hour=hour,stay_minutes=stay,budget=budget,arrival_mode=mode,
                product_ids=list(struct.unpack_from('<4b',b,8)),source_distance_limit=70))
    assert len(profiles)==14
    mixes=[list(struct.iter_unpack('<2h',at(0x8009ff1c+i*20,20))) for i in range(137)]
    worlds=[];store_blob=bytearray();store_ranges=[]
    for mapname in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
        b=payload('/DAT/'+mapname+'.BIN');modes=collections.Counter();invalid=[]
        for k in range(3000):
            mix=struct.unpack_from('<h',b,17+k*8+6)[0]
            if mix==-1:continue
            for profile,heads in mixes[mix]:
                if profile==-1:continue
                if 0<=profile<144:modes[mode_by_id[profile]]+=heads
                else:invalid.append(dict(x=k%60,y=k//60,mix=mix,profile=profile,heads=heads))
        stores=[];running_capacity=0
        for slot in range(10):
            source_off=25907+slot*5080;s=b[source_off:source_off+5080]
            if not s[0]:continue
            w,h=struct.unpack_from('<2i',s,0x44);tier=struct.unpack_from('<i',s,0xc70)[0];anchors=scan(s,w,h,0x108)
            own=sum(a['capacity'] for a in anchors);running_capacity+=own
            packed_off=len(store_blob);store_blob.extend(s)
            store_ranges.append(dict(map=mapname,physical_slot=slot,source_offset=source_off,
                packed_offset=packed_off,bytes=len(s),sha256=sha(s)))
            stores.append(dict(physical_slot=slot,owner_flags=struct.unpack_from('<H',s,4)[0],
                size_subcells=[w,h],tier_index=tier,customer_record_limit=max_groups[tier],parking_anchors=anchors,
                own_parking_capacity=own,source_capacity_after_physical_slot_carryover=running_capacity))
        worlds.append(dict(map=mapname,source_town_sha256=sha(b),valid_profile_population_by_arrival_mode=dict(sorted(modes.items())),
            parking_mode_population_heads=modes[3],invalid_profile_entries=invalid,initial_active_stores=stores))
    assert [w['parking_mode_population_heads'] for w in worlds]==[232,249,191,133]
    assert [[s['source_capacity_after_physical_slot_carryover'] for s in w['initial_active_stores']] for w in worlds]==[[20,40],[20,40,60],[20],[24,36,48,60,72]]
    write('parking-arrival-data.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,
        parking_fixtures=list(fixtures.values()),customer_record_limits=max_groups,all_profile_arrival_mode_counts=dict(sorted(all_modes.items())),
        parking_required_profiles=profiles,builtin_layouts=layouts,worlds=worlds,
        external_layout=dict(path='/DAT/SHOP0302.BIN',sha256=sha(external),matches_layout=16,parking_capacity=layouts[16]['own_parking_capacity']),
        meaning='Population heads describe initial map mix composition, not measured per-day visitors. Parking capacity is a scalar used against group head counts, not one space per customer record. Modes0..2 receive no new transport labels.',
        label_provenance='Fixture label words freshly read from MSG00.OBJ387+id, using existing by-eye font transcription; not new OCR. Appearance group labels are source Shift-JIS.'))
    write('initial-store-ranges.json',dict(file='source/initial-active-stores.bin',stores=store_ranges))
    (ROOT/'source/initial-active-stores.bin').write_bytes(store_blob)
    example_inputs=[(5,3,2),(5,4,2),(5,4,4),(9,4,2)]
    examples=[]
    for demand,capacity,used in example_inputs:
        request=min(demand,5);overflow=used+request>capacity;first=demand-request if overflow else demand
        admitted=max(capacity-used,0) if overflow else request
        final=first-admitted if admitted else first
        examples.append(dict(demand_before=demand,capacity=capacity,occupied=used,requested=request,
            overflow=overflow,after_overflow_deduction=first,admitted=admitted,after_creation_deduction=final,
            complaint_increment=int(overflow),visitor_count_increment=admitted,
            reason='created' if admitted else 'no new record'))
    assert examples[0]['after_creation_deduction']==-1 and examples[2]['admitted']==0
    write('source-derived-examples.json',dict(scope='Arithmetic from source expressions, not runtime observations.',
        arrivals=examples,group_limit=dict(tier0_records=10,maximum_heads_if_each_group_is5=50,not_a_parking_capacity=True)))
    write('android-parking-arrival-bridge.json',dict(schema_version=1,
        fixtures='Only anchored fixtures with kind<53 and(master_flags&255)==10 contribute master+12 capacity. Sum once per anchor, not every covered cell. Rotate footprint when direction>=2.',
        capacity_carry='Summary builder clears parking accumulator once before physical-slot loop0..9. Active later stores inherit previous active stores capacity; not a per-store reset.',
        occupied_rebuild='80022bf4 scans tier-limited customer records. Count group quantity+1e only if state!=0 AND profile+12==3. Coordinates and exact active state1..5 do not filter it.',
        record_limit='10,10,15,15,20,20 indexed by store+C70. These are group-record counts, not total people or parking slots.',
        candidate='Open store, first free record, RNG&3==0. Choose random starting profile modulo144 then advance before checking. Eligibility uses schedule at profile arrival hour and signed16 remaining demand>0. Request=min(demand,5).',
        parking_gate='Only arrival mode3: if occupied+request>capacity, increment signed complaint12e3 if<127, deduct ORIGINAL request from u16 pending demand, and set flag0x40. Then request=capacity-occupied. <=0 means no new record this attempt; do not retry a different profile here.',
        creation='Initialize one state1 customer record with admitted group quantity and one randomly chosen appearance. Deduct admitted quantity from pending demand again, add admitted quantity to summary occupied14 and store visitor count1188. The summary increment is unconditional in this local block, even for modes0..2; the rebuild later counts only active mode3 records.',
        signed_demand='The table is written with low16-bit subtraction but candidates read signed16 and require>0. Partial overflow can make a negative value; preserve it rather than clamping or treating as huge unsigned demand.',
        people_vs_objects='One source customer record and one image represent up to5 admitted heads. Do not expand a group into5 independent source records or debit parking once per record.',
        entry='State1 later attempts edge entry via800331b4: one random edge, ordered scan for empty cell with route marker-2. Failing that edge returns1 and retries in a later update; no fallback scan of all4 edges within this call.',
        warning='12e3 increments once per overflow branch, including partial admission. Original detailed warning displays raw count as people; see prior checkout-waiting report for thresholds and resets.',
        scope='Static source data plus code contract. Existing isolated spawn/parking models are reused as prior knowledge; no CPU-run extension or new gameplay timing measurement.'))
    spans=[('occupied_parking_heads',0x80022bf4,0x80022d28),('metric_capacity',0x80023c20,0x800248b0),
        ('arrival_allocate',0x800319ac,0x800320cc),('edge_entry',0x800331b4,0x800340fc)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];ranges=[]
    for name_,a,end in spans:
        data=at(a,end-a);(ROOT/'source'/f'{name_}.bin').write_bytes(data)
        ranges.append(dict(name=name_,address=hex(a),bytes=len(data),sha256=sha(data)));asm.append(f'\n# {name_} {a:#x}..{end:#x}')
        asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(data,a))
    for name_,a,n in [('layouts',0x800a2074,30*3108),('parking-fixtures',0x80099f0c+50*196,3*196),
        ('shopping-profiles',0x800a09d0,144*24),('customer-mixes',0x8009ff1c,137*20),('customer-record-limits',0x80099db8,24)]:
        data=at(a,n);(ROOT/'source'/f'{name_}.bin').write_bytes(data);ranges.append(dict(name=name_,address=hex(a),bytes=n,sha256=sha(data)))
    (ROOT/'parking-readers.asm').write_text('\n'.join(asm)+'\n');write('source-ranges.json',ranges)
    write('summary.json',dict(parking_fixture_types=3,parking_required_profiles=14,builtin_layouts=30,layouts_without_own_parking=[0,5,10,15,20,25],
        initial_active_stores=sum(len(w['initial_active_stores']) for w in worlds),initial_parking_mode_population_heads={w['map']:w['parking_mode_population_heads'] for w in worlds},
        customer_record_limits=max_groups,original_cpu_updates=0,
        newly_connected='Parking fixtures and capacities for30 layouts/11 starting stores;14 mode3 profiles and4-map mix heads; source occupancy/rejected-partial-group effects with pending-demand signedness.',
        known_before='Isolated parking/spawn logic and cross-store capacity carryover already existed. This work binds them to all source layouts and actual map populations.',
        not_claimed='Initial population mix is not a daily visitor forecast; no new transport label for modes0..2; no real-time entry delay measured.'))
    print(json.dumps(dict(fixtures=len(fixtures),layouts=len(layouts),parking_profiles=len(profiles),active_stores=sum(len(w['initial_active_stores']) for w in worlds))))

if __name__=='__main__':main()
