"""Reproduce 80070F48 with original native callees. Usage: python probe_staff_lifecycle.py EXE OUTDIR. Requires Unicorn only for research, never for Android."""
#!/usr/bin/env python3
"""Run bounded original staffing functions, without replacing native callees.
Optional --exe extracts minimal reproducible source slices from known executable.
"""
import argparse,hashlib,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0
ROOT=Path(sys.argv[2]);ROOT.mkdir(parents=True,exist_ok=True)
(ROOT/"source").mkdir(exist_ok=True)
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
SPANS=[('candidate_pool',0x8006f8bc,0x8006fae0),('staff_commit',0x80070f48,0x80071384),('rest_place',0x8003dda8,0x8003e0b4),('find_fixture',0x8001c8dc,0x8001ca7c),('memset_rng',0x8007e61c,0x8007e678),('role_table',0x800cd750,0x800cd75e),('rest_offsets',0x800997c8,0x800997e0)]
STAFF=0x143ff8; STORE=0x12b2f8; STOP=0x80001000
FIELDS=[(0,2),(2,1),(3,1),(4,1),(6,2),(8,2),(12,4),(16,4),(20,4)]+[(a,1) for a in range(24,47)]+[(47,10)]
def js(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def machine():
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000)
 for name,a,end in SPANS:u.mem_write(a&0x1fffffff,(ROOT/'source'/f'{name}.bin').read_bytes())
 for r,v in [(UC_MIPS_REG_SP,0x801f0000),(UC_MIPS_REG_FP,0x801f0000),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 return u
def write(u,a,b):u.mem_write(a&0x1fffffff,bytes(b))
def read(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def packed_records(mapname):
 out=[]
 for i in range(35):
  b=bytearray(60);struct.pack_into('<I',b,12,7000+i);struct.pack_into('<I',b,20,10+i)
  b[24]=80+i%20;b[26:40]=bytes(range(30,44));out.append(b)
 return out
def run(u,entry):
 u.emu_start(entry,STOP,count=100000)
 assert u.reg_read(UC_MIPS_REG_PC)==STOP,'instruction cap or unexpected return'
def watch(u):
 reads=[];writes=[]
 def hook(u,access,address,size,value,target):
  a=address&0x1fffffff
  for sid in range(35):
   lo=STAFF+sid*60+16
   if a<lo+4 and a+size>lo:target.append(dict(pc=hex(u.reg_read(UC_MIPS_REG_PC)),staff=sid,address=hex(a),size=size))
 u.hook_add(UC_HOOK_MEM_READ,hook,reads);u.hook_add(UC_HOOK_MEM_WRITE,hook,writes)
 return reads,writes
def commit_case(name,old,new):
 records=packed_records('TOWN0001')
 for sid,b in enumerate(records):
  struct.pack_into('<H',b,0,1 if sid in old else 0)
  struct.pack_into('<I',b,16,0x60001000+sid)
  b[25]=1;b[40:47]=bytes([1,2+sid%3,2,0,3,3,0]);b[47:57]=bytes(range(10))
 before=b''.join(records);u=machine();write(u,STAFF,before)
 store=bytearray(5080);store[0]=1;struct.pack_into('<H',store,4,1);struct.pack_into('<ii',store,68,28,26);struct.pack_into('<3h',store,0xdd8,*old)
 # Synthetic accessible room anchor for original native fixture finder/placement.
 struct.pack_into('<I',store,264+6*112+6*4,0x80000000|(48<<12)|120)
 for sid in old:
  if sid!=-1:struct.pack_into('<I',store,264+2*112+(2+sid%3)*4,0x80000000|(650<<12))
 write(u,STORE,store);write(u,0x12ab48,struct.pack('<3i',*new));u.reg_write(UC_MIPS_REG_A0,0x8012b2f8)
 rd,wr=watch(u);run(u,0x80070f48);after=read(u,STAFF,2100)
 assert not rd and not wr
 assert list(struct.unpack('<3h',read(u,STORE+0xdd8,6)))==list(new)
 changed=[]
 for sid in sorted(set(old+new)-{-1}):
  b=before[sid*60:(sid+1)*60];a=after[sid*60:(sid+1)*60];same=any(old[i]==new[i]==sid for i in range(3));released=any(old[i]==sid and old[i]!=new[i] for i in range(3));added=any(new[i]==sid and old[i]!=new[i] for i in range(3))
  assert a[12:20]==b[12:20]
  if not added:assert a[20:24]==b[20:24]
  assert a[24]==b[24] and a[26:40]==b[26:40]
  if same:assert a==b
  if released:assert a[25]==a[24]
  elif added:assert a[25]==b[25]
  assert struct.unpack_from('<i',a,20)[0]==struct.unpack_from('<i',b,20)[0]+int(added)
  changed.append(dict(id=sid,old_slot=old.index(sid) if sid in old else None,new_slot=new.index(sid) if sid in new else None,changed_offsets=[i for i in range(60) if a[i]!=b[i]],energy_before=b[25],energy_after=a[25],maximum_energy=a[24],experience_before=struct.unpack_from('<i',b,20)[0],experience_after=struct.unpack_from('<i',a,20)[0],owner_after=struct.unpack_from('<H',a)[0],body_after=struct.unpack_from('<h',a,6)[0],task_after=a[40],position_after=list(struct.unpack_from('<3b',a,41)),goal_after=list(struct.unpack_from('<3b',a,44)),route_after=list(a[47:57])))
 return dict(name=name,old_slots=old,new_slots=new,people=changed,word16_reads=rd,word16_writes=wr,native_subroutines=True,source_steps='Bounded staffing transaction; not natural gameplay or elapsed time.')
exe=Path(sys.argv[1]).read_bytes();assert hashlib.sha256(exe).hexdigest()==EXE_SHA
for name,a,e in SPANS:(ROOT/'source'/f'{name}.bin').write_bytes(exe[a-0x80010000+2048:e-0x80010000+2048])
cases=[commit_case('unchanged',[0,1,2],[0,1,2]),commit_case('swap_manager_and_staff',[0,1,2],[1,0,2]),commit_case('replace_second',[0,1,2],[0,3,2]),commit_case('dismiss_second',[0,1,2],[0,-1,2])]
js('staff-lifecycle.json',dict(exe_sha256=EXE_SHA,cases=cases,native_callee_replacements=0,scope='Synthetic rosters; four bounded original 80070F48 calls with real rest and fixture finder. No natural play or full UI.'))
print('STAFF_LIFECYCLE_SOURCE_PASS 4 original transactions')
