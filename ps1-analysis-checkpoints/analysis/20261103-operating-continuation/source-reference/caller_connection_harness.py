from check_machine import *
from category_parent_control import run as category_run
from category_call_contract import run as caller_run,PATHS,FEES
from category_frame_harness import CategoryFrameRunner
from operation_runtime import startup
from recovered import i32
from unicorn import UC_HOOK_CODE
import random,json,hashlib,gc
R=Path(__file__).resolve().parent;STORE=0x8012b2f8;FP=0x801ed000
LAYOUTS=[bytes.fromhex(x['raw_hex']) for x in json.loads((R/'layout-tables.json').read_text())['layouts']];CUSTOM=LAYOUTS[1::5]
NATIVE={0x80018940:2,0x800230e8:1,0x80041218:1,0x80065974:0,0x800788c8:1,0x8001b8c4:2,0x8003dda8:3,0x80022d28:1,0x8004095c:1,0x80065690:0,0x80076b68:1,0x80077de4:1,0x80060b90:1,0x80066fcc:1,0x80068978:4,0x80065080:0,0x8001b678:2,0x80044d20:1,0x8001d1ac:1,0x8001d018:1,0x8001d618:1,0x80067c80:1,0x80045404:2,0x80075514:2,0x8001cbc4:2,0x8001ca7c:3,0x8007e57c:3,0x8004594c:2,0x8006966c:0,0x80066c64:1}
REGIONS=[('stores',0x12b2f8,50800),('staff',0x143ff8,2100),('globals',0xcd700,0x380),('templates',0x13f6c0,18648),('map',0xcecec,29480),('calendar_summary',0xce608,1764),('interior_records',0xd8f88,0x10700),('regen',0x1398b0,64),('equipment_catalog',0x99f0c,53*196)]
class Memory:
 def __init__(self,u):self.u=u
 def read(self,a,n):return bytes(self.u.mem_read(a&0x1fffffff,n))
 def write(self,a,b):self.u.mem_write(a&0x1fffffff,bytes(b))
 def word(self,a):return get(self.u,a)
 def wordset(self,a,v):put(self.u,a,v)
 def byte(self,a):return self.read(a,1)[0]
 def byteset(self,a,v):self.write(a,bytes([v&255]))
def fixture(slot,side,staff,style,cash,fees,clock=100,startup_tables=True):
 u=machine()
 if startup_tables:startup(u)
 u.reg_write(UC_MIPS_REG_GP,0x800cd6c4);u.mem_write(0x183e00,(R/'source/MSG00.OBJ').read_bytes());u.reg_write(UC_MIPS_REG_RA,0x80001000);u.emu_start(0x80013448,0x80001000,count=3000000);assert u.reg_read(UC_MIPS_REG_PC)==0x80001000
 store=bytearray(5080);store[0]=1;struct.pack_into('<H',store,4,1|side<<15);struct.pack_into('<ii',store,68,28,26);struct.pack_into('<i',store,0xc70,slot);struct.pack_into('<3h',store,0xdd8,*((-1,-1,-1),(0,1,34),(0,0,0))[staff])
 for kind,x,y,w,h in ((37,2,2,4,2),(48,6,6,4,4)):
  for yy in range(y,y+h):
   for xx in range(x,x+w):struct.pack_into('<I',store,264+yy*112+xx*4,120)
  struct.pack_into('<I',store,264+y*112+x*4,0x80000000|kind<<12|120)
 r=random.Random(8120+staff)
 for sid,x,y in ((0,1,1),(1,5,5),(34,10,10)):
  person=bytearray(r.randbytes(60));person[40:43]=bytes((1,x,y));u.mem_write(0x143ff8+sid*60,bytes(person));struct.pack_into('<I',store,264+y*112+x*4,0x80000000|650<<12)
 store[0xf04]=2;store[0xf04+12:0xf04+14]=bytes((4,5));struct.pack_into('<I',store,264+5*112+4*4,650<<12);store[0xc74:0xc77]=b'\1\1\1';struct.pack_into('<i',store,0xd94,-12345);u.mem_write(STORE&0x1fffffff,bytes(store));u.mem_write(0x13f6c0,b''.join(CUSTOM))
 for a,z in ((0x800cd9f8,cash[0]),(0x800cd9fc,cash[1]),(0x800d8f68,1000),(0x800d8f78,2000),(0x800d6270,0x12345678),(0x800cd93c,clock),(0x800cd924,99),(0x800cd9dc,0xfffffffe),(0x800cd990,0),(0x800cd9cc,0),(0x800cd9c0,0),(0x800cd8fc,1),(0x800b8cb4,0),(0x800b8cac,8)):put(u,a,z)
 for a,z in zip(FEES,fees):put(u,a,z)
 for a,b in ((0xcd834,b'\1'),(0xcd8f8,struct.pack('<h',style)),(0xcd8e4,bytes(2)),(0x143fc0,bytes(12)),(0x12aa00,bytes(1024)),(0xcd7d0,struct.pack('<h',-123)),(0xcda2e,struct.pack('<h',-1)),(0xcd880,struct.pack('<h',5)),(0xe441c,bytes(4)),(0x1398bc,b'\x77')):u.mem_write(a,b)
 return u

