"""Original 8001DE5C mode1; six valid selected tiers, no child stub."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_RA,UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_V0,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(exe).hexdigest()=="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
rows=[]
for tier in range(6):
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:]);u.mem_write(0x12b2f8+0xc70,struct.pack('<i',tier))
 for r,v in [(UC_MIPS_REG_A0,0x8012b2f8),(UC_MIPS_REG_A1,1),(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
 u.emu_start(0x8001de5c,0x80001000,count=10000)
 assert u.reg_read(UC_MIPS_REG_PC)==0x80001000
 fee=u.reg_read(UC_MIPS_REG_V0);assert fee==(tier//2+1)*6000000
 rows.append(dict(selected_tier=tier,fee_yen=fee))
Path(sys.argv[2]).write_text(json.dumps(dict(cases=rows,original_function_entries=6,scope='mode1 cost only; no chooser/interior/controller execution'),indent=2)+'\n')
print('Original size fee: six tiers matched')
