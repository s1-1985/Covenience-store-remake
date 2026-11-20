"""Run original mutable fire scan and all20-customer cleanup excerpts.
Usage: python probe_fire.py EXE OUT.json. Requires Unicorn2.1.4, research only.
Does not execute incident eligibility, popup or a full operating update.
"""
from pathlib import Path
import hashlib,json,struct,sys
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_PC
b=Path(sys.argv[1]).read_bytes();sha=hashlib.sha256(b).hexdigest();assert sha=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
rows=[list(struct.unpack_from('<49i',b,0x80099f0c-0x80010000+2048+i*196)) for i in range(53)]
W,H=28,26;STORE=0x12b2f8

def digest_grid(g):return hashlib.sha256(b''.join(struct.pack('<I',v&0xffffffff) for row in g for v in row)).hexdigest()
def inputs(kind,rotation):
 floors=[[([0,5,10,15,16,28,255,34][(x+y*3)%8]) for x in range(14)] for y in range(13)]
 grid=[[0]*W for y in range(H)]
 for y in range(H):grid[y][13]=1
 grid[20][24]=0x80000000|(53<<12)
 if kind>=0:
  w,h=rows[kind][9:11]
  if rotation>=2:w,h=h,w
  for y in range(2,2+h*2):
   for x in range(2,2+w*2):grid[y][x]=1
  grid[2][2]=0x80000000|(kind<<12)|(rotation<<22)
 for x,y in [(0,0),(27,25),(5,5)]:
  if grid[y][x]==0:grid[y][x]=650<<12
 return floors,grid

def run(kind,rotation,seed):
 floors,grid=inputs(kind,rotation);u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,b[2048:])
 def put(a,fmt,*v):u.mem_write(a,struct.pack(fmt,*v))
 def get(a,fmt):return struct.unpack(fmt,u.mem_read(a,struct.calcsize(fmt)))[0]
 u.reg_write(UC_MIPS_REG_SP,0x801f0000);u.reg_write(UC_MIPS_REG_FP,0x801f0000)
 for off,v in [(0x58,W),(0x5c,H),(0x70,STORE|0x80000000)]:put(0x1f0000+off,'<I',v)
 for y,row in enumerate(floors):u.mem_write(STORE+0x50+y*14,bytes(row))
 for y,row in enumerate(grid):u.mem_write(STORE+0x108+y*112,b''.join(struct.pack('<I',v) for v in row))
 put(0xd6270,'<I',seed);calls=[]
 u.hook_add(UC_HOOK_CODE,lambda *args:calls.append(1),begin=0x8007e648,end=0x8007e648)
 u.emu_start(0x8003c628,0x8003cb78,count=1000000);assert u.reg_read(UC_MIPS_REG_PC)==0x8003cb78
 after=[[get(STORE+0x108+y*112+x*4,'<I') for x in range(W)] for y in range(H)]
 out=dict(kind=kind,rotation=rotation,seed=seed,seed_after=get(0xd6270,'<I'),floor_writes=len(calls),floor_after=[list(u.mem_read(STORE+0x50+y*14,14)) for y in range(13)],grid_after_sha256=digest_grid(after),burned=kind>=0 and after[2][2]==0)
 # All20 records have distinct persistent payload, including unpaid cart.
 before=[]
 for i in range(20):
  p=bytearray(range(32));p[0]=1 if i==0 else (5 if i==1 else (4 if i==19 else 0))
  p[12:14]=struct.pack('<bb',*( (0,0) if i==0 else ((27,25) if i==1 else ((5,5) if i==19 else (-1,-1)))))
  before.append(bytes(p));u.mem_write(STORE+0xf04+i*32,bytes(p))
 u.emu_start(0x8003cb78,0x8003cd0c,count=100000);assert u.reg_read(UC_MIPS_REG_PC)==0x8003cd0c
 for i,p in enumerate(before):
  expected=bytearray(p);expected[0]=0
  assert bytes(u.mem_read(STORE+0xf04+i*32,32))==bytes(expected)
 out['grid_after_customers_sha256']=digest_grid([[get(STORE+0x108+y*112+x*4,'<I') for x in range(W)] for y in range(H)])
 out['customer_payload_retained']=True
 return out
cases=[run(-1,0,0)]+[run(k,r,1+k*4+r) for k in range(53) for r in range(4)]
Path(sys.argv[2]).write_text(json.dumps(dict(exe_sha256=sha,width=W,height=H,customer_positions=[[0,0],[27,25],[5,5]],cases=cases,original_excerpt_calls=len(cases)*2,scope='213 mutable scans + 213 all20 customer cleanup excerpts; synthetic mixed floors, actors and wall marker; real RNG; no UI/eligibility/operating loop',callee_replacements=0),separators=(',',':'))+'\n')
print('FIRE_SOURCE_PASS',len(cases),'scan cases and',len(cases),'all20 customer cleanups')
