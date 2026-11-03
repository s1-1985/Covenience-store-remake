"""Independent activation/summary/demand observations in new-store callers."""
from check_machine import *
from caller_connection_harness import Memory
from terminal_counters import activate_store
from town_mutation import descriptors
from store_summary import store_summaries
from demand import replenish_demand
from unicorn import UC_HOOK_CODE
from recovered import i32
import json,hashlib
R=Path(__file__).resolve().parent;S=0x8012b2f8;C=0x800ce65c
EX=EXE.read_bytes()
def raw(a,n):return EX[a-0x80010000+2048:a-0x80010000+2048+n]
BUILDINGS=descriptors(json.loads((R/'town-building-tables.json').read_text())['buildings'])
FIXTURES=[(raw(0x80099f0c+196*j,1)[0],struct.unpack('<i',raw(0x80099f30+196*j,4))[0],struct.unpack('<i',raw(0x80099f18+196*j,4))[0]) for j in range(53)]
IMAGES=[struct.unpack('<12i',raw(0x8009ce14+88*j,48)) for j in range(27)]
COSTS=[struct.unpack('<i',raw(0x8009ce0c+88*j,4))[0] for j in range(27)]
PROFILES=[list(struct.unpack('<24b',raw(0x800a09d0+j*24,24))) for j in range(145)]
D=json.loads((R/'demand-tables.json').read_text())
# Original selector exposes all seven source schedule rows, including closure.
D['schedules']=[list(raw(0x80099de5+j*45,45)) for j in range(7)]

def stores_state(m):
 out=[]
 for j in range(10):
  p=S+j*5080
  out.append(dict(active=m.byte(p),flags=struct.unpack('<H',m.read(p+4,2))[0],rect=struct.unpack('<4i',m.read(p+8,16)),**{f'c{74+k}':m.byte(p+0xc74+k) for k in range(3)}))
 return out
class OpeningLifecycleMonitor:
 def __init__(self,u,runner):
  self.u=u;self.runner=runner;self.checks=[];self.hooks=[]
  for a in (0x8001baac,0x80023c20,0x8002619c):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.observe,begin=a,end=a))
 def observe(self,u,a,n,d):
  m=Memory(u)
  if a==0x8001baac:
   p=u.reg_read(UC_MIPS_REG_A0);index=(p-S)//5080;stores=stores_state(m);town=bytearray(m.read(0x801398f0,24000));before=bytearray(m.read(S,50800));seed,kind=activate_store(town,BUILDINGS,stores,index,get(u,0x800d6270));before[index*5080]=1
   def check():
    assert m.read(0x801398f0,24000)==bytes(town) and m.read(S,50800)==bytes(before) and get(u,0x800d6270)==seed and m.byte(0x800cd8dc)==0
    self.checks.append([a,index,kind,seed,hashlib.sha256(town).hexdigest()])
  elif a==0x80023c20:
   stores=[];pool=m.read(S,50800);people=m.read(0x80143ff8,2100);prior=m.read(C,1680)
   for j in range(10):
    p=j*5080;c=j*168;w,h=struct.unpack_from('<2i',pool,p+0x44);ids=struct.unpack_from('<3h',pool,p+0xdd8)
    skills=[struct.unpack_from('<b',people,k*60+32)[0] for k in ids if k!=-1]
    stores.append(dict(active=pool[p],width=w,height=h,words={(x,y):struct.unpack_from('<I',pool,p+0x108+y*112+x*4)[0] for y in range(h) for x in range(w)},prices=list(struct.unpack_from('<27i',pool,p+0xc7c)),skills=skills,prior=dict(checkout=struct.unpack_from('<2i',prior,c+32),checkout_width=prior[c+40],rest=struct.unpack_from('<2i',prior,c+24))))
   image_bytes=m.read(0x8009ce14,27*88)
   images=[struct.unpack_from('<12i',image_bytes,j*88) for j in range(27)]
   expected=store_summaries(stores,FIXTURES,images,COSTS)
   def check():
    values=[]
    for j,s in enumerate(expected):
     if s is None:continue
     c=C+j*168;got=[i32(m.word(c+off)) for off in (0,12,16,156,164)];assert got==[s[k] for k in ('price','security','capacity','price_norm','security_norm')],('summary',j,got,s)
     assert list(struct.unpack('<27I',m.read(c+44,108)))==s['stock'],('summary stock',j,list(struct.unpack('<27I',m.read(c+44,108))),s['stock'],self.runner.phase_entries);values.append([j,got,s['stock']])
    self.checks.append([a,values])
  else:
   stores=[]
   for j in range(10):
    p=S+j*5080;c=C+j*168
    stores.append(dict(active=m.byte(p),rating=i32(m.word(p+0xc6c)),schedule=i32(m.word(p+0xc78)),old_total=i32(m.word(p+0xde0)),rect=struct.unpack('<4i',m.read(p+8,16)),capacity=i32(m.word(c+16)),price=i32(m.word(c+156)),distance=i32(m.word(c+160)),security=i32(m.word(c+164)),stock=list(struct.unpack('<27i',m.read(c+44,108)))))
   order=[]
   for j in range(10):
    x=i32(m.word(0x800ce61c+4*j))
    if x==-1:break
    order.append(x)
   town=[[struct.unpack('<h',m.read(0x801398f0+(y*60+x)*8+6,2))[0] for x in range(60)] for y in range(50)]
   expected,tot,weather,updated,seed=replenish_demand(town,D['groups'],PROFILES,stores,order,D['schedules'],D['ranges'],m.word(0x800ce60c),m.word(0x800ce610),bool(m.word(0x800cda00)),D['thresholds'],D['calendar'],D['seasons'],get(u,0x800d6270))
   def check():
    assert get(u,0x800d6270)==seed and get(u,0x800cd904)==weather,('demand rng/weather',get(u,0x800d6270),seed)
    for j in range(10):
     p=S+j*5080;assert list(struct.unpack('<144H',m.read(p+0xde4,288)))==expected[j] and m.word(p+0xde0)==tot[j]&0xffffffff,('demand',j)
     assert m.word(C+j*168+160)==updated[j]['distance']&0xffffffff
    self.checks.append([a,weather,seed,tot,hashlib.sha256(b''.join(struct.pack('<144H',*v) for v in expected)).hexdigest()])
  self.runner.onreturn(u.reg_read(UC_MIPS_REG_RA),check)
 def dispose(self):
  for h in self.hooks:self.u.hook_del(h)
