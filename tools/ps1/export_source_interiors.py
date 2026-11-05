"""Export source layouts without shipping the original executable or an emulator.

Usage: python tools/ps1/export_source_interiors.py restored/algorithm-analysis
The source coordinates include the exterior and walls; do not crop/rotate them.
"""
import collections
import hashlib
import json
from pathlib import Path
import struct
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
src = Path(sys.argv[1])
exe = (src / 'source/SLPS_007.82').read_bytes()
assert hashlib.sha256(exe).hexdigest() == 'd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
raw = lambda a, n: exe[a - 0x80010000 + 2048:a - 0x80010000 + 2048 + n]
base = json.loads((ROOT / 'game/data/vertical_slice.json').read_text())
recovered = json.loads((ROOT / 'game/data/ps1_recovered.json').read_text())
descriptors = recovered['fixture_records']
images = [struct.unpack('<12i', raw(0x8009ce14 + j * 88, 48)) for j in range(27)]
product_ids = ['cold_drink', 'hot_drink', 'alcohol', 'bento', 'bread', 'instant_food', 'snacks', 'books', 'tobacco', 'ice_cream', 'stationery', 'electronics', 'vegetables', 'fish', 'meat', 'retort_food', 'seasoning', 'frozen_food', 'oden', 'daily_goods', 'copy_paper', 'parcel_delivery_form', 'medicine', 'underwear', 'event_goods', 'chinese_steamed_bun']
catalog = {v: k for k, v in recovered['fixture_kind'].items() if not k.startswith('source_fixture_')}
existing = {r['catalog_id']: r for r in base['fixture_catalog']}
extra = []
labels = {19:'大型冷凍棚',20:'小型冷凍ワゴン',21:'大型冷凍ワゴン',23:'おでん器',33:'コピー機1',34:'コピー機2',35:'コピー機3',36:'コピー機4',37:'レジ1',38:'レジ2',39:'宅配便受付レジ',40:'大型レジ1',41:'大型レジ2',42:'大型宅配便受付レジ',43:'特殊商品棚1',44:'特殊商品棚2'}
for k, desc in enumerate(descriptors):
    if k not in catalog:
        cid = 'source_fixture_%d' % k
        catalog[k] = cid
        allowed = [product_ids[p] for p in desc[21:48] if 0 <= p < len(product_ids)]
        extra.append(dict(catalog_id=cid, kind='checkout' if 37 <= k <= 42 else 'shelf', footprint_tiles=desc[9:11], purchase_price_yen=desc[1], capacity=desc[3], compatible_product_categories=allowed, evidence_note='CONFIRMED_BINARY: fixture descriptor 80099F0C + index * 196.'))

