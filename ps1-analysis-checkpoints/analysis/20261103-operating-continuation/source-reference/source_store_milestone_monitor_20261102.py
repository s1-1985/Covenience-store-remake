"""Whole3EAD4 count/goal/real text/queue contract; native text children retained."""
from check_machine import *
from caller_connection_harness import Memory
from progression import store_milestone
from text_buffer import TextBuffer
from event_queue import reserve
from unicorn import UC_HOOK_CODE
import hashlib
class SourceStoreMilestoneMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.pending=0
  def observe(z,a,n,d):
   m=Memory(z);pool=m.read(0x8012b2f8,50800)
   stores=[dict(active=pool[j*5080],flags=struct.unpack_from('<H',pool,j*5080+4)[0]) for j in range(10)]
   mode=m.byte(0x800cd948);flags=m.byte(0x800cd8a0);pending=m.word(0x800cd9b4)
   count,wflags,wpending,notify=store_milestone(stores,mode,flags,pending)
   queue=bytearray(m.read(0x80137970,8000));text=TextBuffer(m.read(0x800e4020,120),m.word(0x800cd8c8),m.read)
   if notify:
    text.append(0x8012b2c8,6);text.append(0x800991f0,0);text.number(count,0);text.append(0x800991f8,0)
    reserve(queue,0,0,100,1,3,text.data)
   frozen=[(p,m.read(p,n)) for p,n in ((0x8012b2f8,50800),(0x80143ff8,2100),(0x801398f0,24000),(0x800d6270,4),(0x800cd9f8,8),(0x800cd93c,4))]
   self.pending+=1
   def check():
    assert m.byte(0x800cd8a0)==wflags and m.word(0x800cd9b4)==wpending
    assert m.read(0x80137970,8000)==queue and m.read(0x800e4020,120)==text.data and m.word(0x800cd8c8)==text.pos
    assert all(m.read(p,len(b))==b for p,b in frozen)
    self.checks.append(dict(count=count,mode=mode,flags_before=flags,flags_after=wflags,pending_before=pending,pending_after=wpending,notification=notify,
     text_sha256=hashlib.sha256(text.data).hexdigest(),queue_sha256=hashlib.sha256(queue).hexdigest()));self.pending-=1
   runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=0x8003ead4,end=0x8003ead4)]
 def dispose(self):
  assert self.pending==0
  for h in self.hooks:self.u.hook_del(h)
