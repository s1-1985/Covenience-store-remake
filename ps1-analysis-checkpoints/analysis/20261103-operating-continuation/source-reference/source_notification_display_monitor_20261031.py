"""Native3FF00 outer notification policy with original drawing/audio children retained."""
from check_machine import *
from caller_connection_harness import Memory
from notification_display import control
from unicorn import UC_HOOK_CODE
from recovered import i32
CALLS={0x80064e4c:1,0x80062a4c:2,0x80065974:0,0x80018940:2,0x80067338:3,0x8006c048:2,0x8006c8b0:2}
class SourceNotificationDisplayMonitor:
 def __init__(self,u,runner):
  self.u=u;self.active=None;self.checks=[]
  def observe(z,a,n,d):
   m=Memory(z);ra=z.reg_read(UC_MIPS_REG_RA)
   if a==0x8003ff00:
    assert self.active is None
    active=m.word(0x801398b4);timer=m.word(0x801398b8);slot=m.word(0x801398b0)
    mode=m.byte(0x80137970+slot*160+2) if slot<50 else 0
    args=[active,timer,m.word(0x800b8cb4),m.word(0x800b8cac),i32(m.word(0x800e3be4)),mode,m.word(0x800cd97c),*struct.unpack('<2H',m.read(0x800e3bd8,4))]
    ea,et,out,calls=control(*args);wanted=[[p,[v&0xffffffff for v in q]] for p,q in calls]
    entry=dict(clock=m.word(0x800cd93c),before_active=active,timer=timer,audio_disabled=args[2],audio_status=args[3],slot=slot,mode=mode,outcome=out,calls=[],vsync_callbacks=[])
    self.active=entry;frames0=len(runner.frames);seed=m.word(0x800d6270);queue=m.read(0x80137970,8000)
    def check():
     assert entry['calls']==wanted,('notification display calls',entry,wanted)
     actual_timer=max(0,et-len(entry['vsync_callbacks'])) if i32(et)>0 else et
     assert m.word(0x801398b4)==ea and m.word(0x801398b8)==actual_timer,('notification state',entry,ea,actual_timer,m.word(0x801398b4),m.word(0x801398b8),len(runner.frames)-frames0)
     assert m.word(0x800d6270)==seed and m.read(0x80137970,8000)==queue and len(runner.frames)==frames0
     entry['after_active']=ea;entry['after_timer']=actual_timer;self.checks.append(entry);self.active=None
    runner.onreturn(ra,check);return
   if a==0x80089ca4:
    # Earlier AsyncInitialVoice hooks may already have replaced RA with their
    # callback-return trampoline; this is adapter context, not a source JAL xref.
    if self.active is not None:self.active['vsync_callbacks'].append(dict(caller=hex(ra),timer_before=m.word(0x801398b8)))
    return
   if self.active is not None and 0x8003ff00<=ra<0x8004095c:
    args=[z.reg_read(v) for v in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)[:CALLS[a]]]
    self.active['calls'].append([a,args])
  self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x8003ff00,0x80089ca4,*CALLS)]
 def dispose(self):
  assert self.active is None
  for h in self.hooks:self.u.hook_del(h)
