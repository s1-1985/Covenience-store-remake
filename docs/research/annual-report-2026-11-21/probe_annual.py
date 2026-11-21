"""Bounded original annual rollover, report reservations and live assessment."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import *
exe=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(exe).hexdigest();assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def put(u,a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def get(u,a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 for r,v in [(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
 return u
additions=[]
for current in [0,2147483647,-2147483648]:
 for monthly in [0,1,-1]:
  u=machine();put(u,0x1f0018,'<I',0x8012b2f8)
  put(u,0x12b2f8+0xcf8,'<i',current);put(u,0x12b2f8+0xd48,'<i',monthly)
  u.emu_start(0x80029c54,0x80029c74,count=1000)
  expected=((current+monthly+2147483648)&0xffffffff)-2147483648
  assert get(u,0x12b2f8+0xcf8,'<i')==expected
  additions.append(dict(current=current,monthly=monthly,expected=expected))
rolls=[]
for current in [0,100,-1,2147483647,-2147483648]:
 for previous in [[],[1000],[2000,1000],[3000,2000,1000]]:
  u=machine();put(u,0xce60c,'<ii',1,1);put(u,0x1f0018,'<I',0x8012b2f8)
  histories=[current]+previous+[0]*(3-len(previous))
  before=[[10*j+k for k in range(4)]+[v] for j,v in enumerate(histories)]
  for j,row in enumerate(before):put(u,0x12b2f8+0xce8+j*20,'<5i',*row)
  u.emu_start(0x80029fc8,0x8002a0b0,count=30000)
  after=[list(struct.unpack('<5i',u.mem_read(0x12b2f8+0xce8+j*20,20))) for j in range(4)]
  assert after==[[0]*5]+before[:3]
  rolls.append(dict(current=current,previous=previous,expected=[current]+previous[:2]))
queues=[]
for month,period,hour,minute in [(1,1,0,0),(2,1,0,0),(12,1,0,0),(1,2,0,0),(1,1,1,0),(1,1,0,1)]:
 u=machine();put(u,0xce60c,'<4i',month,period,hour,minute)
 # Preserve a preceding notification with the actual reserve function.
 for r,v in [(UC_MIPS_REG_A0,3),(UC_MIPS_REG_A1,7),(UC_MIPS_REG_A2,34),(UC_MIPS_REG_A3,1)]:u.reg_write(r,v)
 put(u,0x1f0010,'<i',0);u.emu_start(0x8003ecd8,0x80001000,count=30000)
 u.emu_start(0x8003ceac,0x8003cf44,count=100000)
 modes=[u.mem_read(0x137970+i*160+2,1)[0] for i in range(50) if u.mem_read(0x137970+i*160,1)[0]]
 expected=[1]+([2]+([3] if month==1 else []) if (period,hour,minute)==(1,0,0) else [])
 assert modes==expected
 queues.append(dict(month=month,period=period,hour=hour,minute=minute,modes=modes))
evaluations=[]
for count in [1,2,5,8,10]:
 for sales in [0,100000000,600000000,2147483647]:
  u=machine();put(u,0xcd930,'<I',500000)
  for i in range(10):
   a=0x12b2f8+i*5080;put(u,a,'<b',1);put(u,a+4,'<H',0 if i<count else 0x8000)
   put(u,a+0xd0c,'<i',sales if i<count else 123);put(u,a+0xcf8,'<i',17);put(u,a+0xc68,'<i',90 if i<count else 0)
  u.emu_start(0x8003f7fc,0x8003fe88,count=1000000)
  values=[get(u,0xe3ba8+i*4,'<i') for i in range(5)];parts=[get(u,0xe3bc0+i*4,'<i') for i in range(5)]
  assert values==[count,500000,min(2147483647,sales*count),6000,90],values
  evaluations.append(dict(count=count,sales=sales,visitors=500000,population=6000,rating=90,values=values,parts=parts,total=get(u,0xcd80c,'<i')))
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,additions=additions,rollovers=rolls,reservations=queues,evaluations=evaluations,original_excerpts=len(additions)+len(rolls)+len(queues)+len(evaluations),scope='Synthetic annual store/clock records; real memcpy/memset, reservation, population, assessment callees; stop before rare RNG or UI; not natural year-end/full operating equivalence'),separators=(',',':'))+'\n')
print('ANNUAL_SOURCE_PASS',len(additions),len(rolls),len(queues),len(evaluations))
