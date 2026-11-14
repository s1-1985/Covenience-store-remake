#!/usr/bin/env python3
"""Recover source land/building charges; no PS CPU or gameplay execution."""
import argparse, collections, hashlib, json, runpy, struct
from pathlib import Path
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN

ROOT = Path(__file__).resolve().parent
DISC_SHA = '8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA = 'd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
MAPS = ['TOWN0001', 'TOWN0002', 'TOWN0003', 'TOWNPS']

def sha(b): return hashlib.sha256(b).hexdigest()
def write(name, value): (ROOT/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n')
def i32(v): return (v+2**31) % 2**32-2**31
def trunc(v, d): return (-1 if v < 0 else 1)*(abs(v)//d)

def quote(town, descriptors, x, y):
    """The original 1DFD0/1E1A8 readers, restricted to in-map 2x2 sites."""
    land = 0; demolition = 0; marked = set(); buildings = []
    selected = {(xx, yy) for yy in (y, y+1) for xx in (x, x+1)}
    def tile(xx, yy): return struct.unpack_from('<h', town, (yy*60+xx)*8)[0]
    for yy in (y, y+1):
        for xx in (x, x+1):
            land = i32(land + struct.unpack_from('<b', town, (yy*60+xx)*8+2)[0]*1000000)
            if (xx, yy) in marked: continue
            image = tile(xx, yy)
            # Native 20238 compares index < 0x48, NOT all 82 stored rows.
            d = next((r for r in descriptors[:72] if r['tile_lower'] <= image <= r['tile_upper']), descriptors[0])
            delta = image-d['tile_lower']; width = d['width']; height = d['height']
            left = xx-(delta-trunc(delta, width)*width)
            assert 0 <= left < 60
            # Original reloads tile at corrected x, then derives corrected y.
            top = yy-trunc(tile(left, yy)-d['tile_lower'], width)
            footprint = {(bx, by) for by in range(top, top+height) for bx in range(left, left+width)}
            assert all(0 <= bx < 60 and 0 <= by < 50 for bx, by in footprint)
            marked.update(footprint)
            amount = i32(width*height*d['demolition_coefficient']*1000000)
            demolition = i32(demolition+amount)
            buildings.append(dict(descriptor=d['id'], name=d['name'], first_selected_cell=[xx, yy],
                first_tile=image, origin=[left, top], footprint=[width, height],
                selected_cells=len(selected & footprint), full_charge=amount,
                extends_outside_selection=not footprint <= selected))
    return dict(x=x, y=y, land=land, demolition_full=demolition,
                demolition_player=trunc(demolition, 2), acquisition=i32(land+trunc(demolition, 2)), buildings=buildings)

def placement_trace(town, descriptors, x, y):
    """Deterministic cell outputs for descriptor0/mode0 before final mask rebuild.

    The source still consumes RNG for customer mix; all five choices are -1 for
    both replacement row12 and store row0, so these outputs do not need a seed.
    """
    out=bytearray(town); draws=0; demolished=[]
    def tile(xx,yy): return struct.unpack_from('<h',out,(yy*60+xx)*8)[0]
    def set_cell(xx,yy,image,d):
        nonlocal draws
        off=(yy*60+xx)*8
        struct.pack_into('<h',out,off,image)
        struct.pack_into('<bb',out,off+3,d['demolition_coefficient'],d['category'])
        out[off+5]=(out[off+5]|24) if d['category']>0 else (out[off+5]&~24)
        assert d['customer_mix_choices']==[-1]*5
        struct.pack_into('<h',out,off+6,-1); draws+=1
    image=descriptors[0]['tile_lower']
    for yy in (y,y+1):
        for xx in (x,x+1):
            if struct.unpack_from('<b',out,(yy*60+xx)*8+4)[0]>0:
                v=tile(xx,yy); d=next((d for d in descriptors[:72] if d['tile_lower']<=v<=d['tile_upper']),descriptors[0])
                delta=v-d['tile_lower']; left=xx-(delta-trunc(delta,d['width'])*d['width'])
                top=yy-trunc(tile(left,yy)-d['tile_lower'],d['width'])
                demolished.append(dict(descriptor=d['id'],origin=[left,top],footprint=[d['width'],d['height']]))
                for by in range(top,top+d['height']):
                    for bx in range(left,left+d['width']):set_cell(bx,by,43,descriptors[12])
            set_cell(xx,yy,image,descriptors[0]); image+=1
    changes=[]
    for k in range(3000):
        before=town[k*8:k*8+8]; after=out[k*8:k*8+8]
        if before!=after:changes.append(dict(x=k%60,y=k//60,before_hex=before.hex(),after_hex=after.hex(),
            outside_selected_rectangle=not(x<=k%60<=x+1 and y<=k//60<=y+1)))
    assert out[2::8]==town[2::8]
    return dict(store_descriptor=0,mode=0,origin=[x,y],demolished=demolished,changed_cells=changes,
        changed_outside_selected_rectangle=sum(c['outside_selected_rectangle'] for c in changes),
        original_rng_draws_with_constant_mix_result=draws,
        scope='Cell outputs derived from native1F1C0 and1F4B4 using stored initial masks, before1BAAC final1F8BC rebuild. Not a gameplay run or whole-map post-rebuild snapshot.')

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('disc', type=Path); args=ap.parse_args()
    disc=args.disc.read_bytes(); assert sha(disc)==DISC_SHA
    iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso']
    rows, read=iso(disc); files={r['path']:r for r in rows}
    def payload(path): r=files[path]; return read(r['lba'], r['bytes'])
    exe=payload('/SLPS_007.82'); assert sha(exe)==EXE_SHA
    def at(a,n): return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    (ROOT/'source').mkdir(exist_ok=True)
    descriptors=[]
    for j in range(82):
        b=at(0x8009d738+56*j,56); w,h,lo,hi=struct.unpack_from('<4i', b,24)
        category,coef=struct.unpack_from('<bb',b,40)
        descriptors.append(dict(id=j, name=b[:24].split(b'\0',1)[0].decode('shift_jis'),
            address=hex(0x8009d738+56*j), width=w,height=h,tile_lower=lo,tile_upper=hi,
            category=category,demolition_coefficient=coef,full_demolition_charge=i32(w*h*coef*1000000),
            player_half_charge=trunc(i32(w*h*coef*1000000),2),lookup_20238_scans_row=j<72,
            customer_mix_choices=list(struct.unpack_from('<5h',b,42))))
    (ROOT/'source/building-descriptors.bin').write_bytes(at(0x8009d738,82*56))
    write('building-demolition-master.json',dict(table_address='0x8009d738',stride=56,stored_rows=82,
        lookup_rows=72,reader='0x80020238',fallback_row=0,rows=descriptors))
    tiers=[]
    for tier in range(6):
        layouts=[]
        for variant in range(5):
            j=tier*5+variant; b=at(0x800a2074+3108*j,3108); w,h=struct.unpack_from('<2i',b)
            layouts.append(dict(id=j,variant=variant,half_cell_grid=[w,h],logical_grid=[w//2,h//2],sha256=sha(b)))
        tiers.append(dict(tier=tier,source_store_offset='0xc70',construction_fee=(tier//2+1)*6000000,
            mode0_building_component=(tier//2+1)*3000000,layouts=layouts))
    write('construction-tiers.json',dict(reader='0x8001de5c',tier_count=6,tiers=tiers,
        mode0_note='Mode0 adds equipment_total(1D018) and procurement_inventory_total(1D618) to this building component; it is not the construction purchase fee.',
        mode1_note='Mode1 returns construction fee only. Original land footprint stays 2x2 for all six internal store tiers.',
        availability='6E998 reads signed CD994: <3 exposes2 tiers; otherwise <5 exposes4; otherwise6. This is the source selector condition, not a decoded meaning of CD994.'))
    permit=json.loads((ROOT.parent/'20261114-permit-siting-data/permit-siting-data.json').read_text())
    maskbytes=(ROOT.parent/'20261114-permit-siting-data/source/candidate-mask-bytes.bin').read_bytes()
    worlds=[]; examples=[]; placement_examples=[]; binary=bytearray()
    for map_id,name in enumerate(MAPS):
        b=payload('/DAT/'+name+'.BIN'); town=b[17:24017]
        assert len(town)==24000
        prior=permit['worlds'][map_id]; assert prior['map']==name and prior['source_town_sha256']==sha(b)
        masks=maskbytes[prior['candidate_rebuilt_offset']:prior['candidate_rebuilt_offset']+2891]
        land_hist=collections.Counter(struct.unpack_from('<b',town,k*8+2)[0] for k in range(3000))
        all_quotes=[]; valid=[]; touched=collections.Counter(); partial_count=0; offset=len(binary)
        for y in range(49):
            for x in range(59):
                q=quote(town,descriptors,x,y); mask=masks[y*59+x]; allowed=not mask&8
                binary.extend(struct.pack('<4i',q['land'],q['demolition_full'],q['demolition_player'],q['acquisition']))
                q.update(base_siting_allowed=allowed,rebuilt_candidate_mask=mask); all_quotes.append(q)
                if not allowed: continue
                valid.append(q)
                partial_count+=any(r['extends_outside_selection'] and r['full_charge'] for r in q['buildings'])
                touched.update(r['descriptor'] for r in q['buildings'])
        assert len(valid)==prior['base_siting_allowed']
        low=min(valid,key=lambda q:q['acquisition']); high=max(valid,key=lambda q:q['acquisition'])
        histogram=collections.Counter(q['acquisition'] for q in valid)
        # One concrete partial-building trace per source map, with original cells.
        partial=next(q for q in valid if any(r['extends_outside_selection'] and r['full_charge'] for r in q['buildings']))
        chosen=[]
        for label,q in [('minimum',low),('maximum',high),('partial_building',partial)]:
            cells=[dict(x=x,y=y,tile=struct.unpack_from('<h',town,(y*60+x)*8)[0],
                land_coefficient=struct.unpack_from('<b',town,(y*60+x)*8+2)[0])
                for y in (q['y'],q['y']+1) for x in (q['x'],q['x']+1)]
            chosen.append(dict(label=label,quote=q,source_cells=cells))
        examples.append(dict(map=name,examples=chosen))
        placement_examples.append(dict(map=name,examples=[dict(label=e['label'],trace=placement_trace(town,descriptors,e['quote']['x'],e['quote']['y'])) for e in chosen]))
        worlds.append(dict(map=name,source_sha256=sha(b),land_coefficient_histogram=dict(sorted(land_hist.items())),
            candidate_count=len(all_quotes),base_siting_allowed=len(valid),cost_binary_offset=offset,
            valid_acquisition_histogram=dict(sorted(histogram.items())),minimum_acquisition=low['acquisition'],maximum_acquisition=high['acquisition'],
            minimum_origin=[low['x'],low['y']],maximum_origin=[high['x'],high['y']],
            minimum_acquisition_positions=histogram[low['acquisition']],
            valid_sites_touching_part_of_chargeable_building=partial_count,
            building_ids_seen_on_valid_sites=dict(sorted(touched.items())),
            initial_company_cash=list(struct.unpack_from('<2i',b,1)),
            land_plus_building_ranges=[dict(tier=t['tier'],minimum=low['acquisition']+t['construction_fee'],
                maximum=high['acquisition']+t['construction_fee']) for t in tiers]))
    assert all(w['land_coefficient_histogram']=={5:3000} for w in worlds)
    (ROOT/'candidate-costs.i32le').write_bytes(binary)
    write('initial-map-site-costs.json',dict(source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,worlds=worlds,
        binary=dict(path='candidate-costs.i32le',bytes=len(binary),record_format='<4i',fields=['land','full_demolition','player_half_demolition','acquisition'],
            map_order=MAPS,origins_grid=[59,49],order='For each map, y=0..48 outer, x=0..58 inner; four signed little-endian i32 per position.',
            restrictions='../20261114-permit-siting-data/source/candidate-mask-bytes.bin; offsets in sibling permit-siting-data.json'),
        scope='Loaded original town cells and rebuilt original initial masks; all positions exported, summaries exclude bit8-blocked sites. No future town growth/repricing, permit fees, equipment, stock or editor changes are included. Ranges with construction are additive source arithmetic, not complete furnished-store quotes.'))
    write('source-derived-examples.json',examples)
    write('source-derived-placement-patches.json',placement_examples)
    write('android-land-construction-bridge.json',dict(schema_version=1,
        land='For inclusive valid-map rectangle, sum signed town byte2 *1000000 per cell. All-zero rectangle is sentinel. Source files all start at coefficient5; do not hardcode later land values to5.',
        demolition='Scan selected cells row-major, skip footprint-marked cells. Lookup native descriptor rows0..71 by signed tile range; fallback0. Charge full width*height*signed byte41*1000000 once per touched building. Derive left by signed remainder(tile-lower,width); reload tile at(left,currentY) before deriving top by signed quotient. Mark full footprint, even outside selection.',
        acquisition='Player land UI computes trunc(full_demolition/2) then adds full land price. Do not divide each footprint or cell charge first, do not charge only overlap area, and do not count one footprint multiple times.',
        invalid='1E8CC with descriptor0 checks2x2 bounds and bit8. Invalid land preview sets CD840=-1 but leaves previous CD7E4 unchanged; validity must guard purchase. This stale display state is not a legitimate new quote.',
        stage_gates='Land stage accepts acquisition < signed cash; equality fails. Permit stage accepts fee <= cash, and construction stage accepts size fee <= cash. Preserve distinct comparisons and stage order land -> permits -> size -> interior.',
        size='Use six tiers and 30 layouts: built-in layout index=tier*5+variant. Land footprint remains2x2, regardless of internal half-cell dimensions. Fee=(trunc(tier/2)+1)*6000000.',
        valuation='Mode0 of1DE5C uses3000000 per tier pair plus equipment and procurement stock. Do not substitute this mode0 value for purchase construction fee.',
        placement='1BAAC marks store active, calls1F1C0 at store left/top then1F8BC rebuilds masks.1F1C0 walks new footprint row-major, calls1F4B4 on positive-category cells before overwriting.1F4B4 resolves full old footprint, mode0 replaces it with row12 tile43, attribute0, category0, clears bits0x18, sets mix from5 choices(all -1). Both clear/place preserve land byte2. Each cleared or placed cell still consumes one mix RNG draw; mode1 demolition consumes an additional draw per cell to choose empty row9..13. New placement fills tiles sequentially and writes descriptor attribute/category, sets bits0x18 for positive category and chooses mix. Final mask rebuild is mandatory; interim bit8 must not be treated as final permission overlay.',
        posting='New-game5DBB8 snapshots cash and ledger before6DD18, then5DBEC..5DC6C restores and posts the four land/demolition/size/permit amounts via1CBC4. Cancelled interior posts matching negatives at5DD60..5DDD8. Avoid duplicate provisional plus final charge.',
        source_only='Extracted rules/data for a native implementation; no emulator, BIOS or original executable runtime required. Native Android code/APK is not changed by this extraction.'))
    ranges=[]; asm=[]; md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    for label,a,end in [('premises_value',0x8001de5c,0x8001dfd0),('land_value',0x8001dfd0,0x8001e1a8),
        ('demolition_value',0x8001e1a8,0x8001e660),('building_lookup',0x80020238,0x80020364),
        ('layout_loader',0x8001b678,0x8001b8c4),
        ('store_activate',0x8001baac,0x8001bb80),('place_and_clear',0x8001f1c0,0x8001f8bc),
        ('land_ui',0x8006df94,0x8006e3cc),('size_ui',0x8006e984,0x8006eb34),('newgame_posting',0x8005dbb8,0x8005dde0)]:
        data=at(a,end-a); (ROOT/'source'/f'{label}.bin').write_bytes(data)
        ranges.append(dict(label=label,address=hex(a),bytes=len(data),sha256=sha(data)))
        asm.append(f'\n# {label} {a:#x}..{end:#x}')
        asm.extend(f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(data,a))
    (ROOT/'cost-readers.asm').write_text('\n'.join(asm)+'\n'); write('source-ranges.json',ranges)
    write('source-dependencies.json',dict(town_cells='../20261114-security-theft-data/source/town-cells.bin',
        raw_layouts='../20261114-parking-arrival-data/source/layouts.bin',
        candidate_masks='../20261114-permit-siting-data/source/candidate-mask-bytes.bin',
        note='Existing evidence reused without duplicating whole town or EXE files. This extractor rereads source disc.'))
    write('summary.json',dict(stored_building_descriptors=82,demolition_lookup_rows=72,construction_tiers=6,layouts=30,
        initial_land_coefficients={w['map']:w['land_coefficient_histogram'] for w in worlds},candidate_rectangles=11564,
        valid_sites={w['map']:w['base_siting_allowed'] for w in worlds},
        acquisition_ranges={w['map']:[w['minimum_acquisition'],w['maximum_acquisition']] for w in worlds},
        partial_building_site_counts={w['map']:w['valid_sites_touching_part_of_chargeable_building'] for w in worlds},
        original_cpu_updates=0,
        known_before='Isolated land, demolition, valuation and premises controls already recovered. New work connects all native descriptors, actual72-row lookup, all12000 initial cell coefficients,11564 positions and30 layouts to original stage-specific charges.',
        placement_examples=sum(len(m['examples']) for m in placement_examples),
        limitations='Static initial-map arithmetic and source-derived12 placement patches before mask rebuild, not future town values or a complete editor/furnished-store expenditure audit; native APK not rebuilt.'))
    print((ROOT/'summary.json').read_text())

if __name__=='__main__': main()
