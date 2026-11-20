"""Small real original excerpts: arrival quotient, display aggregate, parent OR.
Usage: PYTHONPATH=<unicorn> python probe_calendar.py EXE FIXTURE
No substituted game calls, renderer, audio or full operating trajectory.
"""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_FP,UC_MIPS_REG_SP,UC_MIPS_REG_PC
b=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(b).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,b[2048:]);u.reg_write(UC_MIPS_REG_FP,0x801f0000);u.reg_write(UC_MIPS_REG_SP,0x801f0000);return u
def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(u,a):return struct.unpack('<I',u.mem_read(a,4))[0]
arrivals=[]
for old,heads,pending in [(0,3,0),(9997,3,0),(9999,3,0),(10000,3,1),(9999,20003,1),(29999,3,1),(4294967294,3,17),(9999,1,4294967295)]:
 u=machine();put(u,0xcd930,old);put(u,0xcd8b8,pending);put(u,0x1f002c,heads);u.emu_start(0x800325e0,0x80032678,count=10000)
 total=(old+heads)&0xffffffff;new=total//10000 if total//10000>old//10000 else pending
 assert get(u,0xcd930)==total and get(u,0xcd8b8)==new
 arrivals.append(dict(before=old,heads=heads,pending_before=pending,total=total,pending_after=new))
stores=[dict(active=int(i%4 in [0,1]),owner=int(i%4 in [1,3]),popularity=20+i,rating=17+i) for i in range(10)]
u=machine()
for i,s in enumerate(stores):
 a=0x12b2f8+5080*i;u.mem_write(a,bytes([s['active']]));u.mem_write(a+4,struct.pack('<H',s['owner']<<15));put(u,a+0xc6c,s['popularity']);put(u,a+0xc68,s['rating'])
u.emu_start(0x80029524,0x800295dc,count=10000)
for i,s in enumerate(stores):
 s['after']=get(u,0x12b2f8+5080*i+0xc6c);assert s['after']==(100 if s['active'] or s['owner']==0 else s['popularity']);assert get(u,0x12b2f8+5080*i+0xc68)==s['rating']
displays=[]
for counts in [[9999,0,80000,50000],[9999,3,80000,50000],[30000,20000,0,0],[4294967295,2,80000,50000],[4294967295,0,80000,50000]]:
 u=machine();put(u,0x1f00b0,4);put(u,0xcd938,0x12345678)
 for i,n in enumerate(counts):
  put(u,0x1f0088+i*4,i);a=0x12b2f8+5080*i;u.mem_write(a,bytes([int(i!=3)]));u.mem_write(a+4,struct.pack('<H',int(i==2)<<15));put(u,a+0x1188,n)
 total=(counts[0]+counts[1])&0xffffffff;stop=0x80052f58 if total>=10000 else 0x800532cc
 u.emu_start(0x80052df4,stop,count=10000);shown=total>=10000;units=get(u,0xcd938)
 assert get(u,0x1f00b8)==total and units==(total//10000 if shown else 0x12345678)
 displays.append(dict(counts=counts,active=[1,1,1,0],owners=[0,0,1,0],total=total,shown=shown,units=total//10000 if shown else 0))
Path(sys.argv[2]).write_text(json.dumps(dict(arrivals=arrivals,popularity=stores,displays=displays,original_excerpt_calls=14,scope='8 counter + 1 ten-slot OR write + 5 display summations; source excerpts, no rendering/audio/full update'),indent=2)+'\n')
print('CALENDAR_SOURCE_PASS 14 original excerpts')
