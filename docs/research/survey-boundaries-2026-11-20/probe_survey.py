"""Bounded original MIPS read-side checks; EXE is an analysis input only.
Reuses the documented machine setup from c4226df's analyze-festival-state.py.
Unicorn 2.1.4. Only 8004E494 (text renderer) is captured/replaced.
Usage: PYTHONPATH=/tmp/conveni-uc python probe_survey.py EXE OUTPUT.json
"""
import hashlib,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_GP,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
S=0x12b2f8;STOP=0x80001000
inputs=[]
a=[0]*27;a[26]=0xffffffff;inputs.append(('last_product_unsigned_max',a,[0]*27))
inputs.append(('all_max_ties',[0xffffffff]*27,[0x80000000]*27))
inputs.append(('signed_boundary_order',[0x7fffffff,0x80000000,0xffffffff]+[0]*24,[0xffffffff,0x80000000,0x7fffffff]+[0]*24))
inputs.append(('zero_columns_third_counter_max',[0]*27,[0]*27))
a=[0]*27;a[0]=1;a[26]=1;inputs.append(('first_last_equal',a,list(reversed(a))))
rows=[]
for name,left,right in inputs:
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 u.reg_write(UC_MIPS_REG_GP,0x800cd6c4)
 for i,(a,b) in enumerate(zip(left,right)):u.mem_write(S+0x1198+12*i,struct.pack('<III',a,b,0xffffffff))
 before=bytes(u.mem_read(S,5080));calls=[]
 def hook(cpu,pc,size,user):
  if pc==0x8004e494:
   d={'x':cpu.reg_read(UC_MIPS_REG_A0),'y':cpu.reg_read(UC_MIPS_REG_A1),'message':cpu.reg_read(UC_MIPS_REG_A2)}
   if d['message']==369:d['value_u32']=struct.unpack('<I',cpu.mem_read(0xcd938,4))[0]
   calls.append(d);cpu.reg_write(UC_MIPS_REG_PC,cpu.reg_read(UC_MIPS_REG_RA))
 u.hook_add(UC_HOOK_CODE,hook)
 for register,value in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,STOP),(UC_MIPS_REG_A0,S+0x80000000)]:u.reg_write(register,value)
 u.emu_start(0x800470e4,STOP,count=3000000)
 assert u.reg_read(UC_MIPS_REG_PC)==STOP
 assert bytes(u.mem_read(S,5080))==before
 expected=[]
 for col,values in enumerate([left,right]):
  chosen=sorted(range(27),key=lambda i:(-values[i],i))[:8]
  expected += [{'x':32+132*col,'y':80+16*row,'message':71+i} for row,i in enumerate(chosen) if values[i]]
  expected += [{'x':120+132*col,'y':80+16*row,'message':369,'value_u32':values[i]} for row,i in enumerate(chosen) if values[i]]
 assert calls==expected,(name,calls,expected)
 rows.append({'case':name,'left_u32':left,'right_u32':right,'captured_text_calls':calls,'store_record_unchanged':True})
result={'source_leaf':'0x800470e4','exe_sha256':hashlib.sha256(exe).hexdigest(),'original_function_entries':len(rows),'text_renderer_replacements_per_case':1,'operating_updates':0,'cases':rows}
Path(sys.argv[2]).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Original MIPS survey:',len(rows),'boundary cases matched; store records unchanged; no gameplay updates')
