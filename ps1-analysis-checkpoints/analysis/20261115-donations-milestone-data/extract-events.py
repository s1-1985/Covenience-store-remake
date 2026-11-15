#!/usr/bin/env python3
"""Original disc data extraction for surplus donation, visitor celebration and festival.
Pure source-data calculations; no original CPU updates.
"""
import argparse,hashlib,json,runpy,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def i32(v):return (v+2**31)%2**32-2**31
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);a=ap.parse_args();raw=a.disc.read_bytes();assert sha(raw)==DISC_SHA
 iso=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'];entries,read=iso(raw);files={r['path']:r for r in entries}
 def payload(p):r=files[p];return read(r['lba'],r['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 def imm(a):return struct.unpack('<I',at(a,4))[0]&65535
 def constant(a,b):return imm(a)<<16|imm(b)
 threshold=constant(0x80027cb0,0x80027cb4);target=-i32(constant(0x80027e5c,0x80027e60));boost=imm(0x80027dbc);cap=imm(0x80027e28)
 assert (threshold,target,boost,cap)==(1500000000,1000000000,5,100)
 assert constant(0x80027ef0,0x80027ef4)==threshold and -i32(constant(0x8002809c,0x800280a0))==target
 divisor=10000;assert imm(0x80052f1c)==divisor and constant(0x80052f3c,0x80052f40)==0xd1b71759
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];msg_path=next(p for p in files if p.endswith('/MSG00.OBJ'));msg=payload(msg_path)
 def codes_from(b,offset):
  cs=[]
  for j in range(200):
   v=struct.unpack_from('<H',b,offset+2*j)[0];cs.append(v)
   if v==0x40ff:return cs
  raise ValueError('No terminator')
 def template(cs):
  out=[];j=0
  while j<len(cs):
   c=cs[j];j+=1
   if c==0x40ff:break
   if c==0x4003:
    width=cs[j];j+=1;out.append('{number:width='+str(width)+'}')
   elif c==0x4002:out.append('\n')
   else:out.append(dec([c]))
  return ''.join(out)
 labels=[]
 for index in (470,471):
  offset=struct.unpack_from('<I',msg,index*4)[0];cs=codes_from(msg,offset);b=struct.pack('<'+'H'*len(cs),*cs);(ROOT/f'source/message-{index}.bin').write_bytes(b)
  labels.append(dict(source=msg_path,index=index,offset=offset,codes=cs,template=template(cs),sha256=sha(b)))
 for address in (0x80098de4,0x80098dfc):
  cs=codes_from(exe,address-0x80010000+2048);labels.append(dict(source='/SLPS_007.82',address=hex(address),codes=cs,template=template(cs)))
 put('event-texts.json',dict(messages=labels,number_control='0x4003 consumes following signed16 width5; that code5 is formatting, not the literal visitor number5.',decoder='Existing original PSMOJI transcription reused. Formatting control handled separately.'))
 put('donation-data.json',dict(cash_trigger_strictly_above=threshold,cash_target=target,popularity_increment=boost,popularity_cap=cap,field='store+0xc6c',not_field='store+0xc68 annual evaluation',calendar='At midnight and stage/day1, after monthly advertising processing and before finance close.',
  primary=dict(condition_cash='0x800cd9f8',stores='active byte!=0 AND owner bit15 clear',amount='i32(current cash - 1000000000)',post='0x8001cbc4(first record0x8012b2f8,amount): company selected from that record flags bit15',notification='kind0,parameter0,sound29,mode1,variant0; original donation text and amount appended'),
  rival=dict(condition_cash='0x800cd9fc',stores='active byte!=0 AND owner bit15 set',post='0x8001cbc4(NULL,amount), chooses company1',notification='None in this branch'),
  assumption='In normal first-record owner0 context the primary posting leaves cash exactly1000000000. Do not assume raw TOWN first slot is own; source files contain only rivals before normal opening/lifecycle setup.'))
 boundaries=[]
 for cash in (999999999,1000000000,1499999999,1500000000,1500000001,1600000000,2000000000,2147483647):
  trigger=i32(cash)>threshold;amount=i32(cash-target) if trigger else 0
  boundaries.append(dict(cash=cash,trigger=trigger,donation=amount,cash_after_if_post_targets_checked_company=i32(cash-amount),popularity_delta_before_cap=boost if trigger else 0))
 put('source-derived-boundaries.json',dict(donation=boundaries,popularity=[dict(before=n,donation_after=min(cap,i32(n+boost)),celebration_after=100) for n in range(101)],
  celebration_write_predicate=[dict(active=active,owner_bit15=owner,write_popularity_100=bool(active or not owner)) for active in (0,1) for owner in (0,1)],
  visitor_quotients=[dict(aggregate=v,display=v>=10000,number=v//10000 if v>=10000 else None) for v in (0,9999,10000,19999,20000,99999999,100000000,0xffffffff)],
  note='Derived lookup data and boundary examples, not newly run CPU test cases. Donation examples assume correct company routing.'))
 calendar=[]
 for month in range(1,13):
  for day in range(1,5):
   festival=month==8 and day==4;calendar.append(dict(month=month,stage_day=day,midnight_donation_check=day==1,festival=festival,pending_celebration_can_run_if_flag_positive=not festival))
 put('calendar-events.json',dict(scope='Only midnight invocations; other hours/subhour states return without these events.',rows=calendar))
 worlds=[]
 for name in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  data=payload('/DAT/'+name+'.BIN');cash=list(struct.unpack_from('<2i',data,1));stores=[]
  for slot in range(10):
   s=data[25907+slot*5080:25907+(slot+1)*5080]
   if not s[0]:continue
   flags=struct.unpack_from('<H',s,4)[0];pop=struct.unpack_from('<i',s,0xc6c)[0]
   stores.append(dict(slot=slot,flags=flags,popularity=pop,entered_visitors=struct.unpack_from('<I',s,0x1188)[0],donation_after_if_company_eligible=min(100,pop+5),celebration_after_if_parent_flag_processed=100))
  worlds.append(dict(map=name,source_town_sha256=sha(data),cash=cash,donation_trigger_initial=[v>threshold for v in cash],source_stores=stores,own_store_visitors=sum(s['entered_visitors'] for s in stores if not s['flags']&0x8000),
   scope='Raw initial files, not a running pre-event snapshot. All stores are rivals; conditional post-event values are reference transforms, not naturally triggered events.'))
 put('initial-event-inputs.json',worlds)
 ranges=[('donations',0x80027c80,0x800280bc),('finance_event_gate',0x80029334,0x800295dc),('arrival_pending_counter',0x800325e0,0x80032678),('visitor_celebration',0x80052dbc,0x800532e8),('festival_screen',0x80052a88,0x80052dbc),('capital_post',0x8001cbc4,0x8001ccc0),('arrival_own_gate',0x800320cc,0x800320f4)]
 rs=[]
 for n,a,b in ranges:
  data=at(a,b-a);(ROOT/f'source/{n}.bin').write_bytes(data);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(b),sha256=sha(data)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,message_file_sha256=sha(msg),ranges=rs))
 put('summary.json',dict(event_groups=3,original_messages=2,maps=4,source_stores=sum(len(w['source_stores']) for w in worlds),midnight_calendar_rows=48,popularity_levels=101,donation_cash_threshold=threshold,donation_cash_target=target,original_cpu_updates=0,
  known_before='Finance-close pending celebration/festival models and controlled displays existed. New data extraction connects native surplus cash donation branches, source message470/471 controls, all4 map inputs/11 stores, source flag-vs-display population writes and compact48-row calendar/101-level popularity data. Advertising table is already analyzed and not counted as new.'))
 print('Extracted donation/celebration/festival data,4 maps,11 stores,48 calendar rows and101 popularity levels.')
if __name__=='__main__':main()
