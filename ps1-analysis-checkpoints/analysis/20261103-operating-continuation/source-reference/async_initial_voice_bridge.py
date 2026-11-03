"""Schedule real CD/input callbacks at supplied VSync SDK boundaries in original menus.

This models callback installation/context restoration, not BIOS IRQ timing.
No nested emu_start: the MIPS PC visits callback then a context-return hook.
"""
from newgame_voice_bridge import *
from cd_audio_control import step
from cd_position import encode,decode
from input_control import interrupt,GP
TRAMPOLINE=0x80001080
REGS=list(range(UC_MIPS_REG_0,UC_MIPS_REG_31+1))+[UC_MIPS_REG_HI,UC_MIPS_REG_LO]

class AsyncInitialVoice(NativeInitialVoice):
 def __init__(self,u,runner,base=None,profile=0):
  self.registered=0x8001310c;self.updating=False;self.profile=profile;self.updates=[];self.update_trace=[];self.poll_number=0;self.nested=False;self.stop_checks=[];self.scheduled=0
  super().__init__(u,runner,returned=self.registered,base=base)
  for a in (0x80089ca4,0x80085da0,0x80089c24,0x8001310c,0x80064550,TRAMPOLINE):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.hook,begin=a,end=a))
 def hook(self,u,a,n,d):
  a0=u.reg_read(UC_MIPS_REG_A0);a1=u.reg_read(UC_MIPS_REG_A1)
  if a==0x80064740:
   self.returned=self.registered;return super().hook(u,a,n,d)
  if a==0x80064550:
   state={k:get(u,v) for k,v in ADDR.items()};mode=bytes(u.mem_read(0xd6130,4));expected=dict(state)
   if not state['disabled'] and state['status']:expected['status']=0
   registered=self.registered
   def check():
    assert all(get(u,v)==expected[k] for k,v in ADDR.items()) and bytes(u.mem_read(0xd6130,4))==mode and self.registered==registered
    self.stop_checks.append([state['status'],expected['status'],registered])
   self.onreturn(u.reg_read(UC_MIPS_REG_RA),check);return
  if a==0x80089ca4:
   assert not self.updating and self.active is None
   self.updating=True;self.update_trace=[];self.poll_number=0;self.scheduled+=1;self.saved={r:u.reg_read(r) for r in REGS};self.saved[UC_MIPS_REG_V0]=0;self.resume=u.reg_read(UC_MIPS_REG_RA);self.irq_sp=u.reg_read(UC_MIPS_REG_SP);self.stack_base=(self.irq_sp&0x1fffffff)-512;self.stack=bytes(u.mem_read(self.stack_base,512));self.before={k:get(u,v) for k,v in ADDR.items()};self.before['mode']=bytes(u.mem_read(0xd6130,4));self.expected=dict(self.before);self.raw=get(u,0x800cd9d8);self.inp={p:get(u,p) for p in (GP+4,GP+8,0x800cd9d8,0x800cd7e0,0x801398b8)}
   # Source-reachable end position, deterministic ready/error response profile.
   self.reported=self.before['end'];self.result=5 if self.profile and self.scheduled%7==0 else 2
   if self.registered==SELF:
    self.wanted=step(self.expected,[self.result,2],decode(encode(self.reported)),encode(self.before['start'])+bytes(u.mem_read(((self.irq_sp-0x1d)&0x1fffffff),1)))
   else:assert self.registered==0x8001310c;self.wanted=[('callback',self.registered)]
   self.expected_registered=self.registered;wanted=[]
   for x in self.wanted:
    if x[0] in ('position','read_position'):continue
    if x[0]=='restore_callback':self.expected_registered=x[1];wanted.append(('register_callback',x[1]))
    elif x[0]=='callback':wanted.extend((x,('pad',self.raw)));interrupt(self.inp,self.raw)
    else:wanted.append(x)
   self.wanted=wanted;u.reg_write(UC_MIPS_REG_RA,TRAMPOLINE);u.reg_write(UC_MIPS_REG_PC,self.registered);return
  if a==TRAMPOLINE:
   assert self.updating
   assert self.update_trace==self.wanted,(self.update_trace,self.wanted)
   assert all(get(u,p)==self.expected[k] for k,p in ADDR.items()) and bytes(u.mem_read(0xd6130,4))==self.expected['mode']
   assert all(get(u,p)==v for p,v in self.inp.items()) and self.registered==self.expected_registered
   self.updates.append(dict(before_status=self.before['status'],after_status=self.expected['status'],registered=self.registered,raw=self.raw,input_words=[self.inp[p] for p in self.inp],state={k:v.hex() if isinstance(v,bytes) else v for k,v in self.expected.items()},calls=[[v.hex() if isinstance(v,bytes) else v for v in x] for x in self.update_trace]))
   u.mem_write(self.stack_base,self.stack)
   for r,value in self.saved.items():u.reg_write(r,value)
   self.updating=False;u.reg_write(UC_MIPS_REG_PC,self.resume);return
  if a==0x8001310c:
   assert self.updating;self.update_trace.append(('callback',a));return
  if a==0x80089c24:
   assert self.updating and a0==0;self.update_trace.append(('pad',self.raw));value=self.raw
  elif a==0x80085da0:
   assert self.updating and a0==1;value=self.result if self.poll_number==0 else 2;self.poll_number+=1;self.update_trace.append(('sync',a0));u.mem_write(a1&0x1fffffff,bytes(5)+encode(self.reported))
  elif a==0x80089f28:
   old=self.registered;self.registered=a0
   if not self.updating:
    assert self.returned==old;return super().hook(u,a,n,d)
   self.update_trace.append(('register_callback',a0));value=old
  elif a==0x80085f48 and self.updating:
   length=4 if a0==13 or (a0==2 and a1==self.irq_sp-0x20) else 1
   self.update_trace.append(('command',a0,bytes(u.mem_read(a1&0x1fffffff,length)) if a1 else None));value=1
  else:return super().hook(u,a,n,d)
  u.reg_write(UC_MIPS_REG_V0,value);u.reg_write(UC_MIPS_REG_PC,u.reg_read(UC_MIPS_REG_RA))
