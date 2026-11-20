"""Real source excerpts for monthly reset, quote fee, funding and payment.
Run: PYTHONPATH=<unicorn> python probe_inspection.py EXE OUTPUT
Does not execute UI, land valuation, ownership migration or full gameplay.
"""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_FP,UC_MIPS_REG_SP
b=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(b).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,b[2048:]);u.reg_write(UC_MIPS_REG_FP,0x801f0000);u.reg_write(UC_MIPS_REG_SP,0x801f0000);return u
def put(u,a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
def get(u,a):return struct.unpack('<i',u.mem_read(a,4))[0]
resets=[];transactions=[];calls=0
for period in [1,2,4]:
 for hour in [0,1]:
  for subhour in [0,1]:
   u=machine();put(u,0xce610,period);put(u,0xce614,hour);put(u,0xce618,subhour)
   a=0x12b2f8+5080;put(u,0x1f0024,a|0x80000000);u.mem_write(a+2,b'\1');put(u,a+0xc68,37);put(u,a+0xc6c,61)
   cleared=(period,hour,subhour)==(1,0,0);stop=0x800235e4 if cleared else 0x80023670
   u.emu_start(0x8002359c,stop,count=1000);calls+=1;flag=u.mem_read(a+2,1)[0]
   assert flag==int(not cleared) and get(u,a+0xc68)==37 and get(u,a+0xc6c)==61
   resets.append(dict(period=period,hour=hour,subhour=subhour,flag_after=flag))
for flag,cashes in [(0,[499999,500000,500001]),(1,[0,1])]:
 for cash in cashes:
  u=machine();a=0x12b2f8+5080;put(u,0x1f0018,a|0x80000000);u.mem_write(a+2,bytes([flag]));u.mem_write(a+4,b'\0\x80');u.mem_write(0x12b2fc,b'\0\0')
  put(u,0xcd9f8,cash);put(u,0xcd9fc,9876543);put(u,0xd8f68,0);put(u,0xd8f78,0)
  u.emu_start(0x80060fbc,0x80060ff4,count=1000);calls+=1;fee=get(u,0xcd7fc);assert fee==(0 if flag==1 else 500000)
  put(u,0x1f0024,0);allowed=cash>=fee;stop=0x8006111c if allowed else 0x80061154
  u.emu_start(0x800610e4,stop,count=1000);calls+=1
  if allowed:u.emu_start(0x80061184,0x800611c0,count=10000);calls+=1
  paid=fee if allowed and flag==0 else 0
  assert get(u,0xcd9f8)==cash-paid and get(u,0xcd9fc)==9876543
  assert get(u,0xd8f68)==paid and get(u,0xd8f78)==0
  after=u.mem_read(a+2,1)[0];assert after==(1 if allowed else flag)
  transactions.append(dict(flag_before=flag,cash_before=cash,fee=fee,allowed=allowed,paid=paid,cash_after=cash-paid,flag_after=after))
Path(sys.argv[2]).write_text(json.dumps(dict(resets=resets,transactions=transactions,original_excerpt_calls=calls,scope='12 monthly flag gates + 5 fee + 5 funding + 4 real payment excerpts; no UI/acquisition/operating update'),indent=2)+'\n')
print('INSPECTION_SOURCE_PASS',calls,'original excerpts')
