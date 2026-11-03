"""Whole60418 parent/panel policy over observed original children in real play."""
from check_machine import *
from caller_connection_harness import Memory
from source_play_return_monitor_20261102 import BytesMemory
from store_operation_control import run
from recovered import i32
from unicorn import UC_HOOK_CODE
import hashlib
FIELDS=[(0x8012b2f8,50800),(0x80143ff8,2100),(0x800cd700,0x380),(0x800e4000,4),(0x800dae60,192*36),(0x801398bc,1),(0x8013796c,4)]
def project(m):return [m.read(a,n) for a,n in FIELDS]
class SourceOperationParentMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.active=None
  counts={0x8008eaec:3,0x80065974:0,0x80017b18:3,0x8004e494:3,0x80067338:3,0x80018940:2,0x800419e0:0,0x8004e578:6,0x80066fcc:1,0x80075514:2,0x80062bd8:1,0x80061938:1,0x80063e44:1}
  exe=EXE.read_bytes();sites={}
  for a in range(0x80060418,0x80060b90,4):
   word=struct.unpack_from('<I',exe,a-0x80010000+2048)[0]
   if word>>26==3:
    target=0x80000000|((word&0x3ffffff)<<2)
    if target in (0x80065820,0x80041630):continue # Independently computed units/record, not shared policy children.
    assert target in counts;sites[a]=target
  def observe(z,a,n,d):
   m=Memory(z)
   if a==0x80060418:
    assert self.active is None;ev=dict(initial=bytes(z.mem_read(0,0x200000)),rows=[]);self.active=ev
    def finish():
     state=BytesMemory(ev['initial']);cursor=0
     def child(target,*args):
      nonlocal cursor
      row=ev['rows'][cursor];cursor+=1;expected=[v&0xffffffff for v in args];actual=row['args'][:]
      if target in (0x80017b18,0x8004e578):expected[2]&=255;actual[2]&=255
      assert [target,expected]==[row['target'],actual],('operation child',cursor,hex(target),expected,hex(row['target']),actual)
      assert project(state)==row['before'],('operation parent bytes',cursor,hex(target),[(hex(p),i) for (p,n),x,y in zip(FIELDS,project(state),row['before']) for i,(v,w) in enumerate(zip(x,y)) if v!=w][:5])
      state.b[:]=row['after'];return row['result']
     ret,states=run(state,child)
     assert cursor==len(ev['rows']) and ret==i32(z.reg_read(UC_MIPS_REG_V0)) and project(state)==project(m)
     self.checks.append(dict(result=ret,states=states,calls=[[hex(r['target']),r['args'],r['result']] for r in ev['rows']],projection_sha256=[hashlib.sha256(b).hexdigest() for b in project(m)]));self.active=None
    runner.onreturn(z.reg_read(UC_MIPS_REG_RA),finish);return
   assert self.active is not None;target=sites[a];num=counts[target];args=[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:min(4,num)]]
   args.extend(m.word(z.reg_read(UC_MIPS_REG_SP)+16+4*j) for j in range(max(0,num-4)))
   row=dict(target=target,args=args,before=project(m));self.active['rows'].append(row)
   def returned():row.update(after=bytes(z.mem_read(0,0x200000)),result=i32(z.reg_read(UC_MIPS_REG_V0)))
   runner.onreturn(a+8,returned)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x80060418,*sites)]
 def dispose(self):
  assert self.active is None
  for h in self.hooks:self.u.hook_del(h)
