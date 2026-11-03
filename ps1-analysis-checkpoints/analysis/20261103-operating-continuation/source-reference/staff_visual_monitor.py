"""Raw string and portrait buffer generation during complete staff UI."""
from check_machine import *
from caller_connection_harness import Memory
from verify_premises_numbered_intro import raw_words
from sprite_record import record
from icon_layout import portrait48
from unicorn import UC_HOOK_CODE
import hashlib
class StaffVisualMonitor:
 def __init__(self,u,runner):
  self.u=u;self.runner=runner;self.checks=[];self.hooks=[]
  for a in (0x80067338,0x800675dc):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.observe,begin=a,end=a))
 def observe(self,u,a,n,d):
  m=Memory(u);args=[u.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)]
  if a==0x80067338:
   words=raw_words(m,args[2]);src=struct.pack('<'+'H'*len(words),*words);prior=m.read(0x800e3948,256);expected=src+prior[len(src):]
   def check():assert m.read(0x800e3948,256)==expected;self.checks.append([a,len(words),hashlib.sha256(expected).hexdigest()])
  else:
   index=struct.unpack('<h',m.read(0x800cda34,2))[0];base=0x800dae60;expected=bytearray(m.read(base,32*36));x,y,code,color=args;x=(x+32768)%65536-32768;y=(y+32768)%65536-32768;offset=index*36;expected[offset:offset+36]=record(expected[offset:offset+36],*portrait48(x,y,code,color))
   def check():assert m.read(base,len(expected))==bytes(expected) and m.read(0x800cda34,2)==struct.pack('<H',(index+1)&65535);self.checks.append([a,index,hashlib.sha256(expected).hexdigest()])
  self.runner.onreturn(u.reg_read(UC_MIPS_REG_RA),check)
 def dispose(self):
  for h in self.hooks:self.u.hook_del(h)
