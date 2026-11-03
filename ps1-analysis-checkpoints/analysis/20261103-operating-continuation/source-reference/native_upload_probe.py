"""Original80CA0 upload/queue/82200 CPU portwrites under supplieddevice state.
Hardwareports mapto RAM; originaltimer/interrupt endpoint instructions areexplicitlypatched.
"""
from check_machine import *
from caller_connection_harness import Memory
from gpu_upload import PORTS,plan
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
import hashlib
PATCHES=(0x80082840,0x80082888,0x80082958,0x80082224,0x8008231c)
class NativeUploadProbe:
 def __init__(self,u,onreturn):
  # Harness-only port storage must not overlap source graphics/audio loads.
  # Original BGM6 VB reaches1EF000 and overwrote the former1E1000 cells.
  self.u=u;self.m=Memory(u);self.onreturn=onreturn;self.hooks=[];self.checks=[];self.writes=[];self.irq=[];self.calls=[];self.saved={a:self.m.read(a,4) for a in PATCHES};self.ports=[0x80002000+j*4 for j in range(5)]
  for a,p in zip(PORTS,self.ports):put(u,a,p)
  for a in PATCHES:self.m.write(a,bytes(4))
  put(u,self.ports[0],0x04000000);put(u,self.ports[4],0);put(u,0x800caf20,0);put(u,0x800caf24,0);self.m.write(0x800cae1d,b'\0\0');self.m.write(0x800cae20,struct.pack('<2h',1024,512))
  for a in(0x80080ca0,0x80082200,0x80082888,0x80082958):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.code,begin=a,end=a))
  self.hooks.append(u.hook_add(UC_HOOK_MEM_WRITE,self.mem,begin=0x2000,end=0x2013));u.ctl_remove_cache(0x80080000,0x80083000)
 def mem(self,z,access,a,n,v,d):
  if a in [p&0x1fffffff for p in self.ports]:self.writes.append([a,v&0xffffffff])
 def code(self,z,a,n,d):
  if a==0x80082888:self.irq.append(0);z.reg_write(UC_MIPS_REG_V0,7);return
  if a==0x80082958:self.irq.append(z.reg_read(UC_MIPS_REG_A0));z.reg_write(UC_MIPS_REG_V0,7);return
  a0=z.reg_read(UC_MIPS_REG_A0);a1=z.reg_read(UC_MIPS_REG_A1)
  if a==0x80082200:self.calls.append([self.m.read(a0,8).hex(),a1]);return
  rect=self.m.read(a0,8);payload=self.m.read(a1,64);mutated,expected,ret=plan(rect,1024,512,payload,a1);wp=len(self.writes);ip=len(self.irq);cp=len(self.calls);expectwrites=[[(self.ports[j]&0x1fffffff),v] for j,v in expected]
  def check():
   assert self.writes[wp:]==expectwrites and self.irq[ip:]==[0,7] and self.calls[cp:]==[[rect.hex(),a1]] and self.m.read(a0,8)==mutated,('upload nativeports',self.writes[wp:],expectwrites,self.irq[ip:])
   assert get(z,0x800caf20)==0 and get(z,0x800caf24)==0
   self.checks.append([list(struct.unpack('<4H',rect)),a1,expectwrites,[0,7]])
  self.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
 def dispose(self):
  for h in self.hooks:self.u.hook_del(h)
  for a,b in self.saved.items():self.m.write(a,b)
