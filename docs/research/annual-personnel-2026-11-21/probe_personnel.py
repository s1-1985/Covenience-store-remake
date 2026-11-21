"""Original per-store wage and global 35-person age loops. No callee replacements."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import *
exe=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(exe).hexdigest();assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def put(u,a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def get(u,a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
def i32(v):return ((v+2147483648)&0xffffffff)-2147483648
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 for r,v in [(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
 return u
u=machine();put(u,0x1f0020,'<I',0x8012b2f8);u.emu_start(0x8001b194,0x8001b1a0,count=100)
percent=get(u,0x12b2f8+0x12dc,'<i');assert percent==3
wages=[]
for wage in [0,1,33,999,1000,65535,2147483647,-1]:
 for refs in [[-1,-1,-1],[0,-1,-1],[0,1,2],[2,0,-1]]:
  u=machine();put(u,0x1f0018,'<I',0x8012b2f8);put(u,0x12b2f8+0x12dc,'<i',percent);put(u,0x12b2f8+0xdd8,'<3h',*refs)
  before=[i32(wage+i) for i in range(3)]
  for i,v in enumerate(before):put(u,0x143ff8+i*60+12,'<i',v)
  u.emu_start(0x8002a0b0,0x8002a1b8,count=30000)
  after=[get(u,0x143ff8+i*60+12,'<i') for i in range(3)]
  expected=before.copy()
  for ref in refs:
   if ref>=0:
    v=i32(expected[ref]*(100+percent));expected[ref]=(abs(v)//100)*(-1 if v<0 else 1)
  assert after==expected,(before,refs,after,expected)
  wages.append(dict(before=before,assignments=refs,after=after))
ages=[]
for values in [[0]*35,[78]*35,[79]*35,[126]*35,[127]*35,([0,78,79,80,125,126,127]*5)]:
 for seed in [0,1,12345]:
  u=machine();put(u,0xce60c,'<ii',1,1);put(u,0xd6270,'<I',seed)
  originals=[]
  for i,age in enumerate(values):
   p=bytearray(60);p[3]=age;struct.pack_into('<H',p,0,0x8001 if i%2 else 0);p[0x18:0x23]=bytes([61,17,62,63,64,65,21,22,23,24,25]);u.mem_write(0x143ff8+i*60,bytes(p));originals.append(p)
  u.emu_start(0x8002a2f8,0x8002a47c,count=100000)
  state=seed;out=[]
  for i,age in enumerate(values):
   expected_age=min(127,age+1);boost=expected_age>=127
   if not boost and expected_age>=80:
    state=(state*1103515245+12345)&0xffffffff;boost=((state>>16)&32767)%5==0
   p=bytearray(u.mem_read(0x143ff8+i*60,60));expected=originals[i].copy();expected[3]=expected_age
   if boost:
    for k in [0x18,0x1a,0x1b,0x1c,0x1d]:expected[k]=100
   assert p==expected
   out.append(dict(age=p[3],boosted=boost))
  assert get(u,0xd6270,'<I')==state
  ages.append(dict(before=values,seed=seed,after=out,seed_after=state))
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,default_percent=percent,wages=wages,ages=ages,original_excerpts=1+len(wages)+len(ages),scope='Original init write, per-store three-slot wage loop, global35 age loop with real RNG; synthetic wages/ages, stop before later finance/UI; full year-start operating order unverified'),separators=(',',':'))+'\n')
print('ANNUAL_PERSONNEL_SOURCE_PASS',1,len(wages),len(ages))
