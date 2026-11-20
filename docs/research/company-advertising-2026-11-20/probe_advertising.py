"""Original player cash gate and payment; no text/notification emulation."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_FP,UC_MIPS_REG_SP,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
rows=[];masters=[]
for i in range(5):
 cost,parameter,gain,period,hour=struct.unpack_from('<iiiii',exe,0x9fe40-0x10000+2048+i*44+24)
 masters.append(dict(index=i,cost_yen=cost,parameter=parameter,gain=gain,period=period,hour=hour))
 for enough in [False,True]:
  cash=cost*5-(0 if enough else 1)
  u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
  def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
  def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
  put(0xcd9f8,cash);put(0xd8f68,0);put(0x1f001c,i);put(0x1f0040,0)
  u.mem_write(0x12b2fc,b'\0\0');u.mem_write(0xe3688+i,b'\1')
  u.reg_write(UC_MIPS_REG_FP,0x801f0000);u.reg_write(UC_MIPS_REG_SP,0x801f0000)
  stop=0x80027918 if enough else 0x800279c0
  u.emu_start(0x8002784c,stop,count=100000)
  assert u.reg_read(UC_MIPS_REG_PC) in [stop,stop-4]
  flag=u.mem_read(0xe3688+i,1)[0];paid=get(0xd8f68);growth=get(0x1f0040)
  assert flag==int(enough) and paid==(cost if enough else 0) and growth==(gain if enough else 0)
  assert get(0xcd9f8)==cash-paid
  rows.append(dict(index=i,cash_before=cash,fired=enough,cash_after=get(0xcd9f8),paid=paid,gain=growth,flag=flag))
Path(sys.argv[2]).write_text(json.dumps(dict(masters=masters,cases=rows,original_excerpt_entries=len(rows),scope='cash gate, accumulator, real company-payment child; stop before text/notice; no full hourly/controller update'),indent=2)+'\n')
print('Original advertising:',len(rows),'cash boundaries matched')
