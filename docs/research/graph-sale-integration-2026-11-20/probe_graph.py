"""Additional bounded MIPS scale checks; original text renderer not entered.
PYTHONPATH=<unicorn2.1.4> python probe_graph.py EXE OUTPUT.json
Reuses 20261119 analyze-graphs.py machine setup and scale boundary.
"""
import hashlib,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN
from unicorn.mips_const import UC_MIPS_REG_A0,UC_MIPS_REG_RA,UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_PC
exe=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(exe).hexdigest()=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
M=-2147483648
cases=[('negative_average_truncation',[-999999],[-6000001],[3]),('zero_count_stops',[20,90000000],[20,90000000],[1,0]),('chain_sentinel_stops',[20,90000000],[20,M],[1,1]),('all_sixty_valid',list(range(60)),list(range(60)),[1]*60),('negative_million_rounding',[-1000001],[0],[1])]
rows=[]
for name,h,t,c in cases:
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:])
 def put(a,v):u.mem_write(a&0x1fffffff,struct.pack('<I',v&0xffffffff))
 def get(a):return struct.unpack('<i',u.mem_read(a&0x1fffffff,4))[0]
 for i in range(60):put(0x8012b2f8+0x12e8+4*i,M);put(0x800e3c28+4*i,M)
 for i,v in enumerate(h):put(0x8012b2f8+0x12e8+4*i,v)
 for i,v in enumerate(t):put(0x800e3c28+4*i,v)
 u.mem_write(0xe43d0,bytes(c))
 for r,v in [(UC_MIPS_REG_A0,0x8012b2f8),(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,0x80001000)]:u.reg_write(r,v)
 u.emu_start(0x80048728,0x80048a60,count=12000000)
 assert u.reg_read(UC_MIPS_REG_PC) in [0x80048a60,0x80048a5c]
 values=[];means=[]
 for a,b,n in zip(h,t,c):
  if a==M or b==M or n<=0:break
  values.append(a);means.append((-1 if b<0 else 1)*(abs(b)//n))
 maximum=max([1]+[abs(v) for v in values+means]);axis=max(1000000,((maximum+999999)//1000000)*1000000)
 observed=get(0x800e4000)*10000
 assert observed==axis and [get(0x800d6018+4*i) for i in range(len(values))]==means
 rows.append({'name':name,'history':h,'chain':t,'counts':c,'model':{'valid':len(values),'averages':means,'axis_yen':axis,'oldest_first':list(reversed(values))},'original_axis_yen':observed})
Path(sys.argv[2]).write_text(json.dumps({'original_function_entries':len(rows),'operating_updates':0,'scope':'scale only, stop before text rendering; no gameplay callee replacement','scale_cases':rows},indent=2)+'\n')
print('Original scale:',len(rows),'additional boundaries matched')
