#!/usr/bin/env python3
"""Original permit fees, map masks, all valid2x2 candidate rectangles and layouts."""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    helper=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))
    rows,read=helper['iso'](raw);files={r['path']:r for r in rows}
    def payload(p):r=files[p];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    def sb(b,o):return struct.unpack_from('<b',b,o)[0]
    decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    msg=payload(next(k for k in files if k.endswith('/MSG00.OBJ')))
    def message(i):
        off=struct.unpack_from('<I',msg,4*i)[0];codes=[]
        for j in range(256):
            v=struct.unpack_from('<H',msg,off+2*j)[0];codes.append(v)
            if v==0x40ff:return dict(index=i,source_offset=off,codes=codes,text=decode(codes))
        raise AssertionError('no terminator')
    (ROOT/'source').mkdir(exist_ok=True)
    fees=list(struct.unpack('<3i',at(0x800b92d0,12)));assert fees==[3000000,7000000,10000000]
    permits=[dict(id=i,label=message(24+i),product=p,store_offset=hex(0xc74+i),fee=fees[i],town_mask=bit,range_cells=radius,
        selection_bit=1<<i,missing_validation_reason=i+1) for i,(p,bit,radius) in enumerate([(8,4,5),(2,2,7),(22,1,10)])]
    products=[]
    for i in range(27):
        b=at(0x8009cdf0+88*i,88);images=[]
        for im in struct.unpack_from('<12i',b,36):
            if im==-1:break
            images.append(im*3+360)
        products.append(dict(id=i,name=b[:24].split(b'\0',1)[0].decode('shift_jis'),images=images))
    def product_for_image(im):return next((p for p in products if any(v//3==im//3 for v in p['images'])),None)
    layouts=[]
    for i in range(30):
        b=at(0x800a2074+3108*i,3108);w,h=struct.unpack_from('<2i',b);goods=[];required=0
        for y in range(h):
            for x in range(w):
                v=struct.unpack_from('<I',b,196+y*112+x*4)[0];im=v>>12&1023
                if not 360<=im<640:continue
                p=product_for_image(im);assert p is not None
                license_=next((q for q in permits if q['product']==p['id']),None)
                if license_:
                    required|=license_['selection_bit'];goods.append(dict(x=x,y=y,image=im,quantity=v>>24&127,product=p['id'],permit=license_['id']))
        layouts.append(dict(id=i,source_sha256=sha(b),required_permit_mask=required,required_permit_ids=[q['id'] for q in permits if required&q['selection_bit']],restricted_goods_cells=goods))
    transitions=[]
    for old in range(8):
        for selected in range(8):
            added=selected&~old;cost=sum(q['fee'] for q in permits if added&q['selection_bit'])
            transitions.append(dict(old_mask=old,selected_mask=selected,dialog_excluded_mask=selected^7,new_mask=old|selected,newly_charged_mask=added,fee=cost))
    worlds=[];mask_blob=bytearray();candidate_blob=bytearray()
    for name in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
        b=payload('/DAT/'+name+'.BIN');town=b[17:24017];raw_flags=town[5::8];flags=bytearray(3000);stores=[]
        for k in range(3000):
            category=sb(town,k*8+4);flags[k]=0 if category<=0 else 16 if category in (3,4,5) else 24
        for i in range(10):
            s=b[25907+5080*i:25907+5080*(i+1)]
            if not s[0]:continue
            left,top,right,bottom=struct.unpack_from('<4i',s,8);lic=list(s[0xc74:0xc77]);stores.append(dict(slot=i,flags=struct.unpack_from('<H',s,4)[0],rect=[left,top,right,bottom],permits=lic))
            for y in range(max(0,top-10),min(49,bottom+10)+1):
                for x in range(max(0,left-10),min(59,right+10)+1):
                    k=y*60+x
                    if lic[2]:flags[k]|=1
                    if left-7<=x<=right+7 and top-7<=y<=bottom+7 and lic[1]:flags[k]|=2
                    if left-5<=x<=right+5 and top-5<=y<=bottom+5 and lic[0]:flags[k]|=4
                    if left-4<=x<=right+4 and top-4<=y<=bottom+4:flags[k]|=8
        hist=collections.Counter();first={};all_masks=[];raw_candidate=[];allowed_subset=[0]*8;blocked=0
        for y in range(49):
            for x in range(59):
                keys=[y*60+x,y*60+x+1,(y+1)*60+x,(y+1)*60+x+1]
                mask=0;rm=0
                for k in keys:mask|=flags[k];rm|=raw_flags[k]
                all_masks.append(mask);raw_candidate.append(rm)
                if mask&8:blocked+=1;continue
                avail=sum(q['selection_bit'] for q in permits if not mask&q['town_mask'])
                hist[avail]+=1;first.setdefault(avail,[x,y])
                for subset in range(8):
                    if subset&avail==subset:allowed_subset[subset]+=1
        offset=len(mask_blob);mask_blob.extend(raw_flags);mask_blob.extend(flags)
        co=len(candidate_blob);candidate_blob.extend(raw_candidate);candidate_blob.extend(all_masks)
        worlds.append(dict(map=name,source_town_sha256=sha(b),stores=stores,raw_flags_offset=offset,rebuilt_flags_offset=offset+3000,
            raw_vs_rebuilt_changed_cells=sum(a!=c for a,c in zip(raw_flags,flags)),candidate_raw_offset=co,candidate_rebuilt_offset=co+2891,
            candidate_rectangles=2891,base_siting_blocked=blocked,base_siting_allowed=2891-blocked,
            available_permit_mask_histogram=dict(sorted(hist.items())),first_candidate_by_available_mask=dict(sorted(first.items())),eligible_count_by_requested_subset=allowed_subset))
    assert [w['raw_vs_rebuilt_changed_cells'] for w in worlds]==[1459,1894,791,1541]
    assert [w['base_siting_allowed'] for w in worlds]==[2030,1789,2182,1526]
    assert [w['eligible_count_by_requested_subset'][7] for w in worlds]==[1433,985,1884,1201]
    (ROOT/'source/map-mask-bytes.bin').write_bytes(mask_blob);(ROOT/'source/candidate-mask-bytes.bin').write_bytes(candidate_blob)
    write('permit-siting-data.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,permits=permits,fee_transitions=transitions,
        layouts=layouts,worlds=worlds,mask_schema=dict(cell_file='source/map-mask-bytes.bin',cell_grid=[60,50],cell_bytes=1,candidate_file='source/candidate-mask-bytes.bin',candidate_grid=[59,49],candidate_bytes=1,order='row-major; each map stores raw then rebuilt bytes; see offsets',candidate_value='OR of4 town-cell masks for inclusive2x2 rectangle'),
        scope='All candidate counts use rebuilt flags from original initial map categories and11 active store permit states. Overlapping candidate rectangles are separate positions, not simultaneous store capacity; prices, cash and later map changes are not included.'))
    write('android-permit-siting-bridge.json',dict(schema_version=1,
        raw_vs_runtime='Original new-game caller5DAF4 loadsTOWN via1A0B8 then5DAFC calls1F8BC to rebuild masks. Treat stored byte5 as source evidence, not immutable runtime restriction data.',
        rebuild='Reset all3000 cell masks from signed category+4: <=0=>0, categories3/4/5=>16, other positive=>24. For each active store of either owner, drug flagC76 addsbit1 in expanded rectangle10; alcoholC75 bit2/range7; tobaccoC74 bit4/range5; all active stores add siting bit8/range4. Rectangles inclusive and map-clipped.',
        site='Native company-store descriptor0 has footprint2x2 and low-byte category2. Valid2x2 map rectangle cannot contain bit8. This is separate from permit bit1/2/4 checks.',
        permit_query='1E660 returns1 if any cell in requested rectangle has corresponding bit4,2,1;0 means no restriction. Its first child41290 only recognizes all-zero rectangle, not a general bounds check. Valid edge rectangles with some zero coordinates must still scan.',
        old_permits='Reconfiguration computes available=(query==0) OR old permit. Existing permit is preserved even if own/nearby mask would now block new issuance; no self-store removal is required to explain this path.',
        selection='UI caller translates dialog excluded bits1/2/4 into selected flags for tobacco/alcohol/drug. Town restriction bits for same order are4/2/1; keep these encodings distinct.',
        fee='For selected permit whose current flag is0, set flag1 and add source fee. No fee for previously held permit. Cash>=sum succeeds locally; insufficient cash restores old3 flags. All3 from none cost20000000. This path does not issue refunds/revoke previously held permits when excluded in a returned selection.',
        parent_commit='Premises screens provisionally deduct cash. Existing-store reconfigure63E44 restores saved cash/ledger around the screen, then posts final permit/size fees via1CBC4. If later interior stage cancels, post negative fees and restore snapshot/old permits before retry. Do not keep provisional debit and also post final charge.',
        product_check='Interior preflight788C8 scans all image fields360..639 even ifquantity0; product8 requiresC74,2 requiresC75,22 requiresC76. Reasons1/2/3 can later be overwritten by other layout errors. Empty shelf with retained product image is not automatically exempt.',
        scope='These are original game rules, not statements about real licensing law. Map overlays change when store/town state changes; initial candidate tables are not permanent city permissions.'))
    write('source-derived-examples.json',dict(scope='Source arithmetic/encoding examples, not new gameplay runs.',
        fees=dict(from_none_all=20000000,already_tobacco_then_all=17000000,already_all_then_all=0),
        encodings=[dict(permit=q['id'],town_mask=q['town_mask'],selection_bit=q['selection_bit']) for q in permits],
        range_example=dict(existing_rect=[20,20,21,21],tobacco_affected_cells=[15,15,26,26],two_by_two_candidate_origins_intersecting_tobacco=[14,14,26,26],
            note='Only this store influence, away from boundaries. Any one of candidate4 cells intersecting the affected region is sufficient.'),
        rectangles=dict(all_zero=[0,0,0,0],valid_corner_candidate=[0,0,1,1],note='Only all-zero is the sentinel; do not reject every rectangle with left/top0.')))
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);ranges=[];asm=[]
    spans=[('permit_query',0x8001e660,0x8001e8cc),('store_siting',0x8001e8cc,0x8001f1c0),('mask_rebuild',0x8001f8bc,0x8001ff38),
        ('zero_rect',0x80041290,0x80041320),('permit_dialog',0x800422a4,0x80042c7c),('premises_permission_commit',0x8006e4bc,0x8006e97c),
        ('existing_store_reconfigure',0x80063e44,0x800640e4),('product_permission_preflight',0x800788c8,0x80078a58),('load_then_rebuild',0x8005dae4,0x8005db04)]
    for label,a,end in spans:
        b=at(a,end-a);(ROOT/'source'/f'{label}.bin').write_bytes(b);ranges.append(dict(name=label,address=hex(a),bytes=len(b),sha256=sha(b)))
        asm.append(f'\n# {label} {a:#x}..{end:#x}');asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(b,a))
    for label,a,n in [('permit-fees',0x800b92d0,12),('company-store-descriptor',0x8009d738,56)]:
        b=at(a,n);(ROOT/'source'/f'{label}.bin').write_bytes(b);ranges.append(dict(name=label,address=hex(a),bytes=n,sha256=sha(b)))
    write('source-ranges.json',ranges);(ROOT/'permit-readers.asm').write_text('\n'.join(asm)+'\n')
    write('source-dependencies.json',dict(town_cells='../20261114-security-theft-data/source/town-cells.bin',layouts='../20261114-parking-arrival-data/source/layouts.bin',initial_stores='../20261114-parking-arrival-data/source/initial-active-stores.bin',source_note='Existing raw source files reused; this extractor itself rereads the disc and exports derived mask bytes.'))
    write('summary.json',dict(permit_types=3,fee_transitions=64,layouts=30,candidate_rectangles_per_map=2891,total_candidate_rectangles=11564,
        base_siting_allowed={w['map']:w['base_siting_allowed'] for w in worlds},all3_permits_allowed={w['map']:w['eligible_count_by_requested_subset'][7] for w in worlds},
        raw_rebuilt_differences={w['map']:w['raw_vs_rebuilt_changed_cells'] for w in worlds},original_cpu_updates=0,
        known_before='Isolated town mask builder, permit query and premises controls existed. This work binds original fees/labels/3 encodings to all4 maps,11564 candidate rectangles,30 source layouts and64 prior/new permit combinations.',
        remaining='Not a new playable building/permit UI or APK; monetary land/demolition stages are not included in candidate counts.'))
    print(json.dumps(dict(permits=3,candidates=11564,base=[w['base_siting_allowed'] for w in worlds],all3=[w['eligible_count_by_requested_subset'][7] for w in worlds])))

if __name__=='__main__':main()
