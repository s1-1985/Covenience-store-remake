"""Original town image producer/background/clock color checks during land input."""
from check_machine import *
from caller_connection_harness import Memory
from town_tile_image import tile_image
from background_init import initialize_background
from town_daylight import rgb
from unicorn import UC_HOOK_CODE
import hashlib
class LandTownMonitor:
 def __init__(self,u,runner):
  self.u=u;self.runner=runner;self.hooks=[];self.checks=[];self.tiles=[];self.active=False
  for a in (0x8006dbf0,0x80019870,0x80019460,0x80066234):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.observe,begin=a,end=a))
 def observe(self,u,a,n,d):
  m=Memory(u)
  if a==0x8006dbf0:
   assert not self.active;self.active=True;self.tiles=[];self.stores=[m.read(0x12b2f8+j*5080,5080) for j in range(10)]
   def check():
    assert len(self.tiles)==3000;h,b=self.background;b=bytearray(b)
    if get(u,0x800cd9a4)==1:
     struct.pack_into('<H',b,6,(struct.unpack_from('<H',b,6)[0]+12)&65535);struct.pack_into('<2H',b,28,2048,2048)
    else:
     sx,sy=struct.unpack('<2h',m.read(0xcd7d6,4));struct.pack_into('<2H',b,4,(-(sx-10)*8)&65535,(-(sy-14)*8)&65535)
    assert m.read(0xe3da8,16)==h and m.read(0xe4410,36)==bytes(b);self.checks.append([a,get(u,0x800cd9a4),len(self.tiles),hashlib.sha256(struct.pack('<3000H',*self.tiles)+h+bytes(b)).hexdigest()]);self.active=False
   self.runner.onreturn(u.reg_read(UC_MIPS_REG_RA),check)
  elif a==0x80019870 and self.active:
   args=[u.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)];retained=struct.unpack('<H',m.read(u.reg_read(UC_MIPS_REG_SP)-16,2))[0];want,_=tile_image(*args,self.stores,retained);self.tiles.append(want&65535)
   def check():assert u.reg_read(UC_MIPS_REG_V0)&65535==want&65535
   self.runner.onreturn(u.reg_read(UC_MIPS_REG_RA),check)
  elif a==0x80019460 and self.active:
   source=bytes([60,50,8,8])+struct.pack('<3000H',*self.tiles);assert m.read(0x146030,6004)==source;self.background=initialize_background(source,0x801fd008,0,m.read(0xe3da8,16),m.read(0xe4410,36),0x80146030)
  elif a==0x80066234:
   before=bytearray(m.read(0xe4410,36));before[16:19]=rgb(get(u,0x800cd93c),before[16:19])
   def check():assert m.read(0xe4410,36)==bytes(before);self.checks.append([a,get(u,0x800cd93c),list(before[16:19])])
   self.runner.onreturn(u.reg_read(UC_MIPS_REG_RA),check)
 def dispose(self):
  for h in self.hooks:self.u.hook_del(h)
