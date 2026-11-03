"""Check real midnight29334 against the prior independent full finance model."""
from check_machine import *
from caller_connection_harness import Memory
from finance_close import close
from finance_notification_text_20261030 import FinanceNotificationText
from unicorn import UC_HOOK_CODE
import hashlib
BYTE={0x800cd835,0x800cd948,*range(0x800e43d0,0x800e43d0+60)}
HALF={0x800cd9e0}
ADDR=[0x800ce610,0x800ce60c,0x800ce618,0x800ce614,0x800ce608,0x800cda00,0x800cd8b8,0x800d6270,
      0x800cd9f8,0x800cd9fc,0x800cd9b4,0x800cd938,*sorted(BYTE),*sorted(HALF)]+[a+j*4 for a in (0x800d8f68,0x800da970,0x800df080) for j in range(8)]+[0x800e3c28+j*4 for j in range(60)]
class SourceFinanceMonitor:
    def __init__(self,u,runner,pending_display_frames=None,special_display_frames=None):
        self.u=u;self.checks=[];self.time_gates=0;self.pending=None;self.hooks=[];m=Memory(u)
        self.ui_active=False;self.ui_checks=[]
        self.pending_display_frames=pending_display_frames
        self.special_monitor=None;self.ui_kind=None
        if special_display_frames is not None:
            from source_special_period_monitor_20261031 import SourceSpecialPeriodMonitor
            self.special_monitor=SourceSpecialPeriodMonitor(u,runner,special_display_frames)
        schedules=[list(m.read(0x80099de5+j*45,24)) for j in range(7)]
        rates=[struct.unpack('<i',m.read(0x80099f14+j*196,4))[0] for j in range(53)]
        def value(a):return int.from_bytes(m.read(a,1 if a in BYTE else 2 if a in HALF else 4),'little')
        def observe(z,a,n,d):
            if a==0x80052270 and self.pending:
                assert special_display_frames is not None
                actual=(a,*[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)])
                assert actual==self.expected_ui[len(self.observed_ui)]
                self.observed_ui.append(actual);self.ui_active=True;self.ui_kind='special'
                def check_special():
                    self.ui_checks.append(dict(call=list(actual),frames=special_display_frames,branch='special_period_mode2'))
                    self.ui_active=False;self.ui_kind=None
                # Registered after the primitive monitor's callback; callbacks
                # are LIFO, so validate completion at enclosing finance return.
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check_special)
                return
            if a==0x800140e8 and self.ui_active and self.ui_kind=='pending':
                assert self.pending_display_frames is not None
                key=[z.reg_read(UC_MIPS_REG_A0),z.reg_read(UC_MIPS_REG_A1)]
                assert key==[18,0];self.ui_resources.append(key);return
            if a==0x80018a5c and self.ui_active and z.reg_read(UC_MIPS_REG_RA)==0x8005323c:
                self.ui_timed+=1
            if a==0x80052dbc and self.pending:
                actual=(a,z.reg_read(UC_MIPS_REG_A0))
                assert actual==self.expected_ui[len(self.observed_ui)]
                self.observed_ui.append(actual);self.ui_active=True;self.ui_kind='pending'
                self.ui_frames_before=len(runner.frames);self.ui_timed=0;self.ui_resources=[]
                total=sum(struct.unpack('<I',m.read(0x8012b2f8+k*5080+0x1188,4))[0]
                          for k in range(10) if m.byte(0x8012b2f8+k*5080) and
                          not struct.unpack('<H',m.read(0x8012b2f8+k*5080+4,2))[0]&0x8000)&0xffffffff
                assert total<10000 or self.pending_display_frames is not None,('52DBC display requires an explicit frame/input contract',total)
                frozen=[(p,m.read(p,n)) for p,n in ((0x8012b2f8,50800),(0x80143ff8,2100),
                        (0x80137970,8000),(0x800e4020,120),(0x800d6270,4),(0x800cd9f8,8),(0x800cd8c8,4),(0x800cd93c,4))]
                if total<10000:frozen.append((0x800cd938,m.read(0x800cd938,4)))
                def check_ui():
                    assert all(m.read(p,len(b))==b for p,b in frozen)
                    frames=len(runner.frames)-self.ui_frames_before
                    if total<10000:assert frames==self.ui_timed==0 and not self.ui_resources
                    else:
                        assert frames==self.pending_display_frames and self.ui_timed==120 and self.ui_resources==[[18,0]]
                        assert value(0x800cd938)==total//10000
                    self.ui_checks.append(dict(call=list(actual),own_visitors=total,frames=frames,timed_frames=self.ui_timed,
                                              branch='below10000_no_display' if total<10000 else 'display_with_explicit_input'))
                    self.ui_active=False;self.ui_kind=None
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check_ui)
                return
            if a==0x80029334:
                assert self.pending is None
                if value(0x800ce618) or value(0x800ce614):self.time_gates+=1;return
                stores=[bytearray(m.read(0x8012b2f8+j*5080,5080)) for j in range(10)]
                staff=[bytearray(m.read(0x80143ff8+j*60,60)) for j in range(35)]
                order=list(struct.unpack('<10i',m.read(0x800ce61c,40)));state={p:value(p) for p in ADDR};before=dict(state)
                queue=bytearray(m.read(0x80137970,8000));text=m.read(0x800e4020,120)
                notifier=FinanceNotificationText(text,value(0x800cd8c8),m.read,value(0x800cd948))
                total=sum(struct.unpack_from('<I',s,0x1188)[0] for s in stores if s[0] and not struct.unpack_from('<H',s,4)[0]&0x8000)&0xffffffff
                def ui_effect(request,current_state):
                    if total>=10000:
                        assert self.pending_display_frames is not None,('pending display contract missing',total)
                        current_state[0x800cd938]=total//10000
                events,ui=close(stores,staff,order,state,queue,text,schedules,rates,notification_text=notifier,pending_ui=ui_effect)
                assert not ui or all(x[0]==0x80052dbc or (x[0]==0x80052270 and special_display_frames is not None) for x in ui),('finance UI requires additional independent contract',events,ui,total)
                self.expected_ui=list(ui);self.observed_ui=[]
                self.pending=True
                def check():
                    assert m.read(0x8012b2f8,50800)==b''.join(stores),('midnight stores',get(z,0x800cd93c))
                    assert m.read(0x80143ff8,2100)==b''.join(staff) and m.read(0x80137970,8000)==queue
                    assert all(value(p)==v for p,v in state.items()),('midnight state',[(hex(p),value(p),v) for p,v in state.items() if value(p)!=v])
                    assert m.read(0x800e4020,120)==notifier.builder.data and value(0x800cd8c8)==notifier.builder.pos,('finance notification text',notifier.calls)
                    assert self.observed_ui==self.expected_ui and not self.ui_active
                    if any(x[0]==0x80052270 for x in self.expected_ui):assert self.special_monitor.checks and not self.special_monitor.active
                    self.checks.append(dict(clock=get(z,0x800cd93c),calendar=[state[p] for p in (0x800ce608,0x800ce60c,0x800ce610,0x800ce614,0x800ce618)],
                                            store_order=order,cash_before=[before[0x800cd9f8],before[0x800cd9fc]],cash_after=[state[0x800cd9f8],state[0x800cd9fc]],
                                            stores_sha256=hashlib.sha256(b''.join(stores)).hexdigest(),staff_sha256=hashlib.sha256(b''.join(staff)).hexdigest(),events=events,UI=ui,
                                            notification_text_calls=notifier.calls,notification_text_sha256=hashlib.sha256(notifier.builder.data).hexdigest()))
                    self.pending=None
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
        for a in (0x80029334,0x80052dbc,0x80052270,0x800140e8,0x80018a5c):
            self.hooks.append(u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a))
    def dispose(self):
        assert self.pending is None
        if self.special_monitor:self.special_monitor.dispose()
        for h in self.hooks:self.u.hook_del(h)
