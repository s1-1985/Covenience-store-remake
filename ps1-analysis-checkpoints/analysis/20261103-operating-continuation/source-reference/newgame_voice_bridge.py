"""Nativeinitial spokenprompt dispatch/start; CD callback/command SDK endpoints only."""
from check_machine import *
from caller_connection_harness import Memory
from cd_audio_start import start
from cd_audio_control import SELF
from unicorn import UC_HOOK_CODE
import json
R=Path(__file__).resolve().parent
B=EXE.read_bytes();off=0x800b8cb8-0x80010000+2048;TABLE=[struct.unpack_from('<III',B,off+j*12) for j in range(131)]
ADDR={'disabled':0x800b8cb4,'status':0x800b8cac,'callback':0x800b8cb0,'start':0x800d6118,'end':0x800d611c,'current':0x800d6120,'retry':0x800d612c,'delay':0x800d6138}
class NativeInitialVoice:
 def __init__(self,u,runner=None,returned=SELF,base=1513):
  self.u=u;self.m=Memory(u);self.runner=runner;self.returned=returned;self.hooks=[];self.returnhooks={};self.callbacks={};self.starts=[];self.trace=[];self.active=None
  if base is not None:put(u,0x800d6134,base)
  self.base=get(u,0x800d6134)
  for a in(0x80064740,0x80089f28,0x80085f48):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.hook,begin=a,end=a))
 def onreturn(self,a,fn):
  if self.runner:self.runner.onreturn(a,fn);return
  if a not in self.returnhooks:self.returnhooks[a]=self.u.hook_add(UC_HOOK_CODE,lambda z,a,n,d:self.flush(a),begin=a,end=a)
  self.callbacks.setdefault(a,[]).append(fn)
 def flush(self,a):
  while self.callbacks.get(a):self.callbacks[a].pop()()
 def hook(self,z,a,n,d):
  m=self.m;a0=z.reg_read(UC_MIPS_REG_A0);a1=z.reg_read(UC_MIPS_REG_A1)
  if a==0x80064740:
   assert a0 in getattr(self,'allowed_voices',(97,98)),('initial voice id',a0);s={k:m.word(v) for k,v in ADDR.items()};s['mode']=m.read(0x800d6130,4);expected=start(s,a0,TABLE,self.base,self.returned);begin=len(self.trace);self.active=a0
   def check():
    assert all(m.word(v)==s[k] for k,v in ADDR.items()) and m.read(0x800d6130,4)==s['mode'] and m.word(0x800d6134)==self.base
    want=[x for x in expected if x[0]!='stop_command'];assert self.trace[begin:]==[[*x[:-1],x[-1].hex()] if x[0]=='command' else list(x) for x in want],(self.trace[begin:],want)
    self.starts.append([a0,{k:(v.hex() if isinstance(v,bytes) else v) for k,v in s.items()},self.trace[begin:]]);self.active=None
   self.onreturn(z.reg_read(UC_MIPS_REG_RA),check);return
  assert self.active is not None
  if a==0x80089f28:assert a0==SELF;self.trace.append(['register',a0]);value=self.returned
  else:assert a0==13;self.trace.append(['command',a0,m.read(a1,4).hex()]);value=1
  z.reg_write(UC_MIPS_REG_V0,value);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA))
 def dispose(self):
  for h in self.hooks+list(self.returnhooks.values()):self.u.hook_del(h)