def rawplan(path,scenario):
 endcategory=[0x4000,0]*4+[0x20,0]
 if path<2 and 24<=scenario<28:return rawplan(3,scenario-24)
 if path<3 and 21<=scenario<24:
  first=[0]+[0x8000,0]*14+[0x20,0];second=[0]+[0x8000,0]*8+[0x20,0]
  if scenario==21:first=[0]+[0x2000,0]*10+[0x20,0]+[0x8000,0]*24+[0x20,0]
  elif scenario==23:first=[0]+[0x8000,0]*10+[0x20,0]+[0x8000,0]*4+[0x20,0]
  else:second=[0]+[0x8000,0]*14+[0x20,0]+[0x2000,0]*6+[0x20,0]
  return {0x80044d20:[[0,0x4000,0,0x20,0]],0x80045404:[[0,0x20,0]],0x8004594c:[[0,0x20,0]],0x8006966c:[[0,0x20,0]],0x80076b68:[first,second],0x80060b90:[endcategory],0x80066fcc:[[0,0x20,0]]}
 if path<3 and 16<=scenario<21:
  q=scenario-16;second=q%4
  firstok=[0]+[0x8000,0]*14+[0x20,0];secondok=[0]+[0x8000,0]*(8 if second<2 else 6)+[0x20,0]
  two=[[0,0x20,0]];four=[[0]+[0x2000,0]*second+[0x20,0]];placements=[firstok,secondok]
  if q==0:two=[[0,0x40,0],[0,0x20,0]]
  if q==1:two=[[0,0x20,0],[0,0x20,0]];placements=[[0,0x40,0],firstok,secondok]
  if q==2:four=[[0,0x40,0]+[0x2000,0]*second+[0x20,0]]
  if q==3:four=[[0]+[0x2000,0]*second+[0x20,0],[0]+[0x2000,0]*second+[0x20,0]];placements=[firstok,[0,0x40,0],secondok]
  floor=[0,0x40,0,0x20,0] if q==4 else [0,0x20,0]
  return {0x80044d20:[[0,0x4000,0,0x20,0]],0x80045404:[floor],0x8004594c:two,0x8006966c:four,0x80076b68:placements,0x80060b90:[endcategory],0x80066fcc:[[0,0x20,0]]}
 if path<3 and 12<=scenario<16:
  selection=1 if scenario<14 else 3;ack=0x20 if scenario%2==0 else 0x40
  return {0x80044d20:[[0]+[0x4000,0]*(selection-1)+[0x20,0],[0,0x40,0]],0x80066c64:[[0,ack,0]]}
 if path<3 and scenario>=4:
  q=scenario-4;first=q//4;second=q%4;floor=q%3
  return {0x80044d20:[[0,0x4000,0,0x20,0]],0x80045404:[[0]+[0x2000,0]*floor+[0x20,0]],0x8004594c:[[0]+[0x2000,0]*first+[0x20,0]],0x8006966c:[[0]+[0x2000,0]*second+[0x20,0]],0x80076b68:[[0]+[0x8000,0]*14+[0x20,0],[0]+[0x8000,0]*(8 if second<2 else 6)+[0x20,0]],0x80060b90:[endcategory],0x80066fcc:[[0,0x20,0]]}
 if path<3:return {0x80044d20:[[0]+([0x40,0] if scenario==0 else [0x4000,0]*(2 if scenario==2 else 0)+[0x20,0])],0x80060b90:[endcategory],0x80066fcc:[[0,0x2000,0,0x20,0] if scenario==3 else [0,0x20,0]]}
 if scenario==0:return {0x80060b90:[endcategory],0x80066fcc:[[0,0x20,0]]}
 if scenario==3:return {0x80060b90:[[0x4000,0]*2+[0x20,0],endcategory],0x80077de4:[[0,0x20,0]],0x80045404:[[0,0x2000,0,0x20,0]],0x80066fcc:[[0,0x20,0]]}
 return {0x80060b90:[[0x20,0],endcategory],0x80067c80:[[0]+([0x4000,0] if scenario==2 else [])+[0x20,0]],0x80068978:[[0,0x20,0]],0x80076b68:[[0]+([8,0] if scenario==2 else [])+[0x20,0]],0x80066fcc:[[0,0x20,0]]}

