"""Independent whole transfer-profile request audit inside actual native UI."""
from check_machine import *
from caller_connection_harness import Memory
from staff_transfer_profile import profile
from settings_rectangles import rectangle
from unicorn import UC_HOOK_CODE
import hashlib,json
LEAF={0x80070194:5,0x8006b780:3,0x800155d0:2,0x8004e494:3,0x800182d0:4}
class OverlayMemory:
 def __init__(self,source):self.source=source;self.overlay={}
 def read(self,a,n):
  a&=0x1fffffff;b=self.source.read(a,n);return bytes(self.overlay.get(a+k,v) for k,v in enumerate(b))
 def write(self,a,b):
  a&=0x1fffffff
  for k,v in enumerate(b):self.overlay[a+k]=v
 def word(self,a):return int.from_bytes(self.read(a,4),'little')
 def wordset(self,a,v):self.write(a,(v&0xffffffff).to_bytes(4,'little'))
 def byte(self,a):return self.read(a,1)[0]
class TransferProfileMonitor:
 def __init__(self,u,runner):
  self.u=u;self.runner=runner;self.active=[];self.checks=[];self.hooks=[]
  for a in (0x80073100,0x80074150,*LEAF):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.observe,begin=a,end=a))
 def observe(self,u,a,n,d):
  m=Memory(u)
  if a in (0x80073100,0x80074150):
   sm=OverlayMemory(m);calls=[]
   def child(addr,*args):
    args=[x&0xffffffff for x in args]
    if addr==0x800155d0:args[1]&=65535
    if addr==0x800182d0:args[2]&=255
    numeric=sm.word(0x800cd938) if addr==0x8004e494 and args[2] in(294,295,369) else None
    wage=sm.word(0x800e4000) if addr==0x8004e494 and args[2]==296 else None
    calls.append([addr,args,numeric,wage])
    return len(rectangle(args[0]&65535,args[0]>>16,args[1]&65535,args[1]>>16,args[2],args[3])) if addr==0x800182d0 else 0
   profile(sm,u.reg_read(UC_MIPS_REG_A0),u.reg_read(UC_MIPS_REG_A1),a==0x80074150,child);ctx={'calls':calls,'at':0,'start':a,'end':0x80074150 if a==0x80073100 else 0x800752c0};self.active.append(ctx)
   def check():
    assert self.active[-1] is ctx and ctx['at']==len(calls);self.active.pop();self.checks.append([a,len(calls),hashlib.sha256(json.dumps(calls,separators=(',',':')).encode()).hexdigest()])
   self.runner.onreturn(u.reg_read(UC_MIPS_REG_RA),check);return
  if not self.active:return
  ctx=self.active[-1]
  if not ctx['start']<=u.reg_read(UC_MIPS_REG_RA)<ctx['end']:return
  want=ctx['calls'][ctx['at']]
  # Nested leaf functions (6B780 ->4E494 ->155D0) are independently checked
  # by existing text monitors, not additional direct profile requests.
  if a!=want[0]:return
  args=[u.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:min(4,LEAF[a])]]
  if LEAF[a]==5:args.append(get(u,u.reg_read(UC_MIPS_REG_SP)+16))
  if a==0x800155d0:args[1]&=65535
  if a==0x800182d0:args[2]&=255
  assert args==want[1],('profile request',hex(a),ctx['at'],args,want[1])
  if want[2] is not None:assert get(u,0x800cd938)==want[2]
  if want[3] is not None:assert get(u,0x800e4000)==want[3]
  ctx['at']+=1
 def dispose(self):
  assert not self.active
  for h in self.hooks:self.u.hook_del(h)
