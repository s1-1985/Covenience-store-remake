"""Independent60E70..612C8 acquisition parent over observed original children.

The resource/TIM prefix remains separately checked by NativeNewgameResources.
Cost, capital transfer and staff reset children have independent byte checks here.
"""
from check_machine import *
from caller_connection_harness import Memory
from source_play_return_monitor_20261102 import BytesMemory
from rival_helpers import land_total,premises_total,capital_post
from store_lifecycle import staff_binding
from recovered import i32
from input_wait import InputWait
from vertical_choice import select
from unicorn import UC_HOOK_CODE
import hashlib
S=0x8012b2f8
FIELDS=[(S,50800),(0x80143ff8,2100),(0x801398f0,24000),(0x800cd9f8,8),(0x800d8f68,32),(0x800cd9e0,2),(0x800cd9b4,4),(0x800cd8a0,1),(0x801398bc,1)]+[(a,4) for a in (0x800cd7fc,0x800cd800,0x800cd73c,0x800cd8a4,0x800cd8c0)]
def project(m):return [m.read(a,n) for a,n in FIELDS]
def h(m,a):return struct.unpack('<h',m.read(a,2))[0]
def acquisition(m,child):
 x,y=h(m,0x800cda42),h(m,0x800cda44);p=None
 for j in range(10):
  q=S+j*5080;box=struct.unpack('<4i',m.read(q+8,16))
  if m.byte(q) and box[0]<=x<=box[2] and box[1]<=y<=box[3]:p=q;child(0x80065000);break
 assert p is not None,'no matching store is outside modeled valid caller precondition'
 fee=0 if m.byte(p+2)==1 else 500000;m.wordset(0x800cd7fc,fee)
 land=child(0x8001dfd0,*struct.unpack('<4i',m.read(p+8,16)));cost=child(0x8001de5c,p,0)
 price=i32((land+cost)*2);m.wordset(0x800cd800,price);m.wordset(0x800cd73c,fee);m.wordset(0x800cd8a4,price)
 serial=struct.unpack('<H',m.read(p+4,2))[0]&255;m.wordset(0x800cd8c0,serial)
 child(0x8004ea68);child(0x80065974);choice=child(0x8004d6ec,50,16,p)
 result='cancel'
 if choice==1 and serial==1:child(0x80065080);result='first_store_guard'
 elif (choice==0 and i32(m.word(0x800cd9f8))<fee) or (choice==1 and i32(m.word(0x800cd9f8))<price):
  child(0x80065080);child(0x80066c64,0x800b9688);result='insufficient'
 else:
  if choice==0:
   if m.byte(p+2)==0:child(0x8001cbc4,S,fee);m.byteset(p+2,1)
   child(0x8004ea68);child(0x80065974);child(0x80065000);child(0x8004095c,0)
   choice=child(0x8004d6ec,50,16,p);result='lease'
  if choice==1:
   child(0x80065000);child(0x8001cbc4,S,price);child(0x8001cbc4,p,-price)
   serial=(struct.unpack('<H',m.read(0x800cd9e0,2))[0]+1)&65535;m.write(0x800cd9e0,struct.pack('<H',serial));m.write(p+4,struct.pack('<H',serial))
   child(0x8001b320,p,1);child(0x8001baac,p);m.byteset(0x801398bc,1);child(0x80023c20);child(0x8003ead4);result='bought'
 child(0x80065974)
 return dict(slot=(p-S)//5080,fee=fee,price=price,result=result)

class SourceAcquisitionMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.input_checks=[];self.selection_checks=[];self.active=None;exe=EXE.read_bytes();sites={};self.hooks=[]
  counts={0x80065000:0,0x8001dfd0:4,0x8001de5c:2,0x8004ea68:0,0x80065974:0,0x8004d6ec:3,0x80065080:0,0x80066c64:1,0x8001cbc4:2,0x8004095c:1,0x8001b320:2,0x8001baac:1,0x80023c20:0,0x8003ead4:0}
  for a in range(0x80060e70,0x800612b0,4):
   word=struct.unpack_from('<I',exe,a-0x80010000+2048)[0]
   if word>>26==3:
    target=0x80000000|((word&0x3ffffff)<<2);assert target in counts;sites[a]=target
  def observe(z,a,n,d):
   m=Memory(z)
   if a in (0x80041374,0x8004e578):
    if self.active is None:return
    ctx=runner.contexts[-1];tick=ctx['tick']
    model=InputWait(m.word(0x800cd9cc),m.word(0x800cd9c0),i32(m.word(0x800cd8fc)),m.word(0x800cd990),ctx['raws'][tick:],m.word(0x800d6270),(struct.unpack('<H',m.read(0x800cd7d0,2))[0],struct.unpack('<H',m.read(0x800cd8e4,2))[0]))
    if a==0x80041374:
     model.poll()
     def checkinput():
      assert ctx['tick']==tick+model.ticks
      assert [m.word(p) for p in (0x800cd9cc,0x800cd9c0,0x800cda28,0x800cda0c,0x800d6270)]==[model.held,model.edge,model.buttons,model.directions,model.seed]
      self.input_checks.append([model.buttons,model.directions,model.ticks,model.seed])
     runner.onreturn(z.reg_read(UC_MIPS_REG_RA),checkinput)
    else:
     a0,a1,a2,a3=[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)];sp=z.reg_read(UC_MIPS_REG_SP)
     expected=select(a0&65535,a0>>16,a1&65535,a1>>16,a2&255,a3,i32(m.word(sp+16)),i32(m.word(sp+20)),model,m.read(0x800dae38,40))
     def checkselection():
      assert z.reg_read(UC_MIPS_REG_V0)==expected['result'] and m.read(0x800dae38,40)==expected['cursor'] and ctx['tick']==tick+model.ticks
      self.selection_checks.append(dict(result=expected['result'],ticks=model.ticks,events=expected['events']))
     runner.onreturn(z.reg_read(UC_MIPS_REG_RA),checkselection)
    return
   if a==0x80060e70:
    assert self.active is None;event=dict(initial=bytes(z.mem_read(0,0x200000)),rows=[]);self.active=event
    def finish():
     state=BytesMemory(event['initial']);cursor=0
     def child(target,*args):
      nonlocal cursor
      row=event['rows'][cursor];cursor+=1
      assert [target,[v&0xffffffff for v in args]]==[row['target'],row['args']],('acquisition call',cursor,hex(target),args,hex(row['target']),row['args'])
      assert project(state)==row['before'],('acquisition parent bytes',cursor,hex(target))
      state.b[:]=row['after'];return row['result']
     proof=acquisition(state,child)
     assert cursor==len(event['rows']) and project(state)==project(m)
     proof.update(calls=[[hex(q['target']),q['args'],q['result']] for q in event['rows']],projection_sha256=[hashlib.sha256(b).hexdigest() for b in project(m)])
     self.checks.append(proof);self.active=None
    runner.onreturn(m.word(z.reg_read(UC_MIPS_REG_FP)+0x30),finish);return
   assert self.active is not None;target=sites[a];args=[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:counts[target]]]
   row=dict(target=target,args=args,before=project(m));self.active['rows'].append(row)
   expected=None
   if target==0x8001dfd0:expected=land_total(m.read(0x801398f0,24000),[i32(v) for v in args])
   elif target==0x8001de5c:
    prices=[i32(m.word(0x80099f10+j*196)) for j in range(53)];products=[struct.unpack('<2i',m.read(0x8009ce08+j*88,8)) for j in range(27)];images=[struct.unpack('<12i',m.read(0x8009ce14+j*88,48)) for j in range(27)]
    expected=premises_total(m.read(args[0],5080),args[1],prices,products,images)
   capital=None;binding=None
   if target==0x8001cbc4:
    flags=struct.unpack('<H',m.read(args[0]+4,2))[0];capital=capital_post(list(struct.unpack('<2i',m.read(0x800cd9f8,8))),[i32(m.word(0x800d8f68+j*16)) for j in range(2)],i32(args[1]),flags)
   if target==0x8001b320:
    store=bytearray(m.read(args[0],5080));staff=[bytearray(m.read(0x80143ff8+j*60,60)) for j in range(35)];staff_binding(store,staff,args[1]);binding=(store,b''.join(staff))
   def returned():
    row.update(after=bytes(z.mem_read(0,0x200000)),result=i32(z.reg_read(UC_MIPS_REG_V0)))
    if expected is not None:assert row['result']==expected,('acquisition cost',hex(target),row['result'],expected)
    if capital is not None:assert list(struct.unpack('<2i',m.read(0x800cd9f8,8)))==capital[0] and [i32(m.word(0x800d8f68+j*16)) for j in range(2)]==capital[1]
    if binding is not None:assert m.read(args[0],5080)==binding[0] and m.read(0x80143ff8,2100)==binding[1]
   runner.onreturn(a+8,returned)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x80060e70,*sites,0x80041374,0x8004e578)]
 def dispose(self):
  assert self.active is None
  for h in self.hooks:self.u.hook_del(h)
