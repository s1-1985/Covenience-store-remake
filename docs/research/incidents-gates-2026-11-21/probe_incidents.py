"""Bounded original incident finance gates, asset comparison, 2 RNG calls,
and the common post-incident tail. No UI stubs or full fire execution.
Usage: python probe_incidents.py EXE OUTPUT.json (Unicorn2.1.4).
"""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_V0,UC_MIPS_REG_S0
b=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
STORE=0x12b2f8;STAFF=0x143ff8;STOP=0x80001000

def put(u,a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def get(u,a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,b[2048:])
 for r,v in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 put(u,0xcd8ec,'<I',0);put(u,0xcecec,'<I',0x80170000)
 return u
def financial(v):
 u=machine();rival,security,pop,heads,last,sales=v
 put(u,STORE+4,'<H',32768 if rival else 1);put(u,0x170008,'<i',security);put(u,STORE+0xc6c,'<i',pop)
 put(u,STORE+0x1188,'<I',heads&0xffffffff);put(u,STORE+0xd5c,'<I',last&0xffffffff);put(u,STORE+0xd98,'<I',sales&0xffffffff)
 put(u,0xd6270,'<I',2468);u.reg_write(UC_MIPS_REG_A0,STORE|0x80000000)
 hit=[]
 def stop(u,a,n,_):
  if a==0x8003c078:hit.append(True);u.emu_stop()
 u.hook_add(UC_HOOK_CODE,stop);u.emu_start(0x8003bf28,STOP,count=10000)
 assert get(u,0xd6270,'<I')==2468
 return dict(rival=rival,security=security,popularity=pop,heads=heads,last_sales=last,sales=sales,allowed=bool(hit),seed_after=2468)
base=[False,50,60,2000,1000000,100000];gates=[financial(base)]
for i,values in [(0,[True]),(1,[60,61]),(3,[1999,0,-1,4294967295]),(4,[999999,1000000,2147483648]),(5,[99999,100000,2147483648])]:
 for value in values:
  v=base[:];v[i]=value;gates.append(financial(v))
assets=[]
for value in [0,99999,100000,2147483647,2147483648,4294967295]:
 u=machine();u.reg_write(UC_MIPS_REG_S0,value);u.reg_write(UC_MIPS_REG_V0,0)
 hit=[]
 def stop(u,a,n,_):
  if a==0x8003c0bc:hit.append(True);u.emu_stop()
 u.hook_add(UC_HOOK_CODE,stop);u.emu_start(0x8003c094,STOP,count=10000)
 assets.append(dict(value=value,allowed=bool(hit)))

def rand(seed):
 seed=(seed*1103515245+12345)&0xffffffff;return seed,(seed>>16)&32767
# Find all four hit combinations in the actual shared LCG.
seeds={}
for seed in range(1000000):
 s,a=rand(seed);s,c=rand(s);key=(a%128==100,c%256==100)
 seeds.setdefault(key,seed)
 if len(seeds)==4:break
assert len(seeds)==4
chances=[]
for (robbery,fire),seed in seeds.items():
 u=machine();put(u,0xd6270,'<I',seed);u.emu_start(0x8003c0bc,0x8003c138,count=10000)
 kind=get(u,0x1f0018,'<i');expected=1 if fire else (0 if robbery else -1)
 assert kind==expected
 s,_=rand(seed);s,_=rand(s);assert get(u,0xd6270,'<I')==s
 chances.append(dict(seed=seed,robbery=robbery,fire=fire,kind=kind,seed_after=s))
tails=[]
for slots in [(0,1,2),(0,-1,2),(-1,-1,-1)]:
 u=machine();put(u,0x1f0070,'<I',STORE|0x80000000);put(u,STORE+0xdd8,'<3h',*slots)
 put(u,STORE+0xc68,'<i',42);put(u,STORE+0xc6c,'<i',99);put(u,STORE+1,'<b',1)
 before=[]
 for i in range(3):
  p=bytearray(range(60));p[25]=70+i;p[40]=2+i;u.mem_write(STAFF+i*60,bytes(p));before.append(bytes(p))
 u.emu_start(0x8003cdc0,0x8003ce90,count=10000)
 energies=[]
 for i in range(3):
  a=bytes(u.mem_read(STAFF+i*60,60));expected=bytearray(before[i])
  if i in slots:expected[25]=0
  assert a==bytes(expected);energies.append(a[25])
 assert get(u,STORE+0xc68,'<i')==42 and get(u,STORE+0xc6c,'<i')==5 and get(u,STORE+1,'<b')==0
 tails.append(dict(slots=slots,energy_after=energies,rating_after=42,popularity_after=5,other_person_bytes_unchanged=True))
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,financial=gates,assets=assets,chances=chances,tails=tails,original_excerpt_calls=len(gates)+len(assets)+len(chances)+len(tails),scope='Original bounded finance/asset/chance/common-tail excerpts. Asset valuation callees and popup/fire not executed.',callee_replacements=0),separators=(',',':'))+'\n')
print('INCIDENT_SOURCE_PASS',len(gates)+len(assets)+len(chances)+len(tails),'original excerpts')
