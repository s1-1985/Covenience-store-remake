"""Independent entry/iteration/wrapper policy over observed original children."""
from check_machine import *
from caller_connection_harness import Memory
from mainplay_entry import run as entry
from mainplay_iteration import iteration
from verify_mainplay_iteration import CALLS
from recovered import i32
from unicorn import UC_HOOK_CODE
import hashlib

FIELDS=[(0x800cd8b8,4),(0x800cda00,4),(0x800cd9b4,4),(0x8013796c,4),
 (0x800cd7f4,4),(0x800cd9a4,4),(0x801398bc,1),(0x800cd884,4),
 (0x800cd850,4),(0x800cd9cc,4),(0x800cd7e0,4),(0x800cd9d8,4)]
class BytesMemory:
 def __init__(self,b):self.b=bytearray(b)
 def read(self,a,n):return bytes(self.b[(a&0x1fffffff):(a&0x1fffffff)+n])
 def write(self,a,b):self.b[(a&0x1fffffff):(a&0x1fffffff)+len(b)]=b
 def word(self,a):return struct.unpack('<I',self.read(a,4))[0]
 def wordset(self,a,v):self.write(a,struct.pack('<I',v&0xffffffff))
 def byte(self,a):return self.read(a,1)[0]
 def byteset(self,a,v):self.write(a,bytes([v&255]))
 def mem_read(self,a,n):return self.read(a,n)
 def mem_write(self,a,b):self.write(a,b)
def project(m,gp):return [m.read(a,n) for a,n in FIELDS+[(gp,1)]]

class SourcePlayReturnMonitor:
 def __init__(self,u,runner,gp):
  self.u=u;self.gp=gp;self.rows=[];self.initial=bytes(u.mem_read(0,0x200000));self.pending=0
  counts=dict(CALLS);counts.update({0x80065b3c:4,0x80065100:2})
  exe=EXE.read_bytes();self.sites={}
  for lo,hi,scope in ((0x8005cd60,0x8005d5c4,'play'),(0x80012d90,0x80012de0,'wrapper')):
   for a in range(lo,hi,4):
    word=struct.unpack_from('<I',exe,a-0x80010000+2048)[0]
    if word>>26==3:
     dest=0x80000000|((word&0x3ffffff)<<2)
     assert dest in counts or dest==0x8005cd60,(hex(a),hex(dest))
     assert struct.unpack_from('<I',exe,a-0x80010000+2052)[0]==0
     if dest!=0x8005cd60:self.sites[a]=(dest,scope)
  def observe(z,a,n,d):
   target,scope=self.sites[a];m=Memory(z)
   row=dict(site=a,target=target,scope=scope,args=[z.reg_read(v) for v in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:counts[target]]],before=project(m,gp))
   self.rows.append(row);self.pending+=1
   def returned():
    row['after_ram']=bytes(z.mem_read(0,0x200000));row['result']=i32(z.reg_read(UC_MIPS_REG_V0));self.pending-=1
   runner.onreturn(a+8,returned)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in self.sites]
 def verify(self):
  assert not self.pending
  m=BytesMemory(self.initial);cursor=0
  def call(a,*args):
   nonlocal cursor
   row=self.rows[cursor];cursor+=1
   assert row['target']==a and row['args']==[x&0xffffffff for x in args],('play policy call',cursor,row['target'],a,row['args'],args)
   assert project(m,self.gp)==row['before'],('play policy parent state',cursor,hex(a))
   m.b[:]=row['after_ram'];return row['result']
  entry(m,call)
  self.iterations=0
  while True:
   self.iterations+=1
   assert self.iterations<=1000,'play policy runaway'
   m.wordset(0x800cd9b4,-1);call(0x80065974)
   if iteration(m,call)=='exit':break
  call(0x80018940,210,0);call(0x8004ea68);m.byteset(self.gp,2)
  assert cursor==len(self.rows) and project(m,self.gp)==project(Memory(self.u),self.gp)
  result=[dict(site=hex(x['site']),target=hex(x['target']),scope=x['scope'],args=x['args'],result=x['result'],after_ram_sha256=hashlib.sha256(x['after_ram']).hexdigest()) for x in self.rows]
  self.rows.clear();return result
 def dispose(self):
  for h in self.hooks:self.u.hook_del(h)
