"""Replay original selection and award excerpts without replacing callees. Research only."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import *
exe=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(exe).hexdigest();assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
STORE=0x12b2f8;FRAME=0x1f0000;STOP=0x80001000
KINDS=['contest','popular','clean','service','cheap']
def put(u,a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def get(u,a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 for r,v in [(UC_MIPS_REG_SP,FRAME|0x80000000),(UC_MIPS_REG_FP,FRAME|0x80000000),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 return u
needle=struct.pack('<I',0x0c000000|((0x8003ceac>>2)&0x3ffffff))
callers=[0x80010000+i-2048 for i in range(2048,len(exe)-4,4) if exe[i:i+4]==needle]
assert callers==[0x800234e8]
rows=[]
for kind in range(5):
 for values in [[20]*4,[20]*5,[20]*10,[10,99,99,20,5],[0,0,0,0,0],[-5,-4,-3,-2,-1]]:
  for seed in [0,1,12345]:
   u=machine();put(u,FRAME+0x18,'<I',kind);put(u,0xd6270,'<I',seed)
   slots=[7,0,3,1,9,2,8,6,4,5][:len(values)]
   for i in range(10):put(u,0xce61c+i*4,'<i',slots[i] if i<len(slots) else -1)
   for slot,value in zip(slots,values):
    base=STORE+slot*5080;put(u,base+4,'<H',0x8000 if slot%2 else 1)
    if kind in [0,1]:put(u,base+(0xc68 if kind==0 else 0xc6c),'<i',value)
    else:put(u,0xce65c+slot*168+{2:4,3:12,4:0}[kind],'<i',100-value if kind==4 else value)
   def stop(uc,address,size,userdata):
    if address==0x8003dd90:uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,stop);u.emu_start(0x8003cfb8,0x8003d508,count=200000)
   eligible=len(values)>=5 and (kind!=4 or max(values)>0)
   after=get(u,0xd6270,'<I');winner=-1
   if eligible:
    after_expected=(seed*1103515245+12345)&0xffffffff;roll=(after_expected>>16)&32767
    choices=[i for i,v in enumerate(values) if v==max(values)];winner=choices[roll%len(choices)]
    assert get(u,FRAME+0x80,'<I')==(STORE+slots[winner]*5080)|0x80000000
    assert after==after_expected
   else:assert after==seed and u.reg_read(UC_MIPS_REG_PC)==0x8003dd90
   rows.append(dict(kind=KINDS[kind],values=values,seed=seed,winner=winner,seed_after=after))
awards=[]
# Execute actual company payment callee and stop before text formatting.
for owner in [0,1]:
 for stores in [5,10]:
  u=machine();put(u,FRAME+0x80,'<I',STORE|0x80000000);put(u,FRAME+0x88,'<I',stores);put(u,STORE+4,'<H',owner<<15)
  for company in [0,1]:put(u,0xcd9f8+company*4,'<i',100000000);put(u,0xd8f68+company*16,'<i',0)
  u.emu_start(0x8003d54c,0x8003d590,count=10000)
  cash=[get(u,0xcd9f8+c*4,'<i') for c in [0,1]];expense=[get(u,0xd8f68+c*16,'<i') for c in [0,1]]
  assert cash[owner]==100000000+stores*10000000 and cash[1-owner]==100000000 and expense[owner]==-stores*10000000
  awards.append(dict(owner=owner,stores=stores,cash=cash,expense=expense))
growth=[]
for kind,start,end,offset in [('popular',0x8003d6e4,0x8003d83c,26),('clean',0x8003d87c,0x8003d9d4,27),('service',0x8003da14,0x8003db6c,28),('cheap',0x8003dbac,0x8003dd04,24)]:
 for before in [0,98,99,100]:
  u=machine();put(u,FRAME+0x80,'<I',STORE|0x80000000);put(u,STORE+0xdd8,'<h',2)
  person=0x143ff8+2*60;put(u,person+29,'<b',before);put(u,person+offset,'<b',before);put(u,person+25,'<b',17)
  u.emu_start(start,end,count=10000);academic=get(u,person+29,'<b');trait=get(u,person+offset,'<b')
  assert academic==min(100,before+2) and trait==academic and get(u,person+25,'<b')==17
  growth.append(dict(kind=kind,before=before,after=academic,current_stamina=17))
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,global_callers=callers,selections=rows,awards=awards,growth=growth,original_excerpts=len(rows)+len(awards)+len(growth),scope='Selection with synthetic active list/store summaries; actual award/payment/trait write excerpts, stop before text/UI; no full event or operating-loop equality'),separators=(',',':'))+'\n')
print('TOWN_PRESS_SOURCE_PASS',len(rows),'selections',len(awards),'company awards',len(growth),'growth')
