#!/usr/bin/env python3
"""Extract owner evaluation labels, literal thresholds and map/project population inputs.
All derived states are static calculations, not emulated annual gameplay.
"""
import argparse,hashlib,itertools,json,runpy,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);a=ap.parse_args();raw=a.disc.read_bytes();assert sha(raw)==DISC_SHA
 iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'];rows,read=iso(raw);files={r['path']:r for r in rows}
 def payload(p):r=files[p];return read(r['lba'],r['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 def imm(a):return struct.unpack('<I',at(a,4))[0]&65535
 def large(a,b):
  if a is None:assert struct.unpack('<I',at(b,4))[0]>>26==13;return imm(b)+1
  assert struct.unpack('<I',at(a,4))[0]>>26==15 and struct.unpack('<I',at(b,4))[0]>>26==13
  return (imm(a)<<16|imm(b))+1
 vis=[large(a,b) for a,b in [(None,0x8003f9e4),(0x8003fa0c,0x8003fa10),(0x8003fa3c,0x8003fa40),(0x8003fa6c,0x8003fa70),(0x8003fa9c,0x8003faa0)]]
 sales=[large(a,b) for a,b in [(0x8003fae0,0x8003fae4),(0x8003fb08,0x8003fb0c),(0x8003fb34,0x8003fb38),(0x8003fb60,0x8003fb64),(0x8003fb8c,0x8003fb90)]]
 def small(addrs):
  for a in addrs:assert struct.unpack('<I',at(a,4))[0]>>26==10
  return [imm(a) for a in addrs]
 pop=small([0x8003fbd4,0x8003fbf8,0x8003fc20,0x8003fc48,0x8003fc70]);rating=small([0x8003fcb0,0x8003fcd4,0x8003fcfc,0x8003fd24,0x8003fd4c])
 assert vis==[50000,100000,200000,400000,500000] and sales==[100000000,200000000,300000000,400000000,600000000]
 assert pop==[3000,8000,14000,18000,20000] and rating==[10,30,50,70,90]
 decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
 def string(a):
  codes=[]
  for j in range(100):
   v=struct.unpack('<H',at(a+j*2,2))[0];codes.append(v)
   if v==0x40ff:break
  assert codes[-1]==0x40ff
  return dict(address=hex(a),codes=codes,text=decode(codes))
 labels=string(0x800b949c);parts=labels['text'].replace('{4002}','\n').splitlines();assert parts==['店舗数','累積来客数','年商','町人口','店舗評価','','総合評価']
 put('source-labels.json',dict(labels=labels,store_unit=string(0x800b9494),person_unit=string(0x800b94d4),star_glyphs=dict(filled=0x28b,empty=0x28c,display='Always five glyphs; fill min(5,max(0,value)).'),decoder='Previously transcribed original PSMOJI font mapping; no new glyph recognition.'))
 metrics=[]
 for j,(key,bands,kind) in enumerate([('stores',list(range(1,11)),'count*2'),('visitors',vis,'bands'),('sales',sales,'bands'),('population',pop,'bands'),('rating',rating,'bands')]):
  metrics.append(dict(id=key,label=parts[j],thresholds_inclusive=bands,points=[2*x for x in range(1,11)] if j==0 else [4,8,12,16,20],comparison='unsigned32' if j==1 else 'signed32',display_stars='trunc(points/4)',value_source=['active owner0 records among first10','cumulative own entered customers RAM0x800cd930','saturating sum of store+0xd0c previous annual ledger revenue','population(0): all town categories, signed16 profile counts','trunc(sum of store+0xc68 evaluation / active own store count)'][j]))
 put('evaluation-thresholds.json',dict(metrics=metrics,raw_total='sum of five points; displayed total=100 if raw>=96 else raw',total_stars='trunc(displayed total/20)',total_address='0x800cd80c',value_slots='0x800e3ba8 + metric*4',point_slots='0x800e3bc0 + metric*4',bounds='Normal positive own store count1..10. Zero own stores causes original divide-by-zero in this consumer; no synthetic score0 asserted.'))
 def points(v,bands):return 4*sum(v>=b for b in bands)
 combos=[]
 for stores in range(1,11):
  for q in itertools.product(range(6),repeat=4):
   raw=stores*2+sum(q)*4
   if raw>=96:combos.append(dict(stores=stores,parts=[stores*2]+[x*4 for x in q],raw=raw,total=100,
     lower_bounds=dict(zip(['cumulative_visitors','previous_annual_sales','total_town_population','mean_store_evaluation'],[b[n-1] if n else None for b,n in zip([vis,sales,pop,rating],q)]))))
 assert len(combos)==7
 put('perfect-score-combinations.json',dict(context='Derived joint requirements over normal count1..10 and each of four six-band metrics; not new gameplay tests.',minimum_stores=8,combinations=combos,
 note='Mode2/3 ending compares displayed100, so raw96 or98 qualifies. Mode1 ten-store target is a separate milestone, not this annual-score requirement.'))
 groups=[list(zip(*[iter(struct.unpack('<10h',at(0x8009ff1c+j*20,20)))]*2)) for j in range(137)]
 gpop=[sum(n for pid,n in pairs if pid!=-1) for pairs in groups]
 buildings=[]
 for k in range(72):
  b=at(0x8009d738+k*56,56);w,h,lo,hi=struct.unpack_from('<4i',b,24);cat=struct.unpack_from('<b',b,40)[0]
  buildings.append(dict(id=k,w=w,h=h,lo=lo,hi=hi,category=cat))
 lookup={t:d for d in reversed(buildings) for t in range(d['lo'],d['hi']+1)}
 projects=json.loads((ROOT.parent/'20261115-town-project-data/project-master.json').read_text())['rows']
 quotes=json.loads((ROOT.parent/'20261115-town-project-data/map-project-costs.json').read_text())['maps']
 worlds=[];examples=[]
 for world in quotes:
  name=world['map'];data=payload('/DAT/'+name+'.BIN');town=data[17:24017]
  tiles=[struct.unpack_from('<h',town,k*8)[0] for k in range(3000)];cats=[struct.unpack_from('<b',town,k*8+4)[0] for k in range(3000)];mixes=[struct.unpack_from('<h',town,k*8+6)[0] for k in range(3000)]
  populations=[0 if m==-1 else gpop[m] for m in mixes];total=sum(populations);bycat={str(c):sum(v for v,cat in zip(populations,cats) if cat==c) for c in sorted(set(cats))}
  stores=[]
  for slot in range(10):
   s=data[25907+slot*5080:25907+(slot+1)*5080]
   if s[0]:stores.append(dict(slot=slot,flags=struct.unpack_from('<H',s,4)[0],evaluation_C68=struct.unpack_from('<i',s,0xc68)[0],popularity_C6C=struct.unpack_from('<i',s,0xc6c)[0],previous_annual_sales_D0C=struct.unpack_from('<i',s,0xd0c)[0]))
  own=[s for s in stores if not s['flags']&0x8000]
  worlds.append(dict(map=name,source_town_sha256=sha(data),population=total,population_by_category=bycat,population_points=points(total,pop),source_stores=stores,active_own_stores=len(own),owner_report_valid=bool(own),note='No initial own stores. Do not run annual average on the unmodified source file.'))
  for q in world['projects']:
   if not q['examples']:continue
   project=projects[q['selection']];ex=q['examples']['cheapest'];x,y,x2,y2=ex['rect'];affected={yy*60+xx for yy in range(y,y2+1) for xx in range(x,x2+1)}
   for yy in range(y,y2+1):
    for xx in range(x,x2+1):
     k=yy*60+xx
     if cats[k]<=0:continue
     d=lookup.get(tiles[k],buildings[0]);left=xx-(tiles[k]-d['lo'])%d['w'];top=yy-(tiles[yy*60+left]-d['lo'])//d['w']
     affected.update(ay*60+ax for ay in range(top,top+d['h']) for ax in range(left,left+d['w']))
   removed=sum(populations[k] for k in affected);after=[total-removed+n for n in project['completed_building_population_range']]
   examples.append(dict(map=name,selection=q['selection'],name=project['name'],site=ex['origin'],total_fee=ex['total_charge'],before_population=total,removed_population=removed,completed_population_bounds=after,population_point_bounds=[points(v,pop) for v in after],
       scope='Counterfactual independent completion on initial map at first cheapest origin. Whole overlapping buildings removed. No natural growth, customer RNG trace, other projects, or yearly sales/score assigned. Bounds are theoretical cell-choice bounds, not a guarantee both endpoints are realizable by one LCG seed.'))
 put('initial-evaluation-inputs.json',worlds);put('project-population-score-links.json',examples)
 ranges=[('owner_evaluation',0x8003f7fc,0x8003fe88),('annual_queue',0x8003ceac,0x8003cf44),('annual_ledger_rollover',0x80029fc8,0x8002a0c4),('event_dispatch',0x8003ef44,0x8003f528),('event_reserve',0x8003ecd8,0x8003ef44),('ten_store_milestone',0x8003ead4,0x8003ecd8),('visitors_save',0x8006baa4,0x8006babc),('visitors_load',0x8006bec4,0x8006bedc),('arrival_counter',0x800325e0,0x80032678),('arrival_owner_gate',0x800320cc,0x800320f4),('population_reader',0x80020498,0x800206ac),('owner_screen',0x8006c8b0,0x8006cde0),('display_labels',0x800b9494,0x800b94d8),('clock_order',0x80023438,0x800234f0)]
 rs=[]
 for name,start,end in ranges:
  b=at(start,end-start);(ROOT/f'source/{name}.bin').write_bytes(b);rs.append(dict(file=f'source/{name}.bin',start=hex(start),end_exclusive=hex(end),sha256=sha(b)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=rs))
 put('summary.json',dict(metrics=5,threshold_values=30,source_maps=4,source_cells=12000,initial_total_populations={w['map']:w['population'] for w in worlds},linked_source_stores=sum(len(w['source_stores']) for w in worlds),project_population_links=len(examples),perfect_score_combinations=len(combos),minimum_stores_for_score100=8,original_cpu_updates=0,
  known_before='Owner-rating scalar formulas, annual-close helpers and controlled owner-screen chains existed. This work extracts source labels/literal thresholds, links 4 actual maps/11 stores and 72 project completion population bounds, derives all7 perfect-score band combinations and records cumulative visits versus annual revenue semantics.'))
 print('Extracted5 metrics,30 literal/count thresholds,4 source towns,72 project-population links,7 perfect-score combinations.')
if __name__=='__main__':main()
