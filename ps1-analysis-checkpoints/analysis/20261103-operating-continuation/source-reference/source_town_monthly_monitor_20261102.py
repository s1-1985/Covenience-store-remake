"""Whole2BD54 independent town/RNG/history/flags/actions and real notification text/queue."""
from check_machine import *
from caller_connection_harness import Memory
from town_monthly import monthly,population
from town_mutation import descriptors
from text_buffer import TextBuffer
from event_queue import reserve
from recovered import i32
from unicorn import UC_HOOK_CODE
import json,hashlib
R=Path(__file__).resolve().parent;TABLE=descriptors(json.loads((R/'town-building-tables.json').read_text())['buildings'])
FIELDS={'seed':0x800d6270,'month':0x800ce60c,'stage':0x800ce610,'hour':0x800ce614,'subhour':0x800ce618,'reference':0x800cd9a8,'divisor':0x800cd9a0,'tier':0x800cd98c,'mode':0x800cd948,'progress_flags':0x800cd8a0,'progress_counter':0x800cd9b4,'dirty':0x800cd8dc}
BYTE={'tier','mode','progress_flags','dirty'}
class SourceTownMonthlyMonitor:
 def __init__(self,u,runner):
  self.u=u;self.checks=[];self.active=None;m=Memory(u)
  groups=[list(zip(*[iter(struct.unpack('<10h',m.read(0x8009ff1c+j*20,20)))]*2)) for j in range(144)]
  def readstate():return {**{k:m.byte(a) if k in BYTE else m.word(a) for k,a in FIELDS.items()},'history':[m.word(0x800e36a8+j*4) for j in range(60)]}
  def observe(z,a,n,d):
   if a!=0x8002bd54:
    ra=z.reg_read(UC_MIPS_REG_RA)
    if self.active is not None and 0x8002bd54<=ra<0x8002e138:
     args=[i32(z.reg_read(v)) for v in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)[:2 if a==0x8001f4b4 else 3]]
     self.active.append(tuple(['remove']+args) if a==0x8001f4b4 else tuple(['build']+args))
    return
   assert self.active is None;town=bytearray(m.read(0x801398f0,24000));before_pop=population(town,0,groups);before=readstate()
   pool=m.read(0x8012b2f8,50800);staff=m.read(0x80143ff8,2100);stores=[]
   for j in range(10):
    p=j*5080;stores.append(dict(active=pool[p],rect=list(struct.unpack_from('<4i',pool,p+8)),value=struct.unpack_from('<i',pool,p+0xd5c)[0],c74=pool[p+0xc74],c75=pool[p+0xc75],c76=pool[p+0xc76]))
   order=[]
   for j in struct.unpack('<10i',m.read(0x800ce61c,40)):
    if j==-1:break
    order.append(j)
   queue=bytearray(m.read(0x80137970,8000));text=TextBuffer(m.read(0x800e4020,120),m.word(0x800cd8c8),m.read);notify_calls=[]
   def notify(kind,tier):
    if kind is None:text.append(0x8009926c if tier==6 else 0x80099294,4);event=(0,0,100,1,0)
    else:
     if kind==20:text.append(0x80099258,4)
     elif kind in (22,23,24):text.append(m.word(0x800993f8+tier*4),4);text.append(0x80098f3c,0)
     else:
      name=struct.unpack('<h',m.read(0x80098768+kind*2,2))[0]+98;text.lookup(name,4);text.append(0x80098f2c,0)
     event=(2,struct.unpack_from('<h',bytes.fromhex(TABLE[kind]['raw_hex']),52)[0],30,1,0)
    reserve(queue,*event,text.data);notify_calls.append([kind,tier,list(event)])
   expected,events,actions=monthly(town,TABLE,groups,stores,order,before,notify_text=notify)
   trace=[];self.active=trace
   def check():
    assert self.active is trace and trace==actions,('monthly actions',trace,actions)
    assert m.read(0x801398f0,24000)==town and readstate()==expected,('whole monthly town/state',readstate(),expected)
    assert m.read(0x80137970,8000)==queue and m.read(0x800e4020,120)==text.data and m.word(0x800cd8c8)==text.pos
    assert m.read(0x8012b2f8,50800)==pool and m.read(0x80143ff8,2100)==staff
    self.checks.append(dict(calendar=[before[k] for k in ('month','stage','hour','subhour')],population_before=before_pop,population_after=population(town,0,groups),
     seed_before=before['seed'],seed_after=expected['seed'],tier_before=before['tier'],tier_after=expected['tier'],pending_after=expected['progress_counter'],flags_after=expected['progress_flags'],
     events=[list(x) for x in events],actions=[list(x) for x in actions],notify_calls=notify_calls,town_sha256=hashlib.sha256(town).hexdigest(),queue_sha256=hashlib.sha256(queue).hexdigest()));self.active=None
   runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x8002bd54,0x8001f1c0,0x8001f4b4)]
 def dispose(self):
  assert self.active is None
  for h in self.hooks:self.u.hook_del(h)
