#!/usr/bin/env python3
"""Connect the recovered monthly store-byte reset to investigation UI and save data."""
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
 assert struct.unpack('<I',at(0x800235e0,4))[0]==0xa0400002 # sb zero,2(v0)
 assert struct.unpack('<I',at(0x800611bc,4))[0]==0xa0430002 # sb v1,2(v0)
 assert (struct.unpack('<I',at(0x800235cc,4))[0]&65535)==1
 ranges=[('monthly_store_reset',0x80023504,0x80023670),('outer_update_order',0x80023438,0x80023504),('survey_fee_and_set',0x800610e4,0x80061208),('survey_ui',0x8004d7f4,0x8004d8a8),('initialization',0x8001b0c8,0x8001b0f4),('save_store_block',0x8006bb94,0x8006bbb8),('load_store_block',0x8006bfb4,0x8006bfec)]
 rs=[]
 for name,start,end in ranges:
  b=at(start,end-start);(ROOT/f'source/{name}.bin').write_bytes(b);rs.append(dict(file=f'source/{name}.bin',start=hex(start),end_exclusive=hex(end),sha256=sha(b)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=rs))
 worlds=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  data=payload('/DAT/'+name+'.BIN');stores=[]
  for j in range(10):
   b=data[25907+j*5080:25907+(j+1)*5080]
   if b[0]:stores.append(dict(slot=j,owner_flags=struct.unpack_from('<H',b,4)[0],source_inspection_flag=b[2],payload_flag_offset=hex(0x8858+j*5080+2)))
  worlds.append(dict(map=name,source_sha256=sha(data),stores=stores))
 put('initial-inspection-fields.json',worlds)
 steps=[];flag=0
 def calendar(t):return dict(year=t//69120+1,month=t//5760%12+1,stage=t//1440%4+1,hour=t//60%24,subhour=t%60)
 for clock,action in [(1200,'inspect'),(1440,'normal_update'),(5758,'save_load_same_state'),(5760,'normal_update'),(6000,'inspect')]:
  before=flag;cal=calendar(clock);fee=0;changed=False
  if action=='inspect':fee=0 if flag==1 else 500000;flag=1
  elif action=='normal_update' and cal['stage']==1 and cal['hour']==0 and cal['subhour']==0:flag=0;changed=True
  steps.append(dict(clock=clock,calendar=cal,action=action,flag_before=before,flag_after=flag,inspection_fee_paid=fee,monthly_reset=changed))
 put('source-derived-lifetime-example.json',dict(scope='Pure source-rule timeline, not a new CPU/gameplay/save trial. Store assumed to remain in original active order and inspections accepted. Save/load step means record bytes retained before normal update.',steps=steps))
 put('summary.json',dict(resolved_issue='R03 inspection flag ordinary lifetime',source_maps=4,source_stores=sum(len(w['stores']) for w in worlds),reset_pc='0x800235e0',reset_gate='stage/day1 AND hour0 AND subhour0',original_cpu_updates=0,
  known_before='Main-update model already reset store[2] monthly; acquisition extraction left other writers/lifetime unconnected. This work joins those existing source facts and resolves ordinary lifetime, rather than claiming a new monthly algorithm.',limits='No exhaustive indirect-writer proof. Normal path resolved; calendar/save examples are static rule-derived data.'))
 print('Connected monthly inspection reset,11 source store fields and source-rule lifetime example.')
if __name__=='__main__':main()