layouts = []
tables = json.loads((src / 'layout-tables.json').read_text())['layouts']
for row in tables:
    idx = row['index']
    b = bytes.fromhex(row['raw_hex'])
    # Cross-check archived extraction against the actual source bytes.
    assert b == raw(0x800a2074 + idx * 3108, 3108)
    w, h = struct.unpack_from('<ii', b)
    walls, fixtures, products = set(), [], []
    floor = [[b[12 + y * 14 + x] for x in range(w // 2)] for y in range(h // 2)]
    entries = [(x*2, y*2) for y, line in enumerate(floor) for x, code in enumerate(line) if code in (28,29,30,31,32,33,34,35)]
    for y in range(h):
        for x in range(w):
            v = struct.unpack_from('<I', b, 196 + y * 112 + x * 4)[0]
            if not v & 0x80000000:
                continue
            kind = v >> 12 & 1023
            if kind == 53:
                walls.update((x+dx,y+dy) for dy in range(2) for dx in range(2))
                continue
            if kind >= 53:
                continue
            # Source directions 0/1/2/3 correspond to client rotations 0/2/3/1.
            direction = v >> 22 & 3
            rotation = [0,2,3,1][direction]
            fw, fh = descriptors[kind][9:11]
            if rotation & 1:
                fw, fh = fh, fw
            cid = catalog[kind]
            fkind = 'checkout' if 37 <= kind <= 42 else ('break_room' if kind in (48,49) else ('parking' if kind >= 50 else ('amenity' if kind in (45,46,47) else 'shelf')))
            fid = 'checkout-1' if fkind == 'checkout' else ('break-room-1' if fkind == 'break_room' else 'source-%d-%d-%d' % (kind,x,y))
            f = dict(id=fid,kind=fkind,catalog_id=cid,origin_subcell=[x,y],footprint_tiles=[fw,fh],rotation_quarter_turns=rotation,source_kind=kind,source_word=v)
            fixtures.append(f)
            stock = struct.unpack_from('<I', b, 196 + (y+1)*112 + x*4)[0] if y+1<h else 0
            image, qty = stock >> 12 & 1023, stock >> 24 & 127
            category = next((j for j, codes in enumerate(images) if any(c >= 0 and (c*3+360)//3 == image//3 for c in codes)), -1)
            # The parcel service on a register and the source's 27th special
            # category have no client shopping contract yet. Preserve raw stock.
            f['source_stock_word'] = stock
            if fkind == 'shelf' and qty and 0 <= category < len(product_ids):
                pid = product_ids[category]
                retail, cost_percent = recovered['products'][category]
                products.append(dict(id='goods-'+fid,catalog_id=pid,fixture_id=fid,initial_stock_units=qty,sale_price_yen=retail,restock_unit_cost_yen=retail*cost_percent//100))
    occupied = set(walls)
    for f in fixtures:
        x,y=f['origin_subcell'];fw,fh=f['footprint_tiles']
        cells={(xx,yy) for yy in range(y,y+fh*2) for xx in range(x,x+fw*2)}
        assert not (cells & occupied), (idx,f)
        assert all(0<=xx<w and 0<=yy<h for xx,yy in cells)
        occupied.update(cells)
    entry = next((p for p in entries if p not in occupied), None)
    assert entry is not None
    reachable={entry};queue=collections.deque([entry])
    while queue:
        x,y=queue.popleft()
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            if 0<=p[0]<w and 0<=p[1]<h and p not in occupied and p not in reachable:
                reachable.add(p);queue.append(p)
    for f in fixtures:
        x,y=f['origin_subcell'];fw,fh=f['footprint_tiles'];fw*=2;fh*=2
        # Client bridge: use a reachable adjacent cell, preferring the source
        # orientation. Source actor subcell dispatch is not yet fully ported.
        sides=[[(xx,y+fh) for xx in range(x,x+fw)],[(xx,y-1) for xx in range(x,x+fw)],[(x-1,yy) for yy in range(y,y+fh)],[(x+fw,yy) for yy in range(y,y+fh)]]
        preferred=(f['source_word']>>22)&3
        candidates=sides[preferred]+sum(sides,[])
        front=next((p for p in candidates if p in reachable),None)
        if front is None and f['kind'] in ('parking','amenity'):
            front=entry
        assert front is not None,(idx,f['id'])
        f['interaction_subcell']=list(front)
    checkout=next((f['id'] for f in fixtures if f['kind']=='checkout'),'')
    positions=sorted(reachable,key=lambda p:(abs(p[0]-entry[0])+abs(p[1]-entry[1]),p))
    layouts.append(dict(source_index=idx,source_sha256=hashlib.sha256(b).hexdigest(),store=dict(width_tiles=w//2,height_tiles=h//2,subcells_per_tile=2,entry_subcell=list(entry),exit_subcell=list(positions[1]),size_tier=['small','medium','large'][idx//10],source_layout_index=idx,source_floor=floor,blocked_subcells=[list(p) for p in sorted(walls)]),fixtures=fixtures,products=products,checkout_fixture_id=checkout,staff_start_subcells={m['id']:list(positions[j+2]) for j,m in enumerate(base['staff']['members'])},sample_layout_label='原作サンプル%d'%(idx%5),max_concurrent_customers=[10,15,20][idx//10],provisional_restock_product_id=products[0]['id'] if products else '',source_equipment_yen=sum(descriptors[f['source_kind']][1] for f in fixtures),source_goods_yen=sum(p['initial_stock_units']*p['restock_unit_cost_yen'] for p in products)))

out=dict(layouts=layouts,extra_fixture_catalog=extra,fixture_kind={v:k for k,v in catalog.items()},labels=labels,evidence_note='CONFIRMED_BINARY: 30 layouts at 800A2074, stride 3108; rival_helpers.load_layout, interior_floor_display.floor_records. REMAKE_BALANCED_DEFAULT: reachable interaction-side fallback and staff spawn cells; register parcel stock and category 26 preserved as raw fields but not sold.')
(ROOT/'game/data/ps1_interiors.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
recovered['fixture_kind'].update(out['fixture_kind'])
(ROOT/'game/data/ps1_recovered.json').write_text(json.dumps(recovered,ensure_ascii=False,separators=(',',':'))+'\n')
texture=Image.open(ROOT/'assets/raw/ps1_disc_analysis_v1/images/TIM0_SYOP_S00.png')
texture.crop((0,0,256,48)).save(ROOT/'game/assets/ps1/floor_atlas.png')
print('Exported',len(layouts),'source layouts and',len(extra),'missing fixture definitions')
