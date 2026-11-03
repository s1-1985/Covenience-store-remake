"""Independent whole36AC0 with five target algorithms on source-created live RAM."""
from check_machine import *
from caller_connection_harness import Memory
from staff_loop_selected import update
from staff_target_chain import target
from source_customer_loop_monitor_20261030 import FIXTURES,PRODUCTS,DIRECTION_IMAGES
from recovered import i32
from unicorn import UC_HOOK_CODE
import hashlib
class SourceStaffLoopMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.pending=0
  def observe(z,a,n,d):
   m=Memory(z);p=z.reg_read(UC_MIPS_REG_A0);slot=(p-0x8012b2f8)//5080;assert 0<=slot<10
   ma=0x800cecec+slot*2948;sa=m.word(ma);store=bytearray(m.read(p,5080));people=[bytearray(m.read(0x80143ff8+j*60,60)) for j in range(35)];meta=bytearray(m.read(ma,2948));summary=m.read(sa,168)
   refs=struct.unpack_from('<3h',store,0xdd8);before=[dict(id=k,state=people[k][0x28],energy=people[k][0x19],position=list(people[k][0x29:0x2c])) for k in refs if k!=-1]
   clock=m.word(0x800cd93c);seed=m.word(0x800d6270);flags=struct.unpack('<H',m.read(0x800cd790,2))[0];cash=[i32(m.word(x)) for x in (0x800cd9f8,0x800cd9fc)];images=[list(struct.unpack('<12i',m.read(0x8009ce14+j*88,48))) for j in range(27)];calls=[]
   def choose(name,role,person,model_meta,sd):
    ret,ns=target(name,role,person,model_meta,sd,store,people,summary,FIXTURES,clock);calls.append([name,role,ret]);return ret,ns
   ec,ef,es,effects=update(store,people,meta,summary,cash,flags,seed,clock,FIXTURES,PRODUCTS,images,m.word(0x800ce60c),DIRECTION_IMAGES,choose)
   self.pending+=1
   def finish():
    for label,address,want in (('store',p,store),('staff',0x80143ff8,b''.join(people)),('metadata',ma,meta),('summary',sa,summary)):
     got=m.read(address,len(want));assert got==want,('live staff loop',slot,clock,label,effects,[(i,x,y) for i,(x,y) in enumerate(zip(got,want)) if x!=y][:8])
    assert m.word(0x800d6270)==es and struct.unpack('<H',m.read(0x800cd790,2))[0]==ef and [m.word(x) for x in (0x800cd9f8,0x800cd9fc)]==[v&0xffffffff for v in ec],('staff RNG/flags/cash',slot,clock,effects)
    self.checks.append(dict(clock=clock,store_slot=slot,before=before,after=[dict(id=k,state=people[k][0x28],energy=people[k][0x19],position=list(people[k][0x29:0x2c])) for k in refs if k!=-1],effects=effects,targets=calls,seed_before=seed,seed_after=es,store_sha256=hashlib.sha256(store).hexdigest(),staff_sha256=hashlib.sha256(b''.join(people)).hexdigest()));self.pending-=1
   runner.onreturn(z.reg_read(UC_MIPS_REG_RA),finish)
  self.h=u.hook_add(UC_HOOK_CODE,observe,begin=0x80036ac0,end=0x80036ac0)
 def dispose(self):
  assert self.pending==0;self.u.hook_del(self.h)
