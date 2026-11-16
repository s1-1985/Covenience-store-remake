#!/usr/bin/env python3
"""Extract source weather/HUD ranges and map-weighted preselection eligibility, no CPU."""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
 iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'];entries,read=iso(raw);files={r['path']:r for r in entries}
 def payload(p):r=files[p];return read(r['lba'],r['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];msg=payload(next(k for k in files if k.endswith('/MSG00.OBJ')))
 labels=[]
 for idx in range(62,71):
  offset=struct.unpack_from('<I',msg,idx*4)[0];cs=[]
  for k in range(32):
   c=struct.unpack_from('<H',msg,offset+2*k)[0];cs.append(c)
   if c==0x40ff:break
  labels.append(dict(index=idx,codes=cs,label=dec(cs)))
 labelmap={x['index']:x['label'] for x in labels};put('weather-labels.json',dict(source='/DAT/MSG00.OBJ',messages=labels,decoder='Previously transcribed original PSMOJI mapping reused.'))
 profiles=[]
 for j in range(144):
  b=at(0x800a09d0+j*24,24);importance,weekday,holiday=[struct.unpack_from('<b',b,a)[0] for a in (13,21,22)]
  profiles.append(dict(id=j,importance=importance,maximum_weather=importance+20,primary_product=struct.unpack_from('<b',b,8)[0],weekday_share=weekday,holiday_share=holiday))
 put('profile-weather-limits.json',dict(profiles=profiles,rule='Reject only if signed profile[13]+20 < weather. Equality passes. Before seasonal/share/store-choice/stock/queue gates. Festival CDA00!=0 bypasses this gate.'))
 masks=bytearray()
 for weather in range(80):
  row=bytearray(18)
  for p in profiles:
   if weather<=p['maximum_weather']:row[p['id']//8]|=1<<(p['id']%8)
  masks.extend(row)
 (ROOT/'weather-profile-eligibility.bits').write_bytes(masks)
 support=[(0,0),(1,19),(20,39),(40,59),(60,79)]
 months=[];rollgrid=bytearray()
 for month in range(1,13):
  ts=list(struct.unpack('<4i',at(0x800994b0+(month-1)*16,16)));selectors=list(struct.unpack('<5H',at(0x800997e0+(month-1)*10,10)));days=list(struct.unpack('<4b',at(0x80099d88+(month-1)*4,4)))
  assert ts==sorted(ts) and all(0<=v<=100 for v in ts) and set(days)<=set((0,1))
  rolls=[next((k for k,t in enumerate(ts) if roll<=t),4) for roll in range(1,101)];rollgrid.extend(rolls)
  buckets=[dict(bucket=k,first_roll_count=rolls.count(k),output_weather_inclusive=list(support[k]),rng_calls=1 if k==0 else 2) for k in range(5)]
  hud=[dict(column=k,weather_condition=['==0','1..19','20..49','50..79','>=80'][k],message=62+v,label=labelmap[62+v],generated_by_this_normal_producer=k<4) for k,v in enumerate(selectors)]
  months.append(dict(month=month,thresholds=ts,first_roll_buckets=buckets,hud=hud,stage_day_share_selector=days))
 put('monthly-weather-hud.json',dict(threshold_base='0x800994b0,12x16',hud_base='0x800997e0,12x10',calendar_base='0x80099d88,12x4',months=months,
  scope='First-roll counts are interval cardinalities over1..100, not measured LCG frequencies or independent output probabilities. Producer outputs0..79 only. HUD>=80 exists but is not produced by this function; no all-writers proof of global unreachability.'))
 (ROOT/'first-roll-buckets.u8').write_bytes(rollgrid)
 groups=[list(zip(*[iter(struct.unpack('<10h',at(0x8009ff1c+j*20,20)))]*2)) for j in range(137)]
 worlds=[];outside=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  data=payload('/DAT/'+name+'.BIN');town=data[17:24017];weights=collections.Counter()
  for k in range(3000):
   mix=struct.unpack_from('<h',town,k*8+6)[0]
   if mix==-1:continue
   for pid,qty in groups[mix]:
    if pid==-1:continue
    weights[pid]+=qty
    if not 0<=pid<144:outside.append(dict(map=name,cell=[k%60,k//60],mix=mix,profile=pid,heads=qty))
  known=sum(n for pid,n in weights.items() if 0<=pid<144);unknown=sum(n for pid,n in weights.items() if not 0<=pid<144);byweather=[]
  for w in range(80):
   accepted=[p for p in profiles if w<=p['maximum_weather']];heads=sum(weights[p['id']] for p in accepted)
   byweather.append(dict(weather=w,accepted_known_heads=heads,rejected_known_heads=known-heads,accepted_profile_rows=len(accepted),
       weekday_share_weight_sum=sum(weights[p['id']]*p['weekday_share'] for p in accepted),holiday_share_weight_sum=sum(weights[p['id']]*p['holiday_share'] for p in accepted)))
  worlds.append(dict(map=name,source_town_sha256=sha(data),population_including_out_of_catalog=sum(weights.values()),known_profile_heads=known,out_of_catalog_heads=unknown,profile_head_weights=dict(sorted(weights.items())),weather_rows=byweather,
       festival_bypass_known_heads=known,scope='Static original-map customer composition weights passing weather only; not distinct people observed, arrivals, store choices or sales. Share sums are raw weighted threshold values, not expected realized demand.'))
 put('map-weather-cohorts.json',worlds)
 put('out-of-catalog-context.json',dict(known_before='Customer-data20261113 already identified mix136/profile144 as adjacent non-profile bytes, retained in total population but unsafe to treat as normal profile.',references=outside,
  adjacent_raw=at(0x800a09d0+144*24,24).hex(),normal_route='Primary product would read-111 from adjacent bytes; original normal seasonal gate rejects this path as previously recovered.',
  festival_connection='CDA00 has a source-reachable month8/day4 producer and bypasses the three filters in demand rebuild. New static connection only; later store-selection behavior for profile144 under bypass is unresolved. No observed crash/corruption claim.',
  port='Keep source population counts separate from valid demand profiles. Do not silently delete these heads from population or dereference profile144 as an Android person.'))
 ranges=[('weather_and_demand_filter',0x8002619c,0x80026730),('hud_weather_dispatch',0x80040a60,0x80040de8),('festival_flag_producer',0x80029394,0x80029504),('update_order',0x80023438,0x800234f0)]
 rs=[]
 for n,a,b in ranges:
  v=at(a,b-a);(ROOT/f'source/{n}.bin').write_bytes(v);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(b),sha256=sha(v)))
 for n,a,size in [('weather-thresholds',0x800994b0,192),('hud-selectors',0x800997e0,120),('calendar-selectors',0x80099d88,48)]:
  v=at(a,size);(ROOT/f'source/{n}.bin').write_bytes(v);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(a+size),sha256=sha(v)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=rs))
 put('summary.json',dict(months=12,hud_mappings=60,weather_labels=9,profiles=144,weather_levels=80,eligibility_bits=11520,maps=4,map_weather_rows=320,out_of_catalog_references=len(outside),original_cpu_updates=0,
 known_before='Weather generation, seasonal filter and source month thresholds already recovered. New extraction joins five generation ranges to monthly five-column HUD labels,144 profile cutoffs to4 source-map weather cohorts, and calendar-reachable festival flag to normal filter bypass plus profile144 boundary context.',
 examples={w['map']:dict(known_heads=w['known_profile_heads'],weather79_accepted=w['weather_rows'][79]['accepted_known_heads'],out_of_catalog_heads=w['out_of_catalog_heads']) for w in worlds}))
 print('Extracted12 weather/HUD rows,60 mappings,11520 gate bits,320 map cohorts and festival boundary context.')
if __name__=='__main__':main()
