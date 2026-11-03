"""Real-state72DBC/72774: independent tentative swap and full two-pass commit/rest."""
from check_machine import *
from caller_connection_harness import Memory
from source_play_return_monitor_20261102 import BytesMemory
from staff_transfer_binding import commit,swap,ORDER,TEMP
from opening_staff_binding import native_rest_model
from unicorn import UC_HOOK_CODE
import hashlib
FIELDS=[(0x8012b2f8,50800),(0x80143ff8,2100),(ORDER,40),(TEMP,120),(0x800cd700,0x380),(0x800d8f68,32),(0x800d6270,4)]
def project(m):return [m.read(a,n) for a,n in FIELDS]
class SourceFullTransferMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.pending=0;exe=EXE.read_bytes()
  raw=lambda a,n:exe[a-0x80010000+2048:a-0x80010000+2048+n]
  dims=[struct.unpack('<2i',raw(0x80099f30+196*k,8)) for k in range(53)];offsets=[struct.unpack('<2i',raw(0x800997c8+j*8,8)) for j in range(3)]
  def observe(z,a,n,d):
   m=Memory(z);expected=BytesMemory(bytes(z.mem_read(0,0x200000)));self.pending+=1
   if a==0x80072774:result=commit(expected,lambda s,row,mode:native_rest_model(expected,s,row,mode,dims,offsets))
   else:swap(expected);result=None
   def finish():
    assert project(m)==project(expected),('whole transfer',hex(a),[(hex(p),i) for (p,n),x,y in zip(FIELDS,project(m),project(expected)) for i,(v,w) in enumerate(zip(x,y)) if v!=w][:6])
    if result is not None:assert z.reg_read(UC_MIPS_REG_V0)==result
    self.checks.append(dict(entry=hex(a),result=result,store_list=[m.word(ORDER+4*k) for k in range(m.word(0x800cd970))],projection_sha256=[hashlib.sha256(b).hexdigest() for b in project(m)]));self.pending-=1
   runner.onreturn(z.reg_read(UC_MIPS_REG_RA),finish)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x80072dbc,0x80072774)]
 def dispose(self):
  assert self.pending==0
  for h in self.hooks:self.u.hook_del(h)
