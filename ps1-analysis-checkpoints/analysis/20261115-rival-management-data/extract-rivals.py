#!/usr/bin/env python3
"""Link native monthly rival policies to original maps, layouts and people; no emulation."""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def i32(v):return (v+2**31)%2**32-2**31
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
 iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'];rows,read=iso(raw);files={r['path']:r for r in rows}
 def payload(p):r=files[p];return read(r['lba'],r['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 # Prior all30-layout extraction is independently tied to these exact original byte ranges.
 layouts=json.loads((ROOT.parent/'20261114-interior-transactions-data/layout-interior-costs.json').read_text())['layouts']
 master=json.loads((ROOT.parent/'20261114-interior-transactions-data/fixture-transaction-master.json').read_text());fixtures=master['fixture_rows'];products=master['product_rows']
 def byimage(im):return next((p for p in products if any(v//3==im//3 for v in p['runtime_images'])),products[0])
 def asset(s):
  w,h=struct.unpack_from('<2i',s,0x44);eq=stock=0
  for y in range(h):
   for x in range(w):
    v=struct.unpack_from('<I',s,0x108+y*112+x*4)[0];f=v>>12&1023
    if not v&0x80000000 or f>=53:continue
    eq=i32(eq+fixtures[f]['purchase_price']);v=struct.unpack_from('<I',s,0x178+y*112+x*4)[0];im=v>>12&1023
    if im:stock=i32(stock+byimage(im)['procurement_unit']*(v>>24&127))
  tier=struct.unpack_from('<i',s,0xc70)[0];premises=i32((tier//2+1)*3000000+eq+stock)
  return dict(equipment=eq,inventory=stock,premises_refund=premises)
 variants=[]
 for tier in range(6):
  for control in range(3):
   idx=tier*5+control+2;l=layouts[idx];assert sha(at(0x800a2074+idx*3108,3108))==l['sha256']
   prods=sorted({a['stock_product'] for a in l['anchors'] if a['stock_product'] is not None});bits=sum(bit for pid,bit in ((8,1),(2,2),(22,4)) if pid in prods);assert bits==l['required_permit_mask']
   fee=sum(v for b,v in ((1,3000000),(2,7000000),(4,10000000)) if bits&b);construction=(tier//2+1)*6000000
   restriction=8|(4 if bits&1 else 0)|(2 if bits&2 else 0)|(1 if bits&4 else 0)
   variants.append(dict(tier=tier,layout_control=control,loader_mode=control+3,layout=idx,source_layout_sha256=l['sha256'],grid=l['half_cell_grid'],stock_products=prods,permit_selection_mask=bits,site_restriction_mask=restriction,permit_cost=fee,construction_cost=construction,
    equipment_cost=l['equipment_cost'],inventory_cost=l['stock_cost'],non_land_total=construction+fee+l['equipment_cost']+l['stock_cost'],empty_level8_site_total=32000000+construction+fee+l['equipment_cost']+l['stock_cost'],
    ledger=dict(procurement_D94=l['equipment_cost'],capital_excluding_land_demolition=construction+fee+l['stock_cost']),site_cost_scope='32m example is theoretical four level8 cells with zero demolition; not an eligible original-map site.'))
 put('rival-layout-costs.json',dict(layouts=variants,index_rule='tier*5+signed8(TOWN.header0)+2; source header values0..2',posting='Native rival caller sends 1D018 equipment cost to1CA7C procurement,1D618 inventory value to1CBC4 capital. Preserve this caller difference from player opening.'))
 worlds=[];joins=[];refunds=[];hire=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  data=payload('/DAT/'+name+'.BIN');town=data[17:24017];control=struct.unpack_from('<b',data)[0];cash=struct.unpack_from('<2i',data,1);staff=[data[24017+j*54:24017+(j+1)*54] for j in range(35)]
  free=[j for j,b in enumerate(staff) if struct.unpack_from('<H',b)[0]==0];stores=[]
  cats=[struct.unpack_from('<b',town,k*8+4)[0] for k in range(3000)];flags=[0 if c<=0 else 16 if c in (3,4,5) else 24 for c in cats]
  for slot in range(10):
   s=data[25907+slot*5080:25907+(slot+1)*5080]
   if not s[0]:continue
   fl=struct.unpack_from('<H',s,4)[0];rect=struct.unpack_from('<4i',s,8);l,t,r,b=rect
   for yy in range(max(0,t-10),min(49,b+10)+1):
    for xx in range(max(0,l-10),min(59,r+10)+1):
     k=yy*60+xx
     if s[0xc76]:flags[k]|=1
     if l-7<=xx<=r+7 and t-7<=yy<=b+7 and s[0xc75]:flags[k]|=2
     if l-5<=xx<=r+5 and t-5<=yy<=b+5 and s[0xc74]:flags[k]|=4
     if l-4<=xx<=r+4 and t-4<=yy<=b+4:flags[k]|=8
   fields=list(struct.unpack_from('<5i',s,0xd4c));profit=i32(fields[4]-sum(fields[:4]));streak=struct.unpack_from('<H',s,0x1184)[0];after=(streak+1)&65535 if profit<0 else 0
   av=asset(s);land=sum(struct.unpack_from('<b',town,(yy*60+xx)*8+2)[0]*1000000 for yy in range(t,b+1) for xx in range(l,r+1))
   refunds.append(dict(map=name,slot=slot,serial=fl&32767,rect=list(rect),land_refund=land,**av,total_refund=land+av['premises_refund'],scope='Static source asset value for conditional withdrawal; no claim these initial stores withdraw.'))
   stores.append(dict(slot=slot,flags=fl,serial=fl&32767,tier=struct.unpack_from('<i',s,0xc70)[0],rect=list(rect),previous_month_ledger=fields,previous_month_profit=profit,loss_streak=streak,streak_after_next_profit_check=after,staff=list(struct.unpack_from('<3h',s,0xdd8))))
  count=len(stores);limit=2 if count<3 else 4 if count<6 else 6;available=[v['layout'] for v in variants if v['tier']<limit and v['layout_control']==control]
  levels=collections.Counter(struct.unpack_from('<b',town,k*8+2)[0] for k in range(3000));candidate_masks={}
  for mask in sorted({v['site_restriction_mask'] for v in variants}):
   mask_ok=eligible=land_ok=0
   for y in range(49):
    for x in range(59):
     high=struct.unpack_from('<b',town,(y*60+x)*8+2)[0]>=8;land_ok+=high
     ok=all(not flags[yy*60+xx]&mask for yy in (y,y+1) for xx in (x,x+1));mask_ok+=ok;eligible+=high and ok
   candidate_masks[mask]=dict(candidate_origins=2891,geometry_and_permit_only=mask_ok,land_level_only=land_ok,eligible=eligible)
  for v in variants:joins.append(dict(map=name,layout=v['layout'],tier=v['tier'],layout_control=v['layout_control'],selected_by_initial_header_and_count=v['layout'] in available,**candidate_masks[v['site_restriction_mask']]))
  choices=[]
  for start in range(35):
   picked=next((j for j in ((start+n)%35 for n in range(35)) if j in free),None);choices.append(picked)
  weights=collections.Counter(choices)
  hire.append(dict(map=name,free_staff=free,blocked_ownership_words={str(j):struct.unpack_from('<H',b)[0] for j,b in enumerate(staff) if j not in free},first_hire_by_start_index=choices,first_hire_start_counts={str(k):v for k,v in sorted(weights.items())},
   scope='Circular first-free selection for each possible start0..34 before hiring anyone. Counts are not equal probability among free people or independent uniform LCG claims. Later hires exclude already selected ids.'))
  worlds.append(dict(map=name,source_town_sha256=sha(data),header_layout_control=control,cash=list(cash),active_stores=count,active_own_stores=sum(not s['flags']&32768 for s in stores),rival_serial_max=max(s['serial'] for s in stores),size_control_CD994_after_loader=count,tier_limit_exclusive=limit,available_candidate_layouts=available,source_land_histogram=dict(levels),free_staff_count=len(free),stores=stores))
 put('initial-rival-inputs.json',worlds);put('map-layout-siting-links.json',joins);put('initial-withdrawal-values.json',refunds);put('staff-first-free-links.json',hire)
 defaults=[]
 for j in range(27):
  b=at(0x8009cdf0+j*88,88);v=struct.unpack_from('<i',b,32)[0]
  defaults.append(dict(product=j,name=b[:24].split(b'\0')[0].decode('shift_jis'),initial_setting=v,discount_candidates=[dict(delta=d,after=i32(v-d) if d<v else v) for d in range(0,31,5)]))
 put('rival-price-initialization.json',dict(rule='After successful capital posting: for each27 products draw RNG&15. If zero draw another RNG%7*5; subtract only when delta<current setting. Store+0xc7c+product*4. No existing-rival repricing claim.',products=defaults,opening_hours='RNG%6 chooses schedule0..5; schedule6 is excluded from this initialization branch.'))
 ranges=[('monthly_manager',0x8002a8e0,0x8002bd54),('layout_loader',0x8001b678,0x8001b8c4),('equipment_value',0x8001d018,0x8001d1ac),('inventory_value',0x8001d618,0x8001d8ac)]
 rs=[]
 for n,a,b in ranges:
  v=at(a,b-a);(ROOT/f'source/{n}.bin').write_bytes(v);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(b),sha256=sha(v)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=rs))
 put('summary.json',dict(source_maps=4,source_rival_stores=len(refunds),candidate_layouts=18,map_layout_links=len(joins),first_hire_start_links=140,source_products=27,source_sites_per_map=2891,source_eligible_sites_all_layouts=0,free_staff_by_map={w['map']:w['free_staff_count'] for w in worlds},original_cpu_updates=0,
 known_before='Monthly rival decision/withdrawal/opening model and controlled chains existed. New source-data links bind18 actual layout/permit/cost/posting variants to4 headers/72 map-layout rows,11 withdrawal asset values,140 first-free staff starts and27 initial price tables. No new month gameplay runs.'))
 print('Extracted18 rival layouts,72 map links,11 withdrawal values,140 staff starts,27 price tables.')
if __name__=='__main__':main()
