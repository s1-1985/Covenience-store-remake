#!/usr/bin/env python3
"""Static source security, neighborhood facility cells and conditional theft data."""
import argparse, collections, hashlib, json, runpy, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))
    rows,read=lib['iso'](raw);files={r['path']:r for r in rows}
    def payload(path):r=files[path];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    def sb(b,o):return struct.unpack_from('<b',b,o)[0]
    decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    msg=payload(next(p for p in files if p.endswith('/MSG00.OBJ')))
    def message(index):
        off=struct.unpack_from('<I',msg,index*4)[0];codes=[]
        for j in range(256):
            v=struct.unpack_from('<H',msg,off+2*j)[0];codes.append(v)
            if v==0x40ff:return dict(index=index,offset=off,codes=codes,text=decode(codes))
        raise AssertionError('unterminated message')
    def inline(a):
        codes=[]
        for j in range(256):
            v=struct.unpack('<H',at(a+2*j,2))[0];codes.append(v)
            if v==0x40ff:return dict(address=hex(a),codes=codes,text=decode(codes))
        raise AssertionError('unterminated inline string')
    (ROOT/'source').mkdir(exist_ok=True)
    denom=list(struct.unpack('<6i',at(0x80098cf8,24)));assert denom==[250,250,275,275,300,300]
    facilities=[]
    for i,bonus in [(5,10),(6,5)]:
        b=at(0x8009da10+i*56,56);w,h,lo,hi=struct.unpack_from('<4i',b,24)
        facilities.append(dict(building=i,name=b[:24].split(b'\0',1)[0].decode('shift_jis'),size=[w,h],tile_range=[lo,hi],bonus_per_matching_cell=bonus,full_footprint_bonus=w*h*bonus,raw_hex=b.hex()))
    assert [(f['name'],f['tile_range']) for f in facilities]==[('交番',[60,63]),('消防署',[64,69])]
    profiles=[]
    for i in range(144):
        b=at(0x800a09d0+i*24,24);group=struct.unpack_from('<h',b)[0]
        profiles.append(dict(id=i,appearance_group=group,group_label=at(0x800a1750+group*23,21).split(b'\0',1)[0].decode('shift_jis'),raw_trait19=sb(b,19),security_threshold=100-sb(b,19),source_products=list(struct.unpack_from('<4b',b,8))))
    assert max(p['security_threshold'] for p in profiles)==90
    assert [p['id'] for p in profiles if p['raw_trait19']==10]==[94,103]
    fixtures=[]
    for i in range(53):
        b=at(0x80099f0c+i*196,196);words=list(struct.unpack('<49i',b));products=[]
        for v in words[21:48]:
            if v==-1:break
            products.append(v)
        cat=words[0]&255
        fixtures.append(dict(id=i,name=message(387+i)['text'],raw_flags=words[0],category=cat,
            immediate_payment=cat in [2,3,5],allowed_products=products))
    products=[]
    for i in range(27):
        b=at(0x8009cdf0+i*88,88);base,cost,setting=struct.unpack_from('<3i',b,24)
        allowed=[f for f in fixtures if i in f['allowed_products']]
        products.append(dict(id=i,name=b[:24].split(b'\0',1)[0].decode('shift_jis'),base_price=base,cost_percent=cost,initial_setting=setting,initial_unit_price=base*(cost+setting)//100,
            non_immediate_fixture_ids=[f['id'] for f in allowed if not f['immediate_payment']],immediate_fixture_ids=[f['id'] for f in allowed if f['immediate_payment']]))
    assert [p['id'] for p in products if not p['non_immediate_fixture_ids']]==[8,20,26]
    write('security-theft-masters.json',dict(schema_version=1,source_exe_sha256=EXE_SHA,security_staff_denominators=denom,
        neighborhood_facilities=facilities,profiles=profiles,fixture_payment_classes=fixtures,products=products,
        trait_label_note='Profile+19 was previously called manners; this work grounds the security comparison role, not a new original UI label.',
        conditional_profile_counts_by_security=[dict(security=s,count=sum(s<p['security_threshold'] for p in profiles)) for s in range(101)],
        source_label_note='Fixture labels decoded from source MSG00 using existing by-eye font table. Building/product/group labels are original Shift-JIS.'))
    # Same54->60 mapping as the prior full staff-roster extraction; only source-written fields used.
    fields=[(0,2),(2,1),(3,1),(4,1),(6,2),(8,2),(12,4),(16,4),(20,4)]+[(a,1) for a in range(24,47)]+[(47,10)]
    worlds=[];town_blob=bytearray()
    for mapname in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
        b=payload('/DAT/'+mapname+'.BIN');town=b[17:24017];town_blob.extend(town);staff=[]
        for i in range(35):
            packed=b[24017+i*54:24017+(i+1)*54];r=bytearray(60);pos=0
            for off,n in fields:r[off:off+n]=packed[pos:pos+n];pos+=n
            assert pos==54
            staff.append(dict(id=i,name=message(150+r[2])['text'],security=sb(r,34)))
        stores=[]
        for slot in range(10):
            s=b[25907+slot*5080:25907+(slot+1)*5080]
            if not s[0]:continue
            rect=list(struct.unpack_from('<4i',s,8));left,top,right,bottom=rect;tier=struct.unpack_from('<i',s,0xc70)[0]
            refs=list(struct.unpack_from('<3h',s,0xdd8));assigned=[staff[i] for i in refs if i!=-1];total=sum(p['security'] for p in assigned);base=total*100//denom[tier];cells=[]
            for y in range(max(0,top-7),min(49,bottom+7)+1):
                for x in range(max(0,left-7),min(59,right+7)+1):
                    tile=struct.unpack_from('<h',town,(y*60+x)*8)[0]
                    for f in facilities:
                        if f['tile_range'][0]<=tile<=f['tile_range'][1]:cells.append(dict(x=x,y=y,tile=tile,building=f['building'],bonus=f['bonus_per_matching_cell']))
            bonus=sum(c['bonus'] for c in cells);security=min(100,base+bonus)
            stores.append(dict(physical_slot=slot,rect=rect,tier=tier,staff_ids=refs,staff_security=assigned,
                raw_security_sum=total,denominator=denom[tier],staff_component=base,neighbor_cells=cells,neighborhood_component=bonus,source_security=security,
                below_threshold_profile_ids=[p['id'] for p in profiles if security<p['security_threshold']]))
        worlds.append(dict(map=mapname,town_source_sha256=sha(b),town_cells_sha256=sha(town),town_cells_packed_offset=len(town_blob)-len(town),stores=stores))
    assert [[s['source_security'] for s in w['stores']] for w in worlds]==[[89,58],[88,60,18],[59],[16,53,54,50,52]]
    write('initial-store-security.json',dict(worlds=worlds,
        scope='Arithmetic from original initial map/staff data, not a new gameplay run. Below-threshold IDs ignore wallet, stock, product reachability, season and appearance frequency; they are not theft probabilities.',
        source_town_cells_file='source/town-cells.bin',town_cells_bytes_per_map=24000,
        source_staff_reference='../20261114-staff-roster-growth-data/source/TOWN*-staff-packed.bin',
        source_store_reference='../20261114-parking-arrival-data/source/initial-active-stores.bin'))
    (ROOT/'source/town-cells.bin').write_bytes(town_blob)
    write('source-text.json',dict(theft_prefix=inline(0x80098e1c),theft_suffix=inline(0x80098e24),decoding='Original16-bit words plus existing by-eye font transcription; no new OCR.'))
    write('android-security-theft-bridge.json',dict(schema_version=1,
        security=dict(producer='800224e0 -> summary+08 via80023da0',staff='Sum signed current警備+22 for assigned slots, no task/energy filter. trunc(sum*100/denominator[tier]).',
            area='Inclusive rectangle(left-7,top-7,right+7,bottom+7), clipped to60x50 map.',
            neighborhood='Every matching cell60..63 adds10;64..69 adds5. Count matching cells, not anchors or buildings; partial intersection contributes partial bonus.',clamp='Upper clamp100 after additions; no new lower clamp.',
            decor='Fixture45/46/47 additions in summary builder feed service+0c, not this security+08. No new anti-theft equipment field is inferred.'),
        theft_gate=['At product goal and facing correct direction, compute current selling unit price and narrow to signed16.',
            'Books7 first pause ordinary purchase while security<100-profile19 and unsigned deadline>=clock.',
            'Underfunded path only when signed wallet<unit. Immediate categories2/3/5 do not take this theft branch.',
            'Require security<100-signed profile19, strictly. No separate theft random draw occurs in this local branch.',
            'Attempt group inventory removal via8003b420; failure is not theft. It can increment the separate stockout call counter.',
            'On success loss118c += unit*group_quantity; event flag0x10; return5 for exit. Do not register purchase statistics or charge selling-price loss again to cash.'],
        unchanged_locally='The theft-success block does not update wallet, cart+0a or cash, and does not increment product counters1198/11a0. Previous cart settlement is not newly invented here.',
        loss_meaning='Current selling price*group quantity, not procurement price and not a separate immediate cash debit.',
        rating_loss='In the rating-update branch gated here by hour0/stage1, nonzero118c decreases ratingC68 by1 once, then118c is cleared. Player-side message includes loss amount and face of slot0 manager; rival skips notification but still reaches reset. Overall later rating calculation can add other changes.',
        warning='Message event parameters(3,manager_portrait,35,1,0). Distinct from the immediate theft event flag0x10.',
        limits='No percentage theft probability inferred from profile counts. Security90 closes this comparison for all144 initial profiles; it does not prove protection from other incidents such as the separate robbery/fire routine.'))
    write('source-derived-examples.json',dict(scope='Source arithmetic examples, not new gameplay observations.',
        neighborhood=[dict(facility='交番',matching_cells=4,bonus=40),dict(facility='消防署',matching_cells=6,bonus=30),dict(facility='交番部分重なり',matching_cells=1,bonus=10)],
        boundaries=[dict(security=s,profile_trait19=10,threshold=90,below=s<90) for s in [89,90,100]],
        loss=dict(unit_selling_price=products[0]['initial_unit_price'],procurement_unit_cost=products[0]['base_price']*products[0]['cost_percent']//100,quantity=5,loss_counter_increase=products[0]['initial_unit_price']*5,immediate_cash_debit=0,
                  note='Uses initial cold-drink price/cost directly from the source master, provided non-immediate fixture and all other gates pass.'),
        rating=dict(nonzero_loss_counter=550,loss_penalty=-1,penalty_is_not_minus550=True)))
    spans=[('security_producer',0x800224e0,0x8002287c),('summary_security_link',0x80023d84,0x80023dcc),
        ('purchase_security_and_theft',0x8003473c,0x80034ccc),('immediate_classifier',0x800360a0,0x80036160),
        ('group_acquisition',0x8003b420,0x8003b570),('rating_loss',0x800281b4,0x800282fc)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);ranges=[];asm=[]
    for label,a,end in spans:
        data=at(a,end-a);(ROOT/'source'/f'{label}.bin').write_bytes(data);ranges.append(dict(name=label,address=hex(a),bytes=len(data),sha256=sha(data)))
        asm.append(f'\n# {label} {a:#x}..{end:#x}');asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(data,a))
    for label,a,n in [('denominators',0x80098cf8,24),('police-fire-buildings',0x8009da10+5*56,112),('profiles',0x800a09d0,144*24),
        ('fixture-master',0x80099f0c,53*196),('product-master',0x8009cdf0,27*88),('theft-text',0x80098e1c,0x80098e50-0x80098e1c)]:
        data=at(a,n);(ROOT/'source'/f'{label}.bin').write_bytes(data);ranges.append(dict(name=label,address=hex(a),bytes=n,sha256=sha(data)))
    write('source-ranges.json',ranges);(ROOT/'security-readers.asm').write_text('\n'.join(asm)+'\n')
    write('summary.json',dict(profiles=144,initial_stores=11,neighborhood_building_types=2,security_denominators=denom,
        initial_store_security={w['map']:[s['source_security'] for s in w['stores']] for w in worlds},
        maximum_initial_profile_threshold=90,immediate_fixture_count=sum(f['immediate_payment'] for f in fixtures),
        trait19_histogram=dict(sorted(collections.Counter(p['raw_trait19'] for p in profiles).items())),original_cpu_updates=0,
        known_before='Isolated theft gate, purchase control and neighborhood score models existed; this work connects all144 original traits, all53 fixture classes and initial11-store map/staff data, plus source loss notification.',
        unresolved='Separate robbery/fire incident frequency and complete end-to-end prior-cart handling are not newly established here.'))
    print(json.dumps(dict(profiles=144,stores=11,security=[[s['source_security'] for s in w['stores']] for w in worlds])))

if __name__=='__main__':main()
