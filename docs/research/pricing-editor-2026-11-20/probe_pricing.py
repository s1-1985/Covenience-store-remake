"""Original group-step excerpts. Boundaries stop before the error/UI call."""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_FP,UC_MIPS_REG_SP,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
rows=[]
cases=[('raise',[50]*26,1),('lower',[50]*26,-1),('upper_last',[40]*25+[100],1),('lower_middle',[40]*13+[0]+[40]*12,-1),('reach_upper',[99]*26,1),('reach_lower',[1]*26,-1),('mixed_up',list(range(26)),1),('mixed_down',list(range(1,27)),-1)]
for name,values,d in cases:
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 def put(a,v):u.mem_write(a,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<i',u.mem_read(a,4))[0]
 for i,v in enumerate(values+[77]):put(0x12b2f8+0xc7c+i*4,v)
 put(0x1f0048,0x8012b2f8);put(0x1f0018,0);put(0xcda0c,0x2000 if d==1 else 0x8000)
 u.mem_write(0xcd83c,b'\0\0');u.reg_write(UC_MIPS_REG_FP,0x801f0000);u.reg_write(UC_MIPS_REG_SP,0x801f0000)
 allowed=all(0<=v+d<=100 for v in values)
 start=0x80063208 if d==1 else 0x80063448
 stop=(0x80063448 if d==1 else 0x80063688) if allowed else (0x8006328c if d==1 else 0x800634cc)
 u.emu_start(start,stop,count=1000000);assert u.reg_read(UC_MIPS_REG_PC) in [stop,stop-4],(name,hex(u.reg_read(UC_MIPS_REG_PC)),hex(stop))
 result=[get(0x12b2f8+0xc7c+i*4) for i in range(26)]
 assert result==[v+d if allowed else v for v in values]
 assert get(0x12b2f8+0xc7c+26*4)==77
 if allowed:assert struct.unpack('<h',u.mem_read(0xcd83c,2))[0]==sum(result)//26
 rows.append(dict(name=name,values=values,delta=d,allowed=allowed,after=result))
products=[]
for i in range(26):
 base,cost,default=struct.unpack_from('<iii',exe,0x9cdf0-0x10000+2048+i*88+24)
 products.append(dict(index=i,base=base,cost=cost,default=default,units=[base*(cost+v)//100 for v in [0,default,100]]))
Path(sys.argv[2]).write_text(json.dumps(dict(group_cases=rows,products=products,original_excerpt_entries=len(rows),scope='group-step excerpts only; limit paths stop before error/UI; product expectations derived from original table and recovered formula'),indent=2)+'\n')
print('Original pricing: eight group boundaries matched; 26 source product rows')
