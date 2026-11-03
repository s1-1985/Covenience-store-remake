"""Observe original3EF44 dequeue without bypassing its children or sound path."""
from check_machine import *
from caller_connection_harness import Memory
from event_queue import consume
from town_monthly import population
from unicorn import UC_HOOK_CODE
from recovered import i32
import hashlib
HALVES={0x800e3bd8,0x800e3bda,0x800e3bdc,0x800e3bde}
BYTES={0x800e3be0,0x800cd948,0x800cd8a0}
ADDRESSES=[0x801398b0,0x801398b4,0x801398b8,0x800e3be4,0x800e3be8,0x800cd7ec,
  0x800e3c28,0x800e3c2c,0x800da974,0x800da978,0x800e36a8,0x800e36ac,
  *range(0x800e3620,0x800e3638,4),*HALVES,0x800e3be0,0x800cd80c,0x800cd930,
  0x800cd9b4,0x800cd948,0x800cd8a0,*range(0x800e3ba8,0x800e3bbc,4),*range(0x800e3bc0,0x800e3bd4,4)]
class SourceEventConsumerMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.pending=[]
  def value(m,a):return m.byte(a) if a in BYTES else struct.unpack('<H',m.read(a,2))[0] if a in HALVES else m.word(a)
  def observe(z,a,n,d):
   if a==0x80064e4c:
    if self.pending:self.pending[-1].append(i32(z.reg_read(UC_MIPS_REG_A0)))
    return
   m=Memory(z);q=bytearray(m.read(0x80137970,8000));text=m.read(0x800e3aa0,120)
   state={a:value(m,a) for a in ADDRESSES};clock=m.word(0x800cd93c);seed=m.word(0x800d6270)
   storesraw=m.read(0x8012b2f8,50800);staff=m.read(0x80143ff8,2100)
   stores=[]
   for j in range(10):
    s=storesraw[j*5080:(j+1)*5080]
    stores.append(dict(active=s[0],flags=struct.unpack_from('<H',s,4)[0],annual_sales=struct.unpack_from('<i',s,0xd0c)[0],rating=struct.unpack_from('<i',s,0xc68)[0]))
   # Population is needed only when an available mode3 notice will be dequeued.
   pop=0
   if not state[0x801398b4]:
    first=next((j for j in range(50) if q[j*160]),None)
    if first is not None and q[first*160+2]==3:
     groups=[list(zip(*[iter(struct.unpack('<10h',m.read(0x8009ff1c+j*20,20)))]*2)) for j in range(144)]
     pop=population(m.read(0x801398f0,24000),0,groups)
   et,sounds,slot=consume(q,state,text,clock,stores,pop)
   calls=[];self.pending.append(calls);caller=z.reg_read(UC_MIPS_REG_RA)
   def check():
    assert self.pending.pop() is calls
    assert m.read(0x80137970,8000)==q,('event queue',clock,slot)
    assert m.read(0x800e3aa0,120)==et,('event text',clock,slot)
    assert calls==sounds,('event sounds',calls,sounds)
    assert m.word(0x800d6270)==seed and m.word(0x800cd93c)==clock
    assert m.read(0x8012b2f8,50800)==storesraw and m.read(0x80143ff8,2100)==staff
    for a,v in state.items():assert value(m,a)==v,('event state',hex(a),value(m,a),v)
    self.checks.append(dict(clock=clock,slot=slot,kind=state[0x800e3be4],mode=None if slot is None else q[slot*160+2],
      sounds=sounds,active=state[0x801398b4],timer=state[0x801398b8],
      queue_sha256=hashlib.sha256(q).hexdigest(),text_sha256=hashlib.sha256(et).hexdigest()))
   runner.onreturn(caller,check)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x8003ef44,0x80064e4c)]
 def dispose(self):
  assert not self.pending
  for h in self.hooks:self.u.hook_del(h)
