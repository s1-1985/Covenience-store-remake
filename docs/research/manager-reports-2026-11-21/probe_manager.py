"""Original MIPS selection, acquisition-parent and rival/clear excerpts; not APK code."""
from pathlib import Path
import hashlib,json,struct,sys,random
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import *
exe=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(exe).hexdigest()
assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
repo=Path(__file__).resolve().parents[3];data=json.loads((repo/'game/data/ps1_integration.json').read_text())
STORE=0x12b2f8;FRAME=0x1f0000;SUMMARY=0x160000;PERSON=0x170000;STOP=0x80001000

def put(u,a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def get(u,a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 for r,v in [(UC_MIPS_REG_SP,FRAME|0x80000000),(UC_MIPS_REG_FP,FRAME|0x80000000),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 put(u,FRAME+0x48,'<I',STORE|0x80000000);put(u,0xcd8ec,'<I',0);put(u,0xcecec,'<I',SUMMARY|0x80000000)
 return u
rows=[];rng=random.Random(84)
cases=[([0]*27,[0]*27),([200]*27,[1]*27),([0,200,200]+[0]*24,[0,2,2]+[0]*24),([0xffffffff,0x80000000]+[0]*25,[1,1]+[0]*25)]
for _ in range(40):cases.append(([rng.choice([0,5,6,199,200,500,0xffffffff]) for i in range(27)],[rng.choice([0,0,1,40]) for i in range(27)]))
for counts,stock in cases:
 u=machine()
 for i in range(27):put(u,STORE+0x11a0+i*12,'<I',counts[i]);put(u,SUMMARY+0x2c+i*4,'<i',stock[i])
 u.emu_start(0x8003ba40,0x8003bc88,count=100000);assert u.reg_read(UC_MIPS_REG_PC)==0x8003bc88
 best=get(u,FRAME+0x28,'<I');worst=get(u,FRAME+0x24,'<I')
 expected=max(range(27),key=lambda i:counts[i]);available=[i for i in range(27) if stock[i]>0]
 assert best==expected and worst==(min(available,key=lambda i:counts[i]) if available else 27)
 rows.append(dict(counts=counts,stock=stock,best=best,worst=worst))
# Normal pickup counts heads immediately, before checkout; failure skips write.
f=next(f for f in data['layouts'][1]['fixtures'] if f['source_kind']==0);category=data['product_ids'].index('retort_food')
image=struct.unpack_from('<i',exe,2048+0x8009cdf0-0x80010000+category*88+44)[0]
anchor=STORE+0x108+2*112+2*4;acquisitions=[]
for stock,heads,before in [(40,3,0),(40,5,0xfffffffe),(2,3,7),(0,1,5)]:
 u=machine();put(u,STORE+4,'<H',1);put(u,STORE+68,'<ii',20,20)
 put(u,anchor,'<I',f['source_word']);put(u,anchor+112,'<I',(f['source_stock_word']&0xc00fff)|(image<<12)|(stock<<24))
 p=bytearray(32);p[1]=category;p[12:15]=bytes([2,3,0]);p[30]=heads;u.mem_write(PERSON,bytes(p))
 put(u,FRAME+0x40,'<I',STORE|0x80000000);put(u,FRAME+0x44,'<I',PERSON|0x80000000);put(u,STORE+0x11a0+category*12,'<I',before)
 def stop_failed(uc,address,size,userdata):
  if address==0x80034b88:uc.emu_stop()
 u.hook_add(UC_HOOK_CODE,stop_failed);u.emu_start(0x800349d0,0x80034a5c,count=100000)
 after=get(u,STORE+0x11a0+category*12,'<I');assert after==((before+heads)&0xffffffff if stock>=heads else before)
 acquisitions.append(dict(stock=stock,heads=heads,before=before,after=after,failed=stock<heads))
u=machine();put(u,STORE+4,'<H',0x8000);put(u,0xd6270,'<I',12345);put(u,STORE+0x12e2,'<b',100)
u.reg_write(UC_MIPS_REG_A0,STORE|0x80000000);u.emu_start(0x8003b570,STOP,count=10000)
assert u.reg_read(UC_MIPS_REG_PC)==STOP and get(u,0xd6270,'<I')==12345 and get(u,STORE+0x12e2,'<b')==100
u=machine()
for i in range(27):put(u,STORE+0x1198+i*12,'<III',17,23,99)
for i in range(4):put(u,STORE+0x12e1+i,'<b',50)
u.emu_start(0x8003be78,0x8003bf10,count=10000)
assert all(get(u,STORE+0x11a0+i*12,'<I')==0 and get(u,STORE+0x1198+i*12,'<I')==17 and get(u,STORE+0x119c+i*12,'<I')==23 for i in range(27))
assert bytes(u.mem_read(STORE+0x12e1,4))==bytes(4)
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,selections=rows,acquisitions=acquisitions,rival_guard=True,clear_separate_survey=True,original_excerpts=len(rows)+len(acquisitions)+2,scope='Selection and parent pickup excerpts, full rival early return, counter-clear excerpt; no UI helpers replaced; not full operating-loop or notification reproduction'),separators=(',',':'))+'\n')
print('MANAGER_SOURCE_PASS',len(rows),'selections;',len(acquisitions),'parent pickups; rival guard and separate clear')
