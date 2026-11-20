"""Bounded original 8001E660 calls with real 80041290 child; no stub."""
import hashlib,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3,UC_MIPS_REG_RA,UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_V0,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(exe).hexdigest()=="d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd"
rows=[]
for index,(name,bit) in enumerate([("tobacco",4),("alcohol",2),("medicine",1)]):
 for label,rect,points in [
  ("empty",[14,14,15,15],[]),
  ("single_corner",[14,14,15,15],[[15,15,bit]]),
  ("outside",[13,13,14,14],[[15,15,bit]]),
  ("top_left",[0,0,1,1],[[0,0,bit]]),
  ("bottom_right",[58,48,59,49],[[59,49,bit]]),
  ("other_bits",[14,14,15,15],[[15,15,7^bit]])]:
  u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN)
  u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
  for x,y,mask in points:u.mem_write(0x1398f5+y*480+x*8,bytes([mask]))
  for r,v in zip([UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3],rect):u.reg_write(r,v)
  for r,v in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
  u.mem_write(0x1f0010,struct.pack("<I",index))
  u.emu_start(0x8001e660,0x80001000,count=100000)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80001000
  expected=int(any(rect[0]<=x<=rect[2] and rect[1]<=y<=rect[3] and mask&bit for x,y,mask in points))
  actual=u.reg_read(UC_MIPS_REG_V0);assert actual==expected,(name,label,actual,expected)
  rows.append(dict(name=name+"_"+label,permit_id=name,rect=rect,points=points,restricted=bool(actual)))
fees=list(struct.unpack_from("<iii",exe,0xb92d0-0x10000+2048))
assert fees==[3000000,7000000,10000000]
Path(sys.argv[2]).write_text(json.dumps(dict(fees=fees,query_cases=rows,original_function_entries=len(rows),scope="rectangle query plus real all-zero child; no operating updates"),indent=2)+"\n")
print("Original permit query:",len(rows),"boundaries matched; fees:",fees)
