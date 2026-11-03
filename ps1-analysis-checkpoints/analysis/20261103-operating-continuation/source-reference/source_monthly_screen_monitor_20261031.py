"""Observer for native whole6C048 layout, calls and numeric working slots."""
from check_machine import *
from caller_connection_harness import Memory
from monthly_results_screen_20261031 import plan
from unicorn import UC_HOOK_CODE
import hashlib
class SourceMonthlyScreenMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.active=None
  def observe(z,a,n,d):
   m=Memory(z)
   if a==0x8006c048:
    assert self.active is None
    x,y=[z.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1)]
    values=struct.unpack('<6i',m.read(0x800e3620,24));expected=plan(x,y,values,m.read(0x80010c18,10))
    entry=dict(clock=m.word(0x800cd93c),coords=[x,y],values=list(values),expected=expected,trace=[])
    self.active=entry;seed=m.word(0x800d6270);stores=m.read(0x8012b2f8,50800);staff=m.read(0x80143ff8,2100)
    def check():
     assert entry['trace']==expected['requests'],('monthly screen',entry['trace'],expected['requests'])
     assert all(m.word(k)==v for k,v in expected['final_slots'].items())
     assert m.read(0x800e3620,24)==struct.pack('<6i',*values)
     assert m.word(0x800d6270)==seed and m.word(0x800cd93c)==entry['clock']
     assert m.read(0x8012b2f8,50800)==stores and m.read(0x80143ff8,2100)==staff
     self.checks.append(dict(clock=entry['clock'],coords=entry['coords'],values=list(values),requests=entry['trace']))
     self.active=None
    runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check);return
   if self.active is None or not 0x8006c048<=z.reg_read(UC_MIPS_REG_RA)<0x8006c8b0:return
   args=[z.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)]
   if a==0x80017b18:args[2]&=65535
   row=dict(address=a,args=args)
   if a==0x8004e494:
    row['slot']=0x800e4000 if args[2]==272 else 0x800cd938;row['value']=m.word(row['slot'])
   self.active['trace'].append(row)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x8006c048,0x80017b18,0x80067338,0x8004e494)]
 def dispose(self):
  assert self.active is None
  for h in self.hooks:self.u.hook_del(h)
