#!/usr/bin/env python3
"""Source data and scoped standard-customer reachability for cash dispensers."""
import argparse,hashlib,json,runpy,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);a=ap.parse_args();raw=a.disc.read_bytes();assert sha(raw)==DISC_SHA
 iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'];entries,read=iso(raw);files={r['path']:r for r in entries}
 def payload(p):r=files[p];return read(r['lba'],r['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 product=at(0x8009cdf0+26*88,88);base,factor,setting=struct.unpack_from('<3i',product,24);rawimages=list(struct.unpack_from('<12i',product,36));images=[v*3+360 for v in rawimages if v!=-1]
 assert product[:24].split(b'\0')[0].decode('shift_jis')=='現金' and base==0 and factor==100
 fixtures=[]
 for j in (43,44):
  b=at(0x80099f0c+j*196,196);w=struct.unpack('<49i',b);opts=[]
  for v in w[21:48]:
   if v==-1:break
   opts.append(v)
  assert opts==[26] and w[0]&255==5
  fixtures.append(dict(id=j,address=hex(0x80099f0c+j*196),flags=w[0],category=w[0]&255,purchase_price=w[1],maintenance_unit=w[2],capacity=w[3],footprint=list(w[9:11]),products=opts,
    image_default_index=w[48],full_stock_purchase_value=0,full_purchase_total=w[1],removal_full_stock_value=w[1],raw_sha256=sha(b)))
 put('cash-master.json',dict(product=dict(id=26,address=hex(0x8009cdf0+26*88),name='現金',base_price=base,cost_percent=factor,default_setting=setting,raw_images=rawimages,runtime_images=images,stock_unit_cost=0),fixtures=fixtures,
  scope='These are fixture price/maintenance/capacity and zero-valued inventory data, not evidence of withdrawal amounts or transaction fees. Maintenance is source rate unit, not a new per-day quote.'))
 profiles=[];refs=[]
 for j in range(144):
  b=at(0x800a09d0+j*24,24);slots=list(struct.unpack_from('<4b',b,8));profiles.append(dict(profile=j,product_slots=slots))
  refs.extend(dict(profile=j,slot=k) for k,v in enumerate(slots) if v==26)
 assert not refs
 put('standard-customer-candidates.json',dict(profile_rows=144,slots_per_row=4,cash_references=refs,rows=profiles,
   known_before='The previous seasonal-data extraction already found zero profile product slots referencing26. This work joins that invariant to dispenser layouts, generic destination/purchase and advice paths.'))
 def cashanchors(b,width,height,offset):
  out=[]
  for y in range(height):
   for x in range(width):
    v=struct.unpack_from('<I',b,offset+y*112+x*4)[0];kind=v>>12&1023
    if v&0x80000000 and kind in (43,44):
     stock=struct.unpack_from('<I',b,offset+(y+1)*112+x*4)[0]
     out.append(dict(x=x,y=y,fixture=kind,direction=v>>22&3,stock_image=stock>>12&1023,stock_quantity=stock>>24&127))
  return out
 layouts=[]
 for j in range(30):
  b=at(0x800a2074+j*3108,3108);w,h=struct.unpack_from('<2i',b);anchors=cashanchors(b,w,h,196);layouts.append(dict(layout=j,tier=j//5,variant=j%5,dispenser_count=len(anchors),anchors=anchors,source_layout_sha256=sha(b)))
 put('layout-cash-dispensers.json',dict(layouts=layouts,scope='All30 stored layouts, including layouts not selected by one specific user menu.'))
 worlds=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  data=payload('/DAT/'+name+'.BIN');stores=[]
  for slot in range(10):
   b=data[25907+slot*5080:25907+(slot+1)*5080]
   if not b[0]:continue
   w,h=struct.unpack_from('<2i',b,0x44);anchors=cashanchors(b,w,h,0x108)
   stores.append(dict(slot=slot,flags=struct.unpack_from('<H',b,4)[0],dispenser_count=len(anchors),anchors=anchors,
      cash_product_counters=list(struct.unpack_from('<3i',b,0x1198+26*12))))
  worlds.append(dict(map=name,source_town_sha256=sha(data),stores=stores))
 put('initial-store-cash-dispensers.json',worlds)
 decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];msg=payload(next(k for k in files if k.endswith('/MSG00.OBJ')))
 def stream(b,o):
  cs=[]
  for k in range(160):
   v=struct.unpack_from('<H',b,o+2*k)[0];cs.append(v)
   if v==0x40ff:return cs
  raise AssertionError('unterminated')
 labels=[]
 for i in (430,431):
  o=struct.unpack_from('<I',msg,i*4)[0];cs=stream(msg,o);labels.append(dict(source='/DAT/MSG00.OBJ',index=i,codes=cs,text=decode(cs)))
 cs=stream(exe,0x80099338-0x80010000+2048);labels.append(dict(source='/SLPS_007.82',address='0x80099338',codes=cs,text=decode(cs)))
 put('dispenser-texts.json',dict(labels=labels,decoder='Existing PSMOJI transcription reused; underscore/long-vowel glyph readings follow original dictionary.'))
 ranges=[('cash_price_average_exclusion',0x80024080,0x800240d4),('customer_initial_wallet_product',0x80032a38,0x80032ad0),('generic_purchase',0x800340fc,0x80035128),('cash_low_use_advice',0x8003bd78,0x8003be78)]
 rs=[]
 for n,a,b in ranges:
  v=at(a,b-a);(ROOT/f'source/{n}.bin').write_bytes(v);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(b),sha256=sha(v)))
 for n,a,size in [('cash-product',0x8009cdf0+26*88,88),('dispenser-small',0x80099f0c+43*196,196),('dispenser-large',0x80099f0c+44*196,196)]:
  v=at(a,size);(ROOT/f'source/{n}.bin').write_bytes(v);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(a+size),sha256=sha(v)))
 for n,a,size in [('cash-product',0x8009cdf0+26*88,88),('fixture43',0x80099f0c+43*196,196),('fixture44',0x80099f0c+44*196,196),('standard-profiles',0x800a09d0,144*24)]:
  v=at(a,size);(ROOT/f'source/{n}.bin').write_bytes(v);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(a+size),sha256=sha(v)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=rs))
 put('summary.json',dict(cash_product=26,dispenser_fixtures=[43,44],layouts=30,layouts_with_dispenser=sum(bool(x['anchors']) for x in layouts),layout_dispenser_anchors=sum(x['dispenser_count'] for x in layouts),source_maps=4,source_stores=sum(len(w['stores']) for w in worlds),source_stores_with_dispenser=sum(bool(s['anchors']) for w in worlds for s in w['stores']),source_dispenser_anchors=sum(s['dispenser_count'] for w in worlds for s in w['stores']),standard_profile_cash_refs=0,original_cpu_updates=0,
   known_before='Cash product classification and zero ordinary profile references were known. New extraction binds both actual dispenser descriptors,30 layouts and11 source stores to candidate/destination/zero-price purchase semantics and original special low-use message.',
   resolution='R01 remains open but narrowed: no ordinary valid-profile withdrawal route established; dedicated withdrawal/fee path or intended unused-feature behavior remains unresolved. Do not invent banking transactions.'))
 print('Extracted cash fixture/layout/store links and scoped normal-route/low-use advice facts.')
if __name__=='__main__':main()
