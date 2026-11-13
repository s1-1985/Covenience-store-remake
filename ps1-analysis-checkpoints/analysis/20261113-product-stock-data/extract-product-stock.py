#!/usr/bin/env python3
"""Extract PS1 product/fixture stock data directly from the original disc.
Static parsing and instruction disassembly only; no CPU emulation.
Requires the sibling 20261113-disc-data-extraction extractor, Pillow, capstone.
"""
import argparse, csv, hashlib, json, runpy, struct
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from capstone import Cs, CS_ARCH_MIPS, CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN
ROOT = Path(__file__).resolve().parent
DISC_SHA = '8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA = 'd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b): return hashlib.sha256(b).hexdigest()
def js(name, data):
    (ROOT/name).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n')
def select_images(product, fixture, direction, month):
    """Image bases at refill/replacement, one entry per logical fixture tile."""
    w,h = fixture['size']; p = product['id']; row = product['runtime_image_bases']
    if direction >= 2: w,h = h,w
    out = []
    for y in range(h):
        for x in range(w):
            if p == 20:
                slot = (2 if x==w-1 else 3) if fixture['id']==36 and direction<2 else (1 if y==h-1 else 3) if fixture['id']==36 else 0
            elif p == 21:
                edge = [x==0,x==w-1,y==h-1,y==0][direction]
                slot = direction if edge else 4
            elif p == 26: slot = direction
            elif p == 24: slot = month-1
            else: slot = (month-1+y*w+x) % product['prefix_image_count']
            assert row[slot] >= 0
            out.append(row[slot])
    return [w,h],out
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('disc',type=Path); args=ap.parse_args()
    raw=args.disc.read_bytes(); assert sha(raw)==DISC_SHA
    prior=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))
    rows,read=prior['iso'](raw); files={r['path']:r for r in rows}
    def payload(name):
        r=files[name]; return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82'); assert sha(exe)==EXE_SHA
    def at(a,n): return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    ranges=[]; (ROOT/'source').mkdir(exist_ok=True)
    for name,a,n in [('product-master',0x8009cdf0,27*88),('fixture-master',0x80099f0c,53*196),('shopping-profiles',0x800a09d0,144*24)]:
        b=at(a,n); (ROOT/'source'/f'{name}.bin').write_bytes(b)
        ranges.append(dict(name=name,address=hex(a),bytes=n,sha256=sha(b)))
    products=[]
    for p in range(27):
        a=0x8009cdf0+p*88; b=at(a,88); price,cost,setting=struct.unpack_from('<3i',b,24)
        images=list(struct.unpack_from('<12i',b,36)); n=next((j for j,v in enumerate(images) if v==-1),12)
        products.append(dict(id=p,address=hex(a),name=b[:24].split(b'\0')[0].decode('shift_jis'),base_price=price,cost_percent=cost,initial_price_setting=setting,disc_image_ids=images,runtime_image_bases=[v*3+360 if v>=0 else v for v in images],prefix_image_count=n,season_code=struct.unpack_from('<i',b,84)[0],allowed_fixture_ids=[]))
    labels={r['id']:r['name'] for r in json.loads((ROOT/'fixture-labels.json').read_text())['labels']}
    fixtures=[]
    for f in range(53):
        a=0x80099f0c+f*196; words=list(struct.unpack('<49i',at(a,196))); allowed=words[21:48]; n=next((j for j,v in enumerate(allowed) if v==-1),len(allowed)); allowed=allowed[:n]
        assert all(0<=p<27 for p in allowed)
        item=dict(id=f,name=labels[f],address=hex(a),raw_words=words,flags=words[0],purchase_price=words[1],stock_capacity=words[3],size=words[9:11],icon_code=words[20],allowed_product_ids=allowed)
        fixtures.append(item)
        for p in allowed: products[p]['allowed_fixture_ids'].append(f)
    assert products[26]['name']=='現金' and products[26]['allowed_fixture_ids']==[43,44]
    assert all(p['cost_percent']+p['initial_price_setting']==100 for p in products)
    refs=[]
    for p in range(144):
        for slot,v in enumerate(struct.unpack('<4b',at(0x800a09d0+p*24+8,4))):
            if v==26: refs.append(dict(profile=p,slot=slot))
    assert not refs
    js('product-fixture-data.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,source_ranges=ranges,product_stride=88,product_schema={'0':'shift_jis[24] name','24':'i32 base_price','28':'i32 cost_percent','32':'i32 initial_price_setting','36':'i32[12] disc_image_ids','84':'i32 season_code'},products=products,fixtures=fixtures,cash_profile_references=refs))
    plans=[]
    for f in fixtures:
        for p in f['allowed_product_ids']:
            for direction in range(4):
                # Deduplicate months with the same actual repaint result.
                groups={}
                for month in range(1,13):
                    size,bases=select_images(products[p],f,direction,month)
                    groups.setdefault(tuple(bases),[]).append(month)
                plans.append(dict(fixture=f['id'],product=p,direction=direction,size=size,variants=[dict(months=months,runtime_image_bases=list(bases)) for bases,months in groups.items()]))
    js('android-stock-bridge.json',dict(schema_version=1,source_exe_sha256=EXE_SHA,product_26_key='cash',label_corrections=[dict(product=26,name='現金'),dict(fixture=43,name='キャッシュディスペンサー'),dict(fixture=44,name='キャッシュディスペンサー')],direction_offsets=list(range(4)),direction_note='Source direction index, not compass names.',state_rule='Persist per-cell image base on consumption; choose repaint variant at refill/replacement using source month 1..12.',phase_rule='t=capacity//3; quantity<=t:2; quantity<=2*t:1; otherwise:0',draw_rule='Draw goods only if 360<=image_code<640 and quantity>0.',plans=plans))
    with (ROOT/'products.csv').open('w',newline='') as fh:
        w=csv.writer(fh); w.writerow(['id','name','base_price','cost_percent','initial_price_setting','season_code','fixture_ids','disc_image_ids'])
        for p in products: w.writerow([p[k] for k in ['id','name','base_price','cost_percent','initial_price_setting','season_code']]+[' '.join(map(str,p['allowed_fixture_ids'])),' '.join(map(str,p['disc_image_ids']))])
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN); asm=[]
    for name,a,end in [('store_initialize',0x8001b0c8,0x8001b320),('stock_update',0x800209f8,0x80021f20),('equipment_product_records',0x8005643c,0x8005670c),('tile_record',0x8005670c,0x80056a3c),('runtime_tables_bootstrap',0x8005c858,0x8005caf0)]:
        b=at(a,end-a); (ROOT/'source'/f'{name}.bin').write_bytes(b)
        asm.append(f'\n# {name} {a:#x}..{end:#x}, sha256={sha(b)}')
        asm.extend(f'{i.address:08x}: {i.bytes.hex()}  {i.mnemonic} {i.op_str}' for i in md.disasm(b,a))
    (ROOT/'stock-readers.asm').write_text('\n'.join(asm)+'\n')
    pages=[]
    for n in range(3):
        name=next(k for k in files if k.endswith(f'SYOP_S0{n}.TIM'))
        meta,im,_=prior['tim'](payload(name)); pages.append(im)
    font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',16)
    canvas=Image.new('RGB',(1900,27*64+44),'#e5e5e5'); draw=ImageDraw.Draw(canvas)
    draw.text((10,8),'商品画像：各組は 在庫多・中・少（数量0では非表示） / 原TIMから抽出',font=font,fill='black')
    for p in products:
        y=44+p['id']*64; draw.text((8,y+12),f"{p['id']:02d} {p['name']}",font=font,fill='black')
        for j,base in enumerate(p['runtime_image_bases']):
            if base<0: continue
            for phase in range(3):
                code=base+phase; page=0 if code<=256 else 1 if code<=512 else 2
                x=(code&15)*16; v=code&240
                tile=pages[page].crop((x,v,x+16,v+16)).resize((32,32),Image.Resampling.NEAREST)
                canvas.paste(tile,(300+j*132+phase*34,y+18),tile)
            draw.text((300+j*132,y),str(j),font=font,fill='black')
    canvas.save(ROOT/'product-images.png')
    # A data-driven example of the month transition, not an executed game trace.
    example=None
    for plan in plans:
        if plan['product'] not in [20,21,24,26] and len(plan['variants'])>1:
            f=fixtures[plan['fixture']];p=products[plan['product']];_,a=select_images(p,f,plan['direction'],1);_,b=select_images(p,f,plan['direction'],2)
            if a!=b:
                example=dict(fixture=f['id'],product=p['id'],direction=plan['direction'],month1_refill_bases=a,month2_sale_bases=a,month2_refill_bases=b); break
    assert example is not None
    js('summary.json',dict(products=27,fixtures=53,compatible_pairs=sum(len(f['allowed_product_ids']) for f in fixtures),direction_plans=len(plans),cash=dict(product=26,name='現金',fixtures=[43,44],profile_references=refs,ordinary_withdrawal_behavior='unconfirmed'),month_transition_example=example,execution='Static extraction only; no simulated business updates.'))
    print(json.dumps(dict(products=27,fixtures=53,plans=len(plans),example=example),ensure_ascii=False))
if __name__=='__main__': main()
