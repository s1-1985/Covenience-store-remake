#!/usr/bin/env python3
"""Extract original patience, staff decline callsites and source word16 values."""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
R=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
 entries,read=runpy.run_path(str(R.parent/'20261113-disc-data-extraction/extract-disc-data.py'))['iso'](raw);fs={x['path']:x for x in entries}
 def payload(p):r=fs[p];return read(r['lba'],r['bytes'])
 exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
 def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 rows=[]
 for i in range(144):
  p=at(0x800a09d0+i*24,24);rows.append(dict(profile=i,patience=struct.unpack_from('b',p,17)[0]))
 put('profile-patience.json',dict(rows=rows,histogram=dict(sorted(collections.Counter(x['patience'] for x in rows).items())),initial_assignment='0x80031F08..0x80031F10: profile+17 -> customer+0x1C'))
 callword=(3<<26)|((0x8003aa58>>2)&0x3ffffff);sites=[]
 for a in range(0x80010000,0x80098000,4):
  if struct.unpack('<I',at(a,4))[0]==callword:sites.append(a)
 assert sites==[0x80035f9c,0x80037534,0x8003771c,0x80038868]
 # Raw direct JALs in this source text span; indirect calls are outside this inventory.
 put('growth-direct-callers.json',dict(code_span=['0x80010000','0x80098000'],target='0x8003AA58',rows=[dict(call=hex(a),mode=m,context=c) for a,m,c in zip(sites,[-1,2,4,1],['patience exhaustion terminal branch','restock completion','cleaning success','checkout service success'])],scope='Literal direct-JAL inventory in original source code span; no claim of exhaustive indirect-call reachability.'))
 skills=[0x1e,0x1f,0x21,0x22];names=['レジ','補充','清掃','警備'];table=[]
 for roll in range(1,101):table.append(dict(roll=roll,staff_decline=roll%3==0,rating_decrement_if_at_least6=roll%10==0))
 assert sum(x['staff_decline'] for x in table)==33 and sum(x['staff_decline'] and x['rating_decrement_if_at_least6'] for x in table)==3
 put('shared-roll-table.json',dict(rows=table,decline_rolls=33,rating_rolls=10,both_rolls=3,domain=100,scope='Exact mapping of original1..100 roll, not an independent probability model or a measured RNG-frequency experiment.'))
 worlds=[]
 for n in ('TOWN0001','TOWN0002','TOWN0003','TOWNPS'):
  b=payload('/DAT/'+n+'.BIN');staff=[]
  for i in range(35):
   p=b[24017+i*54:24017+(i+1)*54];word16=struct.unpack_from('<i',p,13)[0];staff.append(dict(id=i,word16=word16))
  worlds.append(dict(map=n,source_sha256=sha(b),staff=staff))
 put('word16-source-values.json',dict(packed_offset=13,runtime_offset=16,maps=worlds,scope='All140 source records extracted. Loader copies4 bytes. Meaning remains unknown; zero does not prove unused.'))
 rules=dict(patience=dict(function='0x80035D58',first='Always draw roll1..100 before checking force/patience',force='Nonzero force sets patience0',normal='If signed patience>0 draw another RNG and decrement1 only if RNG&3==0',continuing='If resulting patience>0 return1 without abandonment consequences',terminal='Otherwise set global flag0x20 and continue'),cart=dict(terminal='If signed16 cart!=0, add signed16(cart)*signed8(group_quantity) to store.D98 and owner company cash through1CA7C(mode1); clear cart to0',scope='Original posts positive amount, not refund or negative lost sales. It does not perform a fresh wallet deduction here.'),decline=dict(trigger='terminal AND initial roll%3==0',selection='Iterate all3 store staff references atDD8; skip only-1',skills=[dict(offset=hex(o),name=n) for o,n in zip(skills,names)],rule='Each selected skill decrements1 only if signed current>=2',unchanged=['接客+0x20','基本能力+0x18..+0x1D','word16'],rng='Growth helper draws one RNG per present staff even in mode-1, after reading manager academic value; that roll does not determine whether mode-1 decrements'),rating=dict(trigger='same initial roll%10==0 AND store.C68>=6',effect='C68-=1; lower bound5 on this branch',unaffected='C6C popularity is not the affected field'),counter=dict(field='store+0x12E1',terminal='If signed counter<127 increment1'),callers=[dict(address='0x8003501C',force=0,context='shopping movement obstruction after sidestep failure'),dict(address='0x800351D0',force=1,context='nonempty cart, unset checkout goal, checkout destination search fails'),dict(address='0x800352AC',force=0,context='at checkout position, cashier service returns nonzero'),dict(address='0x8003567C',force=0,context='checkout movement obstruction after sidestep failure')],scope='Connects previously recovered wait helper and decline arithmetic to original callsites and all-staff scope; no gameplay/physical timing experiment.')
 put('abandonment-rules.json',rules)
 blocks=[('wait_resolution',0x80035d58,0x800360a0),('growth_entry',0x8003aa58,0x8003ab24),('growth_decrement',0x8003b158,0x8003b278),('posting_mode1',0x8001cb3c,0x8001cbb0),('forced_checkout_abandon',0x80035178,0x800351e4),('checkout_service_wait',0x80035288,0x800352d4),('word16_loader',0x8001a3cc,0x8001a414),('initial_patience',0x80031ee4,0x80031f14)]
 rs=[]
 for n,a,z in blocks:
  b=at(a,z-a);(R/'source'/f'{n}.bin').write_bytes(b);rs.append(dict(file=f'source/{n}.bin',start=hex(a),end_exclusive=hex(z),sha256=sha(b)))
 put('source-ranges.json',dict(disc_sha256=DISC_SHA,exe_sha256=EXE_SHA,ranges=rs))
 put('summary.json',dict(date_jst='2026-11-17',profile_patience_rows=144,staff_source_rows=140,word16_nonzero_source_rows=sum(s['word16']!=0 for w in worlds for s in w['staff']),direct_growth_callers=4,direct_decline_callers=1,wait_callers=4,decline_target_slots=3,decline_skill_fields=4,shared_roll_decline_count=33,shared_roll_rating_count=10,shared_roll_joint_count=3,roll_domain=100,original_cpu_updates=0,known_before='Standalone wait_resolution, growth decrement arithmetic and original skill names existed. New source joins identify all literal direct growth callers, mode-1 parent, four normal/forced wait sites, common roll coupling and positive cart posting.',unresolved='R07 word16 meaning remains unknown; source values and loader copy are scoped evidence only.'))
 print('Extracted patience144, source staff140 and direct decline/wait connections.')
if __name__=='__main__':main()
