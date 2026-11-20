"""Original 8001CBC4 posting/refund; no controller or gameplay emulation."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_RA,UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
rows=[]
for company in [0,1]:
 for amount in [12000000,-12000000,-3000000,0]:
  u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
  def put(a,v):u.mem_write(a,struct.pack('<i',v))
  def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
  for i in range(2):put(0xcd9f8+i*4,200000000);put(0xd8f68+i*16,7)
  u.mem_write(0x12b2f8+4,struct.pack('<H',company<<15))
  for r,v in [(UC_MIPS_REG_A0,0x8012b2f8),(UC_MIPS_REG_A1,amount&0xffffffff),(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
  u.emu_start(0x8001cbc4,0x80001000,count=10000);assert u.reg_read(UC_MIPS_REG_PC)==0x80001000
  cash=[get(0xcd9f8+i*4) for i in range(2)];ledger=[get(0xd8f68+i*16) for i in range(2)]
  assert cash==[200000000-(amount if i==company else 0) for i in range(2)]
  assert ledger==[7+(amount if i==company else 0) for i in range(2)]
  rows.append(dict(company=company,amount=amount,cash=cash,ledger=ledger))
Path(sys.argv[2]).write_text(json.dumps(dict(cases=rows,original_function_entries=len(rows),scope='capital posting only; not original remodel controller or gameplay'),indent=2)+'\n')
print('Original capital postings:',len(rows),'matched')
