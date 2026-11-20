"""Run original 80035D58 with real growth/payment/RNG callees.
Usage: python probe_abandonment.py EXE OUT.json (Unicorn research only).
Synthetic store/customer/staff; no original UI or natural-play frequency test.
"""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_V0
exe=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(exe).hexdigest()
assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
STORE=0x12b2f8;STAFF=0x143ff8;CUSTOMER=0x160000;STOP=0x80001000
FIELDS=[30,31,32,33,34] # register, refill, service, clean, security
BASE=[[0,1,27,2,17],[12,2,19,1,0],[2,0,8,14,1]]
def rand(seed):
 seed=(seed*1103515245+12345)&0xffffffff;return seed,(seed>>16)&32767
def run(seed,patience,force,slots=(0,1,2),counter=0,rating=6,cart=610,heads=3):
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 def put(a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
 def get(a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
 put(STORE+4,'<H',0);put(STORE+0xdd8,'<3h',*slots);put(STORE+0xc68,'<i',rating);put(STORE+0xc6c,'<i',66);put(STORE+0x12e1,'<b',counter)
 put(0xcd9f8,'<i',100000);put(0xd6270,'<I',seed);put(0xcd790,'<H',0)
 put(CUSTOMER+8,'<h',190);put(CUSTOMER+10,'<h',cart);put(CUSTOMER+28,'<b',patience);put(CUSTOMER+30,'<b',heads)
 for i,row in enumerate(BASE):
  put(STAFF+i*60+27,'<b',80)
  for a,v in zip(FIELDS,row):put(STAFF+i*60+a,'<b',v)
 for r,v in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,STOP),(UC_MIPS_REG_A0,STORE|0x80000000),(UC_MIPS_REG_A1,CUSTOMER|0x80000000),(UC_MIPS_REG_A2,int(force))]:u.reg_write(r,v)
 u.emu_start(0x80035d58,STOP,count=50000);assert u.reg_read(UC_MIPS_REG_PC)==STOP
 result=dict(seed=seed,patience_before=patience,force=force,slots=list(slots),counter_before=counter,rating_before=rating,cart_before=cart,heads=heads,continues=bool(u.reg_read(UC_MIPS_REG_V0)),patience_after=get(CUSTOMER+28,'<b'),cart_after=get(CUSTOMER+10,'<h'),budget_after=get(CUSTOMER+8,'<h'),cash_delta=get(0xcd9f8,'<i')-100000,sales_delta=get(STORE+0xd98,'<i'),rating_after=get(STORE+0xc68,'<i'),popularity_after=get(STORE+0xc6c,'<i'),counter_after=get(STORE+0x12e1,'<b'),seed_after=get(0xd6270,'<I'),flag=get(0xcd790,'<H'),skills_after=[[get(STAFF+i*60+a,'<b') for a in FIELDS] for i in range(3)])
 expected_seed,r=rand(seed);roll=r%100+1;energy=0 if force else patience
 if energy>0:
  expected_seed,r=rand(expected_seed)
  if r&3==0:energy-=1
 terminal=energy<=0
 expected=[row[:] for row in BASE]
 if terminal and roll%3==0:
  for i in slots:
   if i==-1:continue
   expected_seed,_=rand(expected_seed)
   for k in [0,1,3,4]:
    if expected[i][k]>=2:expected[i][k]-=1
 assert result['continues']==(not terminal) and result['patience_after']==energy
 assert result['skills_after']==expected and result['seed_after']==expected_seed
 assert result['cash_delta']==result['sales_delta']==(cart*heads if terminal else 0),result
 assert result['cart_after']==(0 if terminal else cart) and result['budget_after']==190
 assert result['rating_after']==rating-int(terminal and roll%10==0 and rating>=6) and result['popularity_after']==66
 assert result['counter_after']==(min(127,counter+1) if terminal else counter)
 assert result['flag']==(32 if terminal else 0)
 result['roll']=roll;return result
seeds={}
for seed in range(100000):
 _,r=rand(seed);seeds.setdefault(r%100+1,seed)
 if len(seeds)==100:break
rows=[run(seeds[r],5,True) for r in range(1,101)]
for r in [1,3,10,30,60,90]:
 for patience in [-1,0,1,2]:rows.append(run(seeds[r],patience,False,slots=(0,-1,2),counter=127,rating=5,cart=0))
for seed in range(8):rows.append(run(seed,2,False,counter=126))
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,base_skills=BASE,skill_offsets=FIELDS,cases=rows,original_calls=len(rows),callee_replacements=0),separators=(',',':'))+'\n')
print('ABANDONMENT_SOURCE_PASS',len(rows),'full original calls including real growth/payment/RNG')
