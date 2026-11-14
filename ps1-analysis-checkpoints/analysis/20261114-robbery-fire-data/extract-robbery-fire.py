#!/usr/bin/env python3
"""Original incident labels, gates, static layout loss classes and facility cover."""
import argparse, collections, hashlib, json, runpy, struct
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
        off=struct.unpack_from('<I',msg,i*4)[0];codes=[]
        for j in range(256):
            v=struct.unpack_from('<H',msg,off+2*j)[0];codes.append(v)
            if v==0x40ff:return dict(id=i,offset=off,codes=codes,text=decode(codes))
        raise AssertionError('no terminator')
    (ROOT/'source').mkdir(exist_ok=True)
    messages=[message(i) for i in [467,468,469]]
    assert '強盗' in messages[0]['text'] and '火災' in messages[1]['text']
    facilities=[]
    for incident_index,table_index,building_id in [(0,18,5),(1,19,6)]:
        a=0x8009d738+56*table_index;assert a==0x8009da10+56*building_id
        b=at(a,56);lo,hi=struct.unpack_from('<2i',b,32)
        facilities.append(dict(incident=incident_index,incident_table_index=table_index,building_master_id=building_id,address=hex(a),name=b[:24].split(b'\0',1)[0].decode('shift_jis'),tile_range=[lo,hi]))
    fixtures=[]
    for i in range(53):
        w=list(struct.unpack('<49i',at(0x80099f0c+196*i,196)));cat=w[0]&255
        fixtures.append(dict(id=i,name=message(387+i)['text'],category=cat,price=w[1],size=w[9:11],survives_fire_class=cat in [4,6]))
    assert [f['id'] for f in fixtures if f['survives_fire_class']]==[37,38,39,40,41,42,48,49]
    products=[]
    for i in range(27):
        b=at(0x8009cdf0+i*88,88);base,cost=struct.unpack_from('<2i',b,24);images=[]
        for image in struct.unpack_from('<12i',b,36):
            if image==-1:break
            images.append(image*3+360)
        products.append(dict(id=i,unit_cost=base*cost//100,runtime_images=images))
    def product_for_image(im):
        return next((p for p in products if any(v//3==im//3 for v in p['runtime_images'])),None)
    layouts=[]
    for i in range(30):
        a=0x800a2074+3108*i;b=at(a,3108);w,h=struct.unpack_from('<2i',b);anchors=[]
        for y in range(h):
            for x in range(w):
                word=struct.unpack_from('<I',b,196+y*112+x*4)[0];kind=word>>12&1023
                if not(word&0x80000000 and kind<53):continue
                stock=struct.unpack_from('<I',b,196+(y+1)*112+x*4)[0];image=stock>>12&1023;qty=stock>>24&127
                p=product_for_image(image) if image else None
                assert not image or p is not None
                anchors.append(dict(x=x,y=y,fixture=kind,rotation=word>>22&3,retained=fixtures[kind]['survives_fire_class'],
                    equipment_value=fixtures[kind]['price'],stock_image=image,stock_quantity=qty,stock_product=p['id'] if p else None,inventory_value=p['unit_cost']*qty if p else 0))
        def value(items):return sum(x['equipment_value']+x['inventory_value'] for x in items)
        retained=[x for x in anchors if x['retained']];removed=[x for x in anchors if not x['retained']]
        layouts.append(dict(id=i,source_sha256=sha(b),size_subcells=[w,h],anchors=anchors,fixture_count=len(anchors),retained_fixture_count=len(retained),removed_fixture_count=len(removed),
            equipment_value=sum(x['equipment_value'] for x in anchors),inventory_procurement_value=sum(x['inventory_value'] for x in anchors),assets_gate_value=value(anchors),assets_gate_pass=value(anchors)>99999,
            retained_value_by_class=value(retained),removed_value_by_class=value(removed)))
    assert sum(x['assets_gate_pass'] for x in layouts)==24
    assert all(x['retained_fixture_count']==2 for x in layouts if x['fixture_count'])
    profiles=[]
    for i in range(144):
        b=at(0x800a09d0+24*i,24);g=struct.unpack_from('<h',b)[0];trait=sb(b,19)
        profiles.append(dict(id=i,trait19=trait,passes_incident_customer_trait=trait<31,
            group_label=at(0x800a1750+g*23,21).split(b'\0',1)[0].decode('shift_jis')))
    assert [p['id'] for p in profiles if p['passes_incident_customer_trait']]==[81,84,94,103]
    worlds=[]
    for mapname in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
        b=payload('/DAT/'+mapname+'.BIN');town=b[17:24017];stores=[]
        for slot in range(10):
            s=b[25907+slot*5080:25907+(slot+1)*5080]
            if not s[0]:continue
            left,top,right,bottom=struct.unpack_from('<4i',s,8);found={0:[],1:[]}
            for y in range(max(0,top-7),min(49,bottom+7)+1):
                for x in range(max(0,left-7),min(59,right+7)+1):
                    tile=struct.unpack_from('<h',town,(y*60+x)*8)[0]
                    for f in facilities:
                        if f['tile_range'][0]<=tile<=f['tile_range'][1]:found[f['incident']].append(dict(x=x,y=y,tile=tile))
            flags=struct.unpack_from('<H',s,4)[0]
            stores.append(dict(physical_slot=slot,flags=flags,rival_skipped_before_any_later_gate=bool(flags&0x8000),rect=[left,top,right,bottom],
                robbery_facility_cells=found[0],fire_facility_cells=found[1],robbery_has_blocker=bool(found[0]),fire_has_blocker=bool(found[1])))
        worlds.append(dict(map=mapname,town_file_sha256=sha(b),stores=stores))
    write('incident-data.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,messages=messages,blocking_facilities=facilities,
        fixture_classes=fixtures,layouts=layouts,customer_profiles=profiles,initial_store_facility_cover=worlds,
        scope='Static source layout values/classes and initial locations. This is not a fired incident simulation or measured probability. All11 initial rival stores are rejected by the actual first owner gate.',
        label_provenance='Original MSG words decoded with prior by-eye font transcription; source building/group names are Shift-JIS. No new OCR.'))
    write('android-incident-bridge.json',dict(schema_version=1,
        gate_order=['Owner rival bit8000 must be clear.','Summary security08 must be strictly below storeC6C.',
            'Unsigned cumulative visitors1188>=2000.','Signed storeD5C>999999 and signed current revenueD98>99999.',
            'Signed32 sum of original equipment valuation8001D018 plus stock procurement valuation8001D618>99999.',
            'Consume2 RNG calls: first rand()%128==100 selects kind0; second rand()%256==100 selects kind1 and overrides kind0. If neither matches, exit.',
            'Search clipped7-cell expanded store rectangle. Kind0 exits on any police-box cell60..63; kind1 exits on any fire-station cell64..69.',
            'Minimum signed profile19 among tier-limited active customer records must be<31. Start minimum at100, so no active customer cannot pass.'],
        eligibility_note='One eligible active group is sufficient; group quantity and exact active state are not weighted. Uses same trait19 as ordinary theft, but threshold is fixed31 here.',
        robbery='Set revenueD98=0; subtract signed32(saved pre-event revenueD98<<3) from player cash0. Popup mode0 receives serial(flags&7fff) and the same scaled amount. No general fixture/customer clear in this branch.',
        fire='No direct revenue zero or player-cash debit here. Scan mutable half-cell grid row-major. For empty cell and signed logical floor0..15, draw once and write trunc(floor/5)*5+rand()%4+1. For valid fixture anchor kind<53 except categories4/6, erase its rotated footprint to0. Loop later sees cells just cleared.',
        fire_floor_note='Multiple empty half-cells can rewrite the same logical floor tile, consuming multiple RNG draws. Floor dirt here is not a new dedicated scorch asset.',
        fire_customers='Scan all20 records, not the tier-limited subset. Set active state0; if coordinates valid, clear image bits in old grid cell. Other customer bytes are not globally memset.',
        fire_popup='Mode1 gets serial(flags&7fff), amount=saved revenueD98<<3. This UI amount is not recomputed as removed equipment+inventory cost.',
        common_tail='After popup path, set current energy19=0 for each assigned employee. Do not set staff task28 to0 or unassign them. Set storeC6C=5 and dirty byte1=0. Do not confuse C6C with ratingC68.',
        subsequent_update='Parent job order is customer319AC,staff36AC0,floor31498,advice3B570,incident3BF28. Incident is at end of these jobs; do not assume earlier summary/occupancy was rebuilt immediately inside this function.',
        limits='No new real-time frequency, exact probability per day, full popup animation/audio reproduction or native Android implementation claimed. Original isolated incident/UI models already existed.'))
    write('source-derived-examples.json',dict(scope='Arithmetic and source branch examples, not new gameplay observations.',
        revenue=dict(pre_event_revenue=100000,robbery_cash_delta=-800000,robbery_revenue_after=0,fire_direct_cash_delta=0,fire_revenue_after=100000,both_popup_amount_argument=800000),
        rng_overwrite=[dict(first_remainder128=a,second_remainder256=b,kind=1 if b==100 else 0 if a==100 else -1) for a,b in [(100,0),(0,100),(100,100),(0,0)]],
        fire_fixture_totals=[{k:x[k] for k in ['id','fixture_count','retained_fixture_count','removed_fixture_count','assets_gate_value','removed_value_by_class']} for x in layouts if x['id'] in [1,16,26]],
        floor_writes=dict(initial_floor=5,first_draw_mod4=0,first_write=6,second_draw_mod4=3,second_write=9,note='Two qualifying half-cell visits to same logical tile; second replaces first.')))
    spans=[('incident',0x8003bf28,0x8003ceac),('incident_popup',0x80052270,0x80052dbc),
        ('equipment_value',0x8001d018,0x8001d1ac),('inventory_value',0x8001d618,0x8001d8ac),('parent_job_order',0x80023438,0x80023c20)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];ranges=[]
    for label,a,end in spans:
        data=at(a,end-a);(ROOT/'source'/f'{label}.bin').write_bytes(data);ranges.append(dict(name=label,address=hex(a),bytes=len(data),sha256=sha(data)))
        asm.append(f'\n# {label} {a:#x}..{end:#x}');asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(data,a))
    for label,a,n in [('facility-descriptors',0x8009da10+5*56,112),('fixture-master',0x80099f0c,53*196),('profiles',0x800a09d0,144*24),('product-master',0x8009cdf0,27*88)]:
        data=at(a,n);(ROOT/'source'/f'{label}.bin').write_bytes(data);ranges.append(dict(name=label,address=hex(a),bytes=n,sha256=sha(data)))
    write('source-ranges.json',ranges);(ROOT/'incident-readers.asm').write_text('\n'.join(asm)+'\n')
    write('source-dependencies.json',dict(layouts=dict(path='../20261114-parking-arrival-data/source/layouts.bin',sha256=sha(at(0x800a2074,3108*30))),town_cells=dict(path='../20261114-security-theft-data/source/town-cells.bin',sha256=sha(b''.join(payload('/DAT/'+n+'.BIN')[17:24017] for n in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS'])))))
    write('summary.json',dict(incident_modes=2,source_messages=3,fixture_classes=53,fire_retained_fixture_ids=[37,38,39,40,41,42,48,49],layouts=30,populated_layouts_passing_assets_gate=24,
        trait_eligible_profile_ids=[81,84,94,103],initial_location_coverage_rows=11,original_cpu_updates=0,
        known_before='Isolated incident damage and original popup paths were reconstructed earlier. This work connects labels, all53 classes/30 layouts,4 actual qualifying profiles,11 initial locations, distinct monetary effects and source common-tail offsets.',
        not_claimed='Actual incidents at initial rival stores, probability per day, a new emulated incident run, or new Android/APK changes.'))
    print(json.dumps(dict(layouts=30,assets_gate=24,retained_ids=[f['id'] for f in fixtures if f['survives_fire_class']],eligible_profiles=[p['id'] for p in profiles if p['passes_incident_customer_trait']])))

if __name__=='__main__':main()
