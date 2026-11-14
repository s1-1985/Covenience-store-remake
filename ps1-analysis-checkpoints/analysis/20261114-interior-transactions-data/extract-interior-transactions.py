#!/usr/bin/env python3
"""Source-only fixture/product costs, original layouts and stock-change matrices."""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def i32(v):return (v+2**31)%2**32-2**31
def trunc(v,d):return (-1 if v<0 else 1)*(abs(v)//d)
def write(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    disc=args.disc.read_bytes();assert sha(disc)==DISC_SHA
    iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso']
    rows,read=iso(disc);files={r['path']:r for r in rows}
    def payload(path):r=files[path];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    msg=payload(next(k for k in files if k.endswith('/MSG00.OBJ')))
    def message(i):
        off=struct.unpack_from('<I',msg,i*4)[0];codes=[]
        for j in range(256):
            v=struct.unpack_from('<H',msg,off+j*2)[0];codes.append(v)
            if v==0x40ff:return dict(index=i,offset=off,codes=codes,text=decode(codes))
        raise AssertionError('missing message terminator')
    products=[]
    for i in range(27):
        b=at(0x8009cdf0+i*88,88);base,percent=struct.unpack_from('<2i',b,24);images=[]
        for im in struct.unpack_from('<12i',b,36):
            if im==-1:break
            images.append(im*3+360)
        products.append(dict(id=i,name=b[:24].split(b'\0',1)[0].decode('shift_jis'),base_price=base,
            cost_percent=percent,procurement_unit=trunc(i32(base*percent),100),runtime_images=images))
    def byimage(im):return next((p for p in products if any(v//3==im//3 for v in p['runtime_images'])),products[0])
    fixtures=[];catalog=[];matrices=[];n_changes=0
    for i in range(53):
        b=at(0x80099f0c+i*196,196);w=struct.unpack('<49i',b);opts=[]
        for v in w[21:48]:
            if v==-1:break
            opts.append(v)
        f=dict(id=i,label=message(387+i),category=w[0]&255,flags=w[0],purchase_price=w[1],capacity=w[3],
            logical_footprint=list(w[9:11]),compatible_products=opts,source_default_index=w[48],
            regular_removal_allowed=(w[0]&255) not in (4,6),
            ordinary_product_change=i<22 or 29<=i<33)
        assert not opts or 0<=w[48]<len(opts)
        default=opts[w[48]] if opts else None
        f['source_default_product']=default;fixtures.append(f)
        quotes=[dict(product=p,product_name=products[p]['name'],stock_quantity=w[3],
            stock_cost=i32(products[p]['procurement_unit']*w[3]),
            total_purchase=i32(w[1]+products[p]['procurement_unit']*w[3]),
            ordinary_removal_refund=i32(w[1]+products[p]['procurement_unit']*w[3]) if f['regular_removal_allowed'] else None) for p in opts]
        catalog.append(dict(fixture=i,empty_purchase=w[1],full_stock_options=quotes,
            default_purchase=w[1]+(0 if default is None else products[default]['procurement_unit']*w[3])))
        if not f['ordinary_product_change']:continue
        quantities=sorted(set([0,w[3]//2,w[3]]));charges=[]
        for qty in quantities:
            matrix=[[i32(products[new]['procurement_unit']*w[3]-products[old]['procurement_unit']*qty) for new in opts] for old in opts]
            n_changes+=len(opts)**2;charges.append(dict(old_quantity=qty,delta=matrix))
        matrices.append(dict(fixture=i,products=opts,capacity=w[3],old_product_rows_new_product_columns=True,charges=charges))
    write('fixture-transaction-master.json',dict(source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,
        fixture_rows=fixtures,product_rows=products,unit_note='Amounts are original signed cash arithmetic units. Fixture source word1 enters cash directly in76474/773BC/1D018, without guessed scaling.'))
    write('catalog-purchase-quotes.json',catalog)
    write('product-change-matrices.json',dict(reader='209F8 amount10000, used by68978',
        formula='new_unit*capacity - old_unit*old_quantity; unit=trunc(i32(base*cost_percent)/100)',
        quantity_profiles='0, floor(capacity/2), capacity; all source-compatible old/new product pairs for the26 fixtures routed to ordinary product selection.',
        negative_means='Net credit to cash and reduction in stock cost counter; this is not sales revenue.',fixtures=matrices))
    permits=json.loads((ROOT.parent/'20261114-permit-siting-data/permit-siting-data.json').read_text())
    layouts=[];all_anchors=0;partial_stock_anchors=0
    for j in range(30):
        b=at(0x800a2074+j*3108,3108);width,height=struct.unpack_from('<2i',b);anchors=[]
        for y in range(height):
            for x in range(width):
                top=struct.unpack_from('<I',b,196+y*112+x*4)[0];kind=top>>12&1023
                if not top&0x80000000 or kind>=53:continue
                f=fixtures[kind];stock=struct.unpack_from('<I',b,196+(y+1)*112+x*4)[0]
                image=stock>>12&1023;qty=stock>>24&127;p=byimage(image) if image else None
                value=0 if p is None else i32(p['procurement_unit']*qty)
                if p is not None and qty<f['capacity']:partial_stock_anchors+=1
                anchors.append(dict(x=x,y=y,fixture=kind,direction=top>>22&3,stock_image=image,
                    stock_product=None if p is None else p['id'],stock_quantity=qty,equipment_value=f['purchase_price'],stock_value=value,
                    refill_to_capacity_cost=0 if p is None else i32(p['procurement_unit']*(f['capacity']-qty)),
                    after_refill_stock_value=0 if p is None else i32(p['procurement_unit']*f['capacity']),
                    ordinary_removal_allowed=f['regular_removal_allowed'],
                    ordinary_removal_refund=f['purchase_price']+value if f['regular_removal_allowed'] else None))
        equipment=sum(q['equipment_value'] for q in anchors);stock=sum(q['stock_value'] for q in anchors)
        regular=[q for q in anchors if q['ordinary_removal_allowed']];protected=[q for q in anchors if not q['ordinary_removal_allowed']]
        layouts.append(dict(id=j,tier=j//5,variant=j%5,sha256=sha(b),half_cell_grid=[width,height],anchor_count=len(anchors),
            equipment_cost=equipment,stock_cost=stock,interior_total=equipment+stock,
            after_refill_stock_cost=sum(q['after_refill_stock_value'] for q in anchors),
            all_regular_removal_refund=sum(q['ordinary_removal_refund'] for q in regular),
            protected_equipment_value=sum(q['equipment_value'] for q in protected),
            protected_stock_value=sum(q['stock_value'] for q in protected),
            required_permit_mask=permits['layouts'][j]['required_permit_mask'],anchors=anchors))
        all_anchors+=len(anchors)
    write('layout-interior-costs.json',dict(layouts=layouts,
        scope='All30 raw built-in templates valued by native anchor/stock rules. New-game prefab choice1 loads only tier*5+1; this file does not claim all30 templates are selectable through that choice. Saved-layout choice3 is loaded then1D1AC refills its existing products to capacity before valuation.'))
    # Six actually selected built-in prefabs; connect previously extracted land,
    # construction and permit rules without inventing an alternative layout path.
    land=json.loads((ROOT.parent/'20261114-land-construction-cost-data/initial-map-site-costs.json').read_text())
    openings=[]
    for tier in range(6):
        layout=layouts[tier*5+1];fee=(tier//2+1)*6000000
        required=layout['required_permit_mask'];permit_fee=sum(q['fee'] for q in permits['permits'] if required&q['selection_bit'])
        openings.append(dict(tier=tier,built_in_prefab_layout=layout['id'],required_permit_mask=required,required_permit_fee=permit_fee,
            construction_fee=fee,equipment=layout['equipment_cost'],stock=layout['stock_cost'],interior=layout['interior_total'],
            cheapest_initial_acquisition=20000000,minimum_opening_amount_without_editor_changes=20000000+fee+permit_fee+layout['interior_total'],
            additional_cash_needed_for_strict_interior_gate=1,
            map_price_ranges_before_permit_siting_filter=[dict(map=w['map'],minimum=w['minimum_acquisition']+fee+permit_fee+layout['interior_total'],
                maximum=w['maximum_acquisition']+fee+permit_fee+layout['interior_total']) for w in land['worlds']]))
    write('built-in-prefab-opening-costs.json',dict(rows=openings,
        note='Source arithmetic at original template values, minimum required permits only, unchanged prefab, no later manual edits. Strict acquisition/interior cash gates mean a bare exact total is insufficient at interior confirmation. Requested additional optional permits add their own fees. Size unlock and final operational/layout preflight still apply. Ranges are before extra permit availability filtering.'))
    bridge=dict(schema_version=1,
        counters='CD978 equipment cost and CD8E0 procurement stock cost are editor deltas/working totals; cashCD9F8 is provisional inside caller backup/restore flow.',
        purchase='76474 checks store bounds, low10 occupancy, floor16 flag0x200 versus other floor0x100 at origin; copies footprint, calls209F8(amount0, requested-1), then unless CD924==1 adds descriptor+4 to equipment/cash debit and preview first stock row unit*quantity to stock/cash debit. No local cash comparison in this leaf. Do not infer a global permission to finish with negative cash from this alone.',
        removal='773BC CD924==3 rejects low-byte descriptor categories4 and6. Otherwise copies whole oriented footprint to buffer8014BDA0 and clears it; equipment counter minus full original price, cash plus same; nonzero stock image returns trunc(base*factor/100)*quantity at procurement value. No age/depreciation or sale-price setting used here.',
        move='Normal parent75514 menu selection1 sets CD924=1 and enters77DE4.773BC copies/clears and generates preview with sourceCD9D0=2, with no pickup money change;76474 skips money changes specifically for CD924==1. Thus normal move pickup/place does not purchase again.77DE4 cancel restores copied cells then209F8 amount0. A synthetic CD924==4 leaf pickup is not normal move: parent selection4 enters finish preflight, not77DE4.',
        protected_replacement='CD924==2: fixtures0..21 or29..32 route to68978 product choice; other category6 returns2 and category4 returns3 after clearing/refunding equipment only. Parent75514 maps these returns to states4/5 for replacement. This path bypasses ordinary-removal rejection for required facilities.',
        product_change='68978 existing-anchor confirmation calls209F8 amount10000 and applies returned net cost to stock counter/cash. Old stock refunded at procurement, new product fills source fixture capacity even if same product is selected. No local cash gate in this path. Permission checks for tobacco8/alcohol2/drug22 precede commit. Selected index saved to mutable descriptor+192, so source default0 is initial state only.',
        prebuilt='75514 state1 resets to blank tier layout then built-in selection1 loads layout tier*5+1. Saved selection3 loads custom tier template, calls1D1AC to top up all valid anchors to capacity, then uses1D018+1D618 for cost. The sum must be strictly less than available cash; equality fails.',
        caller='New-game caller5DD04 backs up cash/ledger, runs75514 and restores, then posts CD8E0 with1CA7C and CD978 with1CBC4 on success. Avoid applying both provisional and final debits. Existing-store wrappers can use different posting paths; do not apply new-game full-total accounting blindly to every editor call.',
        units='Keep original arithmetic units; no inferred realism multiplier on fixture price. 32-bit signed wrapping precedes truncation for original multiplies.',
        scope='Source-data extraction, not native Android code or APK update.')
    write('android-interior-transactions-bridge.json',bridge)
    spans=[('equipment_value',0x8001d018,0x8001d1ac),('template_refill',0x8001d1ac,0x8001d348),
        ('stock_value',0x8001d618,0x8001d8ac),('product_image_lookup',0x800206ac,0x800209f8),
        ('stock_change',0x800209f8,0x80021ad0),('product_selection',0x80068978,0x80069438),
        ('prefab_charge',0x800759dc,0x80075d40),('placement_charge',0x80076474,0x80076b68),
        ('normal_menu_dispatch',0x80076164,0x800762c4),
        ('existing_select',0x800773bc,0x80077de4),('pickup_cancel',0x800782a4,0x800784d8),
        ('newgame_interior_post',0x8005dd04,0x8005de1c)]
    (ROOT/'source').mkdir(exist_ok=True);ranges=[];assembly=[];md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
    for name,a,end in spans:
        b=at(a,end-a);(ROOT/'source'/f'{name}.bin').write_bytes(b);ranges.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)))
        assembly.append(f'\n# {name} {a:#x}..{end:#x}');assembly.extend(f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b,a))
    (ROOT/'transaction-readers.asm').write_text('\n'.join(assembly)+'\n');write('source-ranges.json',ranges)
    write('source-dependencies.json',dict(fixture_master='../20261114-robbery-fire-data/source/fixture-master.bin',
        product_master='../20261114-robbery-fire-data/source/product-master.bin',raw_layouts='../20261114-parking-arrival-data/source/layouts.bin',
        source_note='This extractor rereads verified disc; existing raw master/layout evidence reused, no new full EXE or RAM dumps.'))
    write('summary.json',dict(fixtures=53,products=27,layouts=30,source_anchors=all_anchors,
        source_anchors_below_capacity=partial_stock_anchors,ordinary_product_change_fixtures=len(matrices),product_change_charge_entries=n_changes,
        ordinary_removal_blocked_fixture_ids=[f['id'] for f in fixtures if not f['regular_removal_allowed']],
        built_in_prefab_quotes=[dict(tier=q['tier'],layout=q['built_in_prefab_layout'],interior=q['interior'],minimum_opening_amount=q['minimum_opening_amount_without_editor_changes']) for q in openings],
        original_cpu_updates=0,known_before='Isolated placement/removal/product-change and template-cost paths already recovered. This extraction binds53 actual descriptors,27 products,30 original templates and source-compatible change matrices to working counters, required-facility exceptions and six actual prefab selections.',
        limits='No claim of all editor paths complete; existing-store final posting and later negative-cash handling remain to connect. No Android build this work.'))
    print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