def compare(path,scenario,slot,side,staff,style,buffer,cash=(50000000,60000000),fees=(111,222,333,444),clock=100,argument=0,setup=None,plan=None,monitor=None):
 p=PATHS[path];u=fixture(slot,side,staff,style,cash,fees,clock)
 if setup is not None:setup(u)
 put(u,FP+p['storeoff'],STORE)
 if p['argoff'] is not None:put(u,FP+p['argoff'],argument)
 if p['stateoff']:put(u,FP+p['stateoff'],77)
 u.mem_write((FP+0x1400)&0x1fffffff,bytes((7,8,9)));u.reg_write(UC_MIPS_REG_FP,FP);u.reg_write(UC_MIPS_REG_SP,FP);v=machine();v.reg_write(UC_MIPS_REG_GP,0x800cd6c4);v.mem_write(0,bytes(u.mem_read(0,0x200000)));v.reg_write(UC_MIPS_REG_FP,FP);v.reg_write(UC_MIPS_REG_SP,FP);traces=[[],[]];states=[];hooks=[[],[]];ends=[];financial=[[],[]]
 phase={a:[ss+[0]*200 for ss in plans] for a,plans in (rawplan(path,scenario) if plan is None else plan).items()};phase[0x80065690]=[[0]*200 for _ in range(30)];runners=[CategoryFrameRunner(uc,buffer,phase) for uc in (u,v)]
 if monitor is not None:
  for which,uc in enumerate((u,v)):monitor(uc,runners[which],which,hooks[which])
 for which,uc in enumerate((u,v)):
  def observe(machine,a,n,d,which=which):
   args=tuple(machine.reg_read(z) for z in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)[:NATIVE[a]]);traces[which].append((a,args))
   if a not in (0x8001cbc4,0x8001ca7c):return
   store,amount=args[:2];amount=i32(amount);side2=struct.unpack('<H',machine.mem_read((store+4)&0x1fffffff,2))[0]>>15;cashaddr=0x800cd9f8+4*side2;capitaladdr=0x800d8f68+16*side2;cashbefore=get(machine,cashaddr);capitalbefore=get(machine,capitaladdr);expected=bytes(machine.mem_read(store&0x1fffffff,5080));cashafter=i32(cashbefore-amount);capitalafter=i32(capitalbefore+amount)
   if a==0x8001ca7c:
    assert args[2]==0;expected=bytearray(expected);struct.pack_into('<I',expected,0xd94,(get(machine,store+0xd94)+amount)&0xffffffff);capitalafter=i32(capitalbefore)
   def check():
    assert get(machine,cashaddr)==cashafter&0xffffffff and get(machine,capitaladdr)==capitalafter&0xffffffff and bytes(machine.mem_read(store&0x1fffffff,5080))==bytes(expected)
    financial[which].append([a,side2,amount,cashafter,capitalafter,hashlib.sha256(expected).hexdigest()])
   runners[which].onreturn(machine.reg_read(UC_MIPS_REG_RA),check)
  for a in NATIVE:hooks[which].append(uc.hook_add(UC_HOOK_CODE,observe,begin=a,end=a))
 def stateobserve(machine,a,n,d):states.append(get(machine,machine.reg_read(UC_MIPS_REG_FP)+0x1c))
 hooks[0].append(u.hook_add(UC_HOOK_CODE,stateobserve,begin=0x80075994,end=0x80075994))
 def stop(machine,a,n,d):ends.append(a);machine.emu_stop()
 for a in p['ends']:hooks[0].append(u.hook_add(UC_HOOK_CODE,stop,begin=a,end=a))
 u.emu_start(p['start'],0,count=30000000);assert len(ends)==1,('nativebudget',path,scenario,hex(u.reg_read(UC_MIPS_REG_PC)))
 def child(a,*args):
  for reg,x in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),args):v.reg_write(reg,x&0xffffffff)
  v.reg_write(UC_MIPS_REG_RA,0x80001000);v.emu_start(a,0x80001000,count=10000000);assert v.reg_read(UC_MIPS_REG_PC)==0x80001000,('childbudget',hex(a));runners[1].flush(0x80001000);return i32(v.reg_read(UC_MIPS_REG_V0))
 parentstates=[]
 def outerchild(a,*args):
  if a==0x80075514:
   traces[1].append((a,tuple(x&0xffffffff for x in args)));v.reg_write(UC_MIPS_REG_SP,FP-64);v.reg_write(UC_MIPS_REG_FP,FP-64);result,ss=category_run(Memory(v),*args,child);parentstates.extend(ss);v.reg_write(UC_MIPS_REG_SP,FP);v.reg_write(UC_MIPS_REG_FP,FP);return result
  return child(a,*args)
 answer,end=caller_run(Memory(v),path,FP,outerchild)
 assert states==parentstates and ends==[end] and traces[0]==traces[1],(path,scenario,slot,side,staff,'control',states,parentstates,len(traces[0]),len(traces[1]),next(((i,x,y) for i,(x,y) in enumerate(zip(traces[0],traces[1])) if x!=y),None))
 hashes=[]
 for name,a,n in REGIONS:
  x=bytes(u.mem_read(a,n));y=bytes(v.mem_read(a,n));assert x==y,(path,scenario,slot,side,staff,'region',name,next((i,xx,yy) for i,(xx,yy) in enumerate(zip(x,y)) if xx!=yy));hashes.append(hashlib.sha256(x).hexdigest())
 assert financial[0]==financial[1] and runners[0].placement_checks==runners[1].placement_checks and runners[0].frames==runners[1].frames and runners[0].sounds==runners[1].sounds and runners[0].hud_checks==runners[1].hud_checks==len(states) and not runners[0].contexts and not runners[1].contexts
 if path<2:assert get(u,FP+p['stateoff'])==get(v,FP+p['stateoff'])
 if path==2:assert bytes(u.mem_read((FP+0x28)&0x1fffffff,5080))==bytes(v.mem_read((FP+0x28)&0x1fffffff,5080))
 row=[path,scenario,slot,side,staff,style,buffer,list(cash),list(fees),clock,argument,answer,end,states,[get(u,0x800cd9f8+4*j) for j in range(2)],[get(u,0x800d8f68+16*j) for j in range(2)],financial[0],runners[0].placement_checks,runners[0].hud_checks,hashes,traces[0],runners[0].frames,runners[0].sounds]
 for runner in runners:runner.dispose()
 for which,uc in enumerate((u,v)):
  for hk in hooks[which]:uc.hook_del(hk)
 return row
FIELDS=['caller_path','scenario','slot','bank_side','staff_fixture','font_style','buffer','cash_before','preallocated_fee_fixture','clock','caller_argument','category_return','caller_continuation','states','cash_after','capital_after','financial_helper_checks','placement_checks','HUD_checks','region_sha256','child_trace','frames','audio_events']
