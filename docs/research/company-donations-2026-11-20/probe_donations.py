"""Source donation gates, active/owner masks and real company payment child.
No rendering or notification execution. Normal first record is player owned.
Usage: PYTHONPATH=<unicorn-dir> python3 probe_donations.py EXE OUTPUT
"""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_FP,UC_MIPS_REG_SP,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
cases=[]
stores=[(1,0,20),(0,0,30),(1,1,40),(0,1,50),(1,0,99),(1,1,99),(1,0,100),(1,1,100),(0,0,100),(0,1,100)]
for company in [0,1]:
 for cash in [1499999999,1500000000,1500000001,1600000000,2000000000,2147483647]:
  for period,hour in [(1,0),(2,0),(1,1)]:
   u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
   def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
   def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
   for i,(active,owner,pop) in enumerate(stores):
    a=0x12b2f8+i*5080;u.mem_write(a,bytes([active]));u.mem_write(a+4,struct.pack('<H',owner<<15));put(a+0xc68,pop);put(a+0xc6c,17)
   put(0xce610,period);put(0xce614,hour);put(0xcd9f8+4*company,cash);put(0xcd9f8+4*(1-company),0)
   put(0xd8f68,0);put(0xd8f78,0)
   u.reg_write(UC_MIPS_REG_FP,0x801f0000);u.reg_write(UC_MIPS_REG_SP,0x801f0000)
   fired=period==1 and hour==0 and cash>1500000000
   start=0x80027c80 if company==0 or period!=1 or hour!=0 else 0x80027ee8
   stop=0x80027e80 if fired and company==0 else 0x800280bc
   u.emu_start(start,stop,count=100000)
   assert u.reg_read(UC_MIPS_REG_PC) in [stop,stop-4]
   amount=cash-1000000000 if fired else 0
   assert get(0xcd9f8+4*company)==cash-amount and get(0xcd9f8+4*(1-company))==0
   assert get(0xd8f68+16*company)==amount and get(0xd8f68+16*(1-company))==0
   ratings=[get(0x12b2f8+i*5080+0xc68) for i in range(10)]
   assert ratings==[min(100,pop+5) if fired and active and owner==company else pop for active,owner,pop in stores]
   assert all(get(0x12b2f8+i*5080+0xc6c)==17 for i in range(10))
   cases.append(dict(company=company,cash_before=cash,period=period,hour=hour,fired=fired,paid=amount,cash_after=cash-amount,ratings=ratings))
Path(sys.argv[2]).write_text(json.dumps(dict(stores=[dict(active=a,company=c,rating=p) for a,c,p in stores],cases=cases,scope='36 partial original executions, real payment child, stop before player text/notification; normal first-slot owner0'),indent=2)+'\n')
print('DONATION_SOURCE_PASS',len(cases),'cash/time/owner conditions')
