"""Observe native72774 write-before-validation binding contract on real stores."""
from check_machine import *
from caller_connection_harness import Memory
from unicorn import UC_HOOK_CODE
class SourceTransferMonitor:
 def __init__(self,u,r):
  self.u=u;self.checks=[]
  def observe(z,a,n,d):
   m=Memory(z);count=m.word(0x800cd970);assert 0<count<=10
   ids=[get(z,0x800e4328+4*k) for k in range(count)]
   expected=[list(struct.unpack('<3i',m.read(0x800e3ed8+k*12,12))) for k in range(count)]
   before=[list(struct.unpack('<3h',m.read(0x8012b2f8+k*5080+0xdd8,6))) for k in ids]
   ret=next((k+1 for k,b in enumerate(expected) if b[0]==-1),0)
   def check():
    actual=[list(struct.unpack('<3h',m.read(0x8012b2f8+k*5080+0xdd8,6))) for k in ids]
    assert actual==expected and z.reg_read(UC_MIPS_REG_V0)==ret,(before,expected,actual,ret)
    self.checks.append(dict(store_slots=ids,before=before,after=actual,result=ret))
   r.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
  self.h=u.hook_add(UC_HOOK_CODE,observe,begin=0x80072774,end=0x80072774)
 def dispose(self):self.u.hook_del(self.h)
