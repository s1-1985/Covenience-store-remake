"""Original52270 mode2: resource metadata, sprite/window/message/timed draw contracts."""
from check_machine import *
from caller_connection_harness import Memory
from unicorn import UC_HOOK_CODE
class SourceSpecialPeriodMonitor:
 def __init__(self,u,runner,expected_frames):
  self.u=u;self.active=None;self.checks=[]
  def observe(z,a,n,d):
   m=Memory(z);ra=z.reg_read(UC_MIPS_REG_RA)
   if a==0x80052270:
    assert self.active is None
    args=[z.reg_read(v) for v in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)]
    assert args==[2,0,0],('special screen mode contract',args)
    frame0=len(runner.frames);frozen=[(p,m.read(p,size)) for p,size in [(0x8012b2f8,50800),(0x80143ff8,2100),(0x80137970,8000),(0x800d6270,4),(0x800cd93c,4),(0x800cd9f8,8),(0x800e4020,120),(0x800cd8c8,4),(0x800cd938,4)]]
    entry=dict(timed=0,resource=[],sprites=[],windows=[],messages=[],sound=[]);self.active=entry
    def check():
     assert entry['timed']==120 and len(runner.frames)-frame0==expected_frames,('special frames',entry['timed'],len(runner.frames)-frame0,expected_frames)
     assert entry['resource']==[16] and entry['messages']==[[80,64,470]]
     assert entry['sprites']==[[0xffc0ff90,0x00200020,0xe0c0001d,0x01ef0000]]
     assert entry['windows']==[[0x00300030,0x0004000e,0]] and entry['sound']==[58]
     assert all(m.read(p,len(b))==b for p,b in frozen)
     entry['frames']=len(runner.frames)-frame0;entry['gameplay_preserved']=True;self.checks.append(entry);self.active=None
    runner.onreturn(ra,check);return
   if self.active is None:return
   e=self.active
   if a==0x80013f7c and ra==0x800522b0:e['resource'].append(z.reg_read(UC_MIPS_REG_A0))
   if a==0x80064e4c and ra==0x80052aa4:e['sound'].append(z.reg_read(UC_MIPS_REG_A0))
   if a==0x80018a5c and ra==0x80052c5c:e['timed']+=1
   if a==0x80041630 and ra==0x80052b44:
    sp=z.reg_read(UC_MIPS_REG_SP);e['sprites'].append([z.reg_read(UC_MIPS_REG_A2),z.reg_read(UC_MIPS_REG_A3),m.word(sp+16),m.word(sp+20)])
   if a==0x80017b18 and ra==0x80052c08:e['windows'].append([z.reg_read(UC_MIPS_REG_A0),z.reg_read(UC_MIPS_REG_A1),z.reg_read(UC_MIPS_REG_A2)&255])
   if a==0x8004e494 and ra==0x80052c34:e['messages'].append([z.reg_read(v) for v in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)])
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x80052270,0x80013f7c,0x80064e4c,0x80018a5c,0x80041630,0x80017b18,0x8004e494)]
 def dispose(self):
  assert self.active is None
  for h in self.hooks:self.u.hook_del(h)
