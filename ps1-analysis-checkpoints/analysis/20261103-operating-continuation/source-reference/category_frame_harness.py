"""Original menu/UI renderer integration. Packet formulas independent; input phases explicit."""
from check_machine import *
from unicorn import UC_HOOK_CODE
from confirmation_dialog_frame_harness import SDK
from render_control import dispatch,packet,GROUPS
from hud_display import hud,bars
from interior_placement import gate,apply_copy
from inventory_full import update
from rival_helpers import product_image
from operation_runtime import IMAGES
from interior_catalog import FIXTURES,PRODUCTS
from recovered import i32,truncdiv
import hashlib,json
R=Path(__file__).resolve().parent
MESSAGES={x['index']:x['words'] for x in json.loads((R/'message-control-inventory.json').read_text())['messages']}
class CategoryFrameRunner:
 def __init__(self,u,buffer,plans,table_address=0x80160000):
  self.u=u;self.buffer=buffer;self.buf=0x800e4540+buffer*144000;self.table=table_address;self.plans={a:[list(s) for s in ss] for a,ss in plans.items()};self.contexts=[];self.callbacks={};self.returnhooks={};self.hooks=[];self.frames=[];self.sounds=[];self.hud_checks=0;self.placement_checks=[];self.phase_entries=[]
  u.mem_write(0xe436a,struct.pack('<HH',160,120));u.mem_write((0x800e3e70+20*buffer)&0x1fffffff,struct.pack('<5I',4,self.table,0,0,0))
  for a in SDK+(0x80018a5c,0x8008ed1c,0x8008ea7c,0x80086074,0x8004095c,0x80076474):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.hook,begin=a,end=a))
  for a in self.plans:self.hooks.append(u.hook_add(UC_HOOK_CODE,self.phase,begin=a,end=a))
 def onreturn(self,address,callback):
  if address not in self.returnhooks:self.returnhooks[address]=self.u.hook_add(UC_HOOK_CODE,lambda u,a,n,d:self.flush(a),begin=address,end=address)
  self.callbacks.setdefault(address,[]).append(callback)
 def flush(self,address):
  while self.callbacks.get(address):self.callbacks[address].pop()()
 def phase(self,u,a,n,d):
  assert self.plans[a],('phase queue exhausted',hex(a),self.phase_entries)
  context=dict(address=a,raws=self.plans[a].pop(0),tick=0);self.contexts.append(context);self.phase_entries.append(a)
  def pop():assert self.contexts[-1] is context;self.contexts.pop()
  self.onreturn(u.reg_read(UC_MIPS_REG_RA),pop)
 def hook(self,u,a,n,d):
  if a==0x80086074 and getattr(self,'movie_boundary',None) is not None and self.movie_boundary.active:return
  if a==0x80076474:
   storeaddr=u.reg_read(UC_MIPS_REG_A0);before=bytes(u.mem_read(storeaddr&0x1fffffff,5080));preview=bytes(u.mem_read(0xe3f58,256));kind=struct.unpack_from('<I',preview)[0]>>12&1023;descriptor=bytes(u.mem_read(0x99f0c+kind*196,196));x,y,w,h=(i32(get(u,z)) for z in (0x800cd960,0x800cd964,0x800cd9e8,0x800cd9ec));bad,gx,gy=gate(before,x,y,w,h,struct.unpack_from('<I',descriptor)[0]);cash,eq,stock=(i32(get(u,z)) for z in (0x800cd9f8,0x800cd978,0x800cd8e0));es=bytearray(before);financial=get(u,0x800cd924)
   if not bad:
    es=bytearray(apply_copy(es,preview,gx,gy,w,h));month=__import__('hud_display').calendar(get(u,0x800cd93c))[1];update(es,gx,gy,0,-1,FIXTURES,PRODUCTS,IMAGES,month)
    if financial!=1:
     price=struct.unpack_from('<i',descriptor,4)[0];eq=i32(eq+price);cash=i32(cash-price);part=struct.unpack_from('<I',preview,24)[0];image=part>>12&1023;qty=part>>24&127
     if image:
      pid=product_image(image,IMAGES);base,factor=PRODUCTS[pid];cost=i32(truncdiv(i32(base*factor),100)*qty);stock=i32(stock+cost);cash=i32(cash-cost)
   def check_placement():
    assert bytes(u.mem_read(storeaddr&0x1fffffff,5080))==bytes(es) and [get(u,z) for z in (0x800cd9f8,0x800cd978,0x800cd8e0)]==[z&0xffffffff for z in (cash,eq,stock)] and u.reg_read(UC_MIPS_REG_V0)==bad,('placement model',kind,bad,[get(u,z) for z in (0x800cd9f8,0x800cd978,0x800cd8e0)],[z&0xffffffff for z in (cash,eq,stock)],u.reg_read(UC_MIPS_REG_V0),[(i,a,b) for i,(a,b) in enumerate(zip(bytes(u.mem_read(storeaddr&0x1fffffff,5080)),bytes(es))) if a!=b][:8])
    self.placement_checks.append([kind,financial,bad,gx,gy,w,h,cash,eq,stock,hashlib.sha256(es).hexdigest()])
   self.onreturn(u.reg_read(UC_MIPS_REG_RA),check_placement);return
  if a==0x8004095c:
   style=struct.unpack('<h',u.mem_read(0xcd8f8,2))[0];flags=struct.unpack('<H',u.mem_read(0xcd8e4,2))[0];state=bytes(u.mem_read(0x143fc0,12));prior=bytes(u.mem_read(0xdf0a0,4096));buffer=bytes(u.mem_read(0x12aa00,1024));bg=bytes(u.mem_read(0xd8f88,72));expected= hud(get(u,0x800cd93c),get(u,0x800cd9f8),get(u,0x800cd904),style,flags,state,prior,buffer,MESSAGES)
   def check():
    text,count,font,tflags,buf,cache,calls=expected
    assert bytes(u.mem_read(0xdf0a0,4096))==text and bytes(u.mem_read(0xd8f88,72))==bars(bg) and bytes(u.mem_read(0x143fc0,12))==font and bytes(u.mem_read(0x12aa00,1024))==buf and struct.unpack('<H',u.mem_read(0xcda3e,2))[0]==count and struct.unpack('<H',u.mem_read(0xcd8e4,2))[0]==tflags
    self.hud_checks+=1
   self.onreturn(u.reg_read(UC_MIPS_REG_RA),check);return
  if a==0x80018a5c:
   c=self.contexts[-1] if self.contexts else None;raw=0
   if c:
    assert c['tick']<len(c['raws']),('raws exhausted',hex(c['address']),c['tick'],self.phase_entries);raw=c['raws'][c['tick']];c['tick']+=1
   put(u,0x800cd9d8,raw);mask=get(u,0x800cd9dc);assert not mask&1,'tiled background excluded explicitly';counts={addr:struct.unpack('<H',u.mem_read(addr&0x1fffffff,2))[0] for bit,base,addr,fix,depth in GROUPS if addr};links=[0xffffff]*16;stream=bytearray();draw=[]
   for fn,base,ot,depth in dispatch(mask,self.buffer,counts,4096):
    assert fn==0x80084830;record=bytes(u.mem_read(base&0x1fffffff,36));part=packet(record,160,120,links[depth]);draw.append((base,depth,bool(part)))
    if part:links[depth]=(self.buf+len(stream))&0xffffff;stream.extend(part)
   assert len(stream)<getattr(self,'packet_capacity',65536)-16;self.expected_stream=bytes(stream);self.expected_links=links;self.current_frame=[mask,raw,c['address'] if c else 0,draw];return
  if a in SDK:
   value=self.buffer if a==0x80084fac else 0
   if a==0x800856c0:put(u,0x800e3bf8,self.buf);u.mem_write(self.buf&0x1fffffff,bytes(getattr(self,'packet_capacity',65536)));u.mem_write(self.table&0x1fffffff,struct.pack('<16I',*([0xffffff]*16)))
   elif a==0x80085338:
    assert bytes(u.mem_read(self.buf&0x1fffffff,len(self.expected_stream)+16))==self.expected_stream+bytes(16) and bytes(u.mem_read(self.table&0x1fffffff,64))==struct.pack('<16I',*self.expected_links) and get(u,0x800e3bf8)==self.buf+len(self.expected_stream)
    self.frames.append(self.current_frame+[len(self.expected_stream),hashlib.sha256(self.expected_stream).hexdigest()])
   u.reg_write(UC_MIPS_REG_V0,value);u.reg_write(UC_MIPS_REG_PC,u.reg_read(UC_MIPS_REG_RA));return
  args=[u.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)];si=lambda v:v-0x100000000 if v&0x80000000 else v
  if a==0x8008ed1c:self.sounds.append(('track_stop',si(args[0]),si(args[1])))
  elif a==0x8008ea7c:self.sounds.append(('track_play',si(args[0]),si(args[1]),args[2],args[3]))
  else:assert args[1:3]==[0,0];self.sounds.append(('stop_command',args[0]))
  u.reg_write(UC_MIPS_REG_V0,0);u.reg_write(UC_MIPS_REG_PC,u.reg_read(UC_MIPS_REG_RA))
 def dispose(self):
  for h in self.hooks+list(self.returnhooks.values()):self.u.hook_del(h)
  self.hooks=[];self.returnhooks={}
