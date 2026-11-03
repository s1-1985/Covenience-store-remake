"""Independent window, ordinary MSG text and rectangle producers in menus."""
from check_machine import *
from caller_connection_harness import Memory
from category_frame_harness import MESSAGES
from text_render import render_selected
from text_controls import ExpandBuffer,expand_stream
from message_banks_20261031 import source_messages
from recovered import i32
from window_tiles import window,apply_window
from settings_rectangles import rectangle,apply_records
from unicorn import UC_HOOK_CODE
import hashlib
class MenuGeneratorMonitor:
 def __init__(self,u,runner,rect_capacity=32,text_capacity=4096,window_capacity=256):
  self.u=u;self.runner=runner;self.rect_capacity=rect_capacity;self.text_capacity=text_capacity;self.window_capacity=window_capacity;self.checks=[];self.hooks=[]
  for a in (0x80017b18,0x800155d0,0x800182d0):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.observe,begin=a,end=a))
 def observe(self,u,a,n,d):
  m=Memory(u);a0=u.reg_read(UC_MIPS_REG_A0);a1=u.reg_read(UC_MIPS_REG_A1);a2=u.reg_read(UC_MIPS_REG_A2)
  if a==0x80017b18:
   addr=0xe0fe0;expected=bytearray(m.read(addr,self.window_capacity*36));apply_window(expected,0,window(a0&65535,a0>>16,a1&65535,a1>>16,a2&255));count=(a1&65535)*(a1>>16);counter=0xcda46
   def check():assert m.read(addr,len(expected))==bytes(expected) and m.read(counter,2)==struct.pack('<H',count);self.checks.append([a,count,hashlib.sha256(expected).hexdigest()])
  elif a==0x800182d0:
   addr=0x14a180;expected=bytearray(m.read(addr,self.rect_capacity*36));calls=rectangle(a0&65535,a0>>16,a1&65535,a1>>16,a2&255,u.reg_read(UC_MIPS_REG_A3)&255);apply_records(expected,0,calls);count=len(calls)
   def check():assert m.read(addr,len(expected))==bytes(expected) and u.reg_read(UC_MIPS_REG_V0)==count;self.checks.append([a,count,hashlib.sha256(expected).hexdigest()])
  else:
   index=a0&65535;bank=source_messages(m.read,m.word(0x800cd888));source=bank['messages'][index];buffer=bytearray(m.read(0x12aa00,1024));eb=ExpandBuffer(buffer,0);variables={j:i32(m.word(0x800e4000+4*j)) for j in range(16)};twos={j:i32(m.word(0x8014c270+4*j)) for j in range(16)}
   def words(address):
    out=[]
    for j in range(256):
     v=struct.unpack('<H',m.read(address+2*j,2))[0];out.append(v)
     if v==0x40ff:return out
    raise AssertionError('menu text terminator')
   strings={}
   if 0x400a in source:strings[(0x400a,0)]=words(0x800e3948)
   if 0x4006 in source:strings[(0x4006,0)]=words(0x8012b2c8)
   used=expand_stream(source,eb,{'variable':variables,'two':twos},strings,struct.unpack('<h',m.read(0xcd8e6,2))[0],i32(get(u,0x800cd938)));buffer=eb.data;codes=list(struct.unpack_from('<'+'H'*eb.pos,buffer,64))
   style=struct.unpack('<h',m.read(0xcd8f8,2))[0];flags=struct.unpack('<H',m.read(0xcd8e4,2))[0];start=struct.unpack('<H',m.read(0xcda3c,2))[0];prior=m.read(0xdcc80,self.text_capacity);tail,count,state,flags=render_selected(codes,style,a0>>16,a1&65535,flags,m.read(0x143fc0,12),prior[start*36:],False);expected=prior[:start*36]+tail
   def check():assert m.read(0xdcc80,self.text_capacity)==expected and m.read(0x12aa00,1024)==bytes(buffer) and m.read(0x143fc0,12)==state and m.read(0xcd8e4,2)==struct.pack('<H',flags) and m.read(0xcda3c,2)==struct.pack('<H',start+count);self.checks.append([a,index,count,hashlib.sha256(expected).hexdigest()])
  self.runner.onreturn(u.reg_read(UC_MIPS_REG_RA),check)
 def dispose(self):
  for h in self.hooks:self.u.hook_del(h)
