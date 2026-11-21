"""Original RNG/selection and actual rival company payment excerpts, no callee stubs."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import *
exe=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(exe).hexdigest()
assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def put(u,a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
def get(u,a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 for r,v in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
 return u
selection=[]
for control in [-1,0,1,2,3]:
 for cash in [999999,1000000,4999999,5000000,9999999,10000000,29999999,30000000,49999999,50000000]:
  for seed in [0,1,12345,99999]:
   u=machine();put(u,0xcd8a8,'<b',control);put(u,0xcd9fc,'<i',cash);put(u,0xce610,'<i',1);put(u,0xd6270,'<I',seed);u.mem_write(0xe368d,b'\1'*5)
   u.emu_start(0x800275f8,0x80027770,count=10000)
   after=(seed*1103515245+12345)&0xffffffff;roll=((after>>16)&32767)%4
   costs=[100000,500000,1000000,3000000,5000000]
   enabled=[i for i in range(5) if u.mem_read(0xe368d+i,1)[0]]
   expected=[max(i for i,c in enumerate(costs) if cash>=10*c)] if roll<=control and cash>=1000000 else []
   assert enabled==expected and get(u,0xd6270,'<I')==after and get(u,0xcd9fc,'<i')==cash
   selection.append(dict(control=control,cash=cash,seed=seed,enabled=enabled,seed_after=after))
gates=[]
for period,hour,minute in [(1,0,1),(1,1,0),(2,0,0)]:
 u=machine();put(u,0xce610,'<iii',period,hour,minute);put(u,0xd6270,'<I',7);u.mem_write(0xe368d,b'\1'*5)
 u.emu_start(0x800275f8,0x80027770 if minute==0 else 0x80029008,count=10000)
 assert get(u,0xd6270,'<I')==7 and bytes(u.mem_read(0xe368d,5))==b'\1'*5
 gates.append(dict(period=period,hour=hour,minute=minute))
payments=[]
for index,cost in enumerate(costs):
 for slots in [[],[0],[2,7]]:
  for cash in [0,cost*10]:
   u=machine();put(u,0x1f001c,'<i',index);put(u,0x1f0044,'<i',0);put(u,0xcd9fc,'<i',cash);put(u,0xcd9f8,'<i',123456789);u.mem_write(0xe368d+index,b'\1')
   for slot in slots:put(u,0x12b2f8+slot*5080,'<b',1);put(u,0x12b2fc+slot*5080,'<H',0x8000)
   # Active owned shop before the rival must not receive its expense.
   if 0 not in slots:put(u,0x12b2f8,'<b',1);put(u,0x12b2fc,'<H',0)
   def stop(uc,address,size,data):
    if address in [0x80027bc8,0x80027c64]:uc.emu_stop()
   u.hook_add(UC_HOOK_CODE,stop);u.emu_start(0x80027a5c,0x80027c68,count=10000)
   gain=get(u,0x1f0044,'<i');paid=cost if slots else 0
   assert get(u,0xcd9fc,'<i')==cash-paid and get(u,0xcd9f8,'<i')==123456789
   assert get(u,0xd8f78,'<i')==paid and gain==[12,20,40,60,90][index]
   payments.append(dict(index=index,slots=slots,cash_before=cash,cash_after=cash-paid,paid=paid,gain=gain))
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,selection=selection,gates=gates,payments=payments,original_excerpts=len(selection)+len(gates)+len(payments),scope='Original selection with real RNG; payment search with real company callee; stop before text/UI. Synthetic time/store inputs; no full operating-loop equivalence.'),separators=(',',':'))+'\n')
print('RIVAL_ADVERTISING_SOURCE_PASS',len(selection),len(gates),len(payments))
