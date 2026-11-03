"""3ECD8 original event reservation: exact queue, return slot, caller and text."""
from check_machine import *
from caller_connection_harness import Memory
from event_queue import reserve
from recovered import i32
from unicorn import UC_HOOK_CODE
import hashlib
class SourceEventReservationMonitor:
    def __init__(self,u,runner):
        self.u=u;self.checks=[];self.pending=0
        def observe(z,a,n,d):
            m=Memory(z);q=bytearray(m.read(0x80137970,8000));text=m.read(0x800e4020,120)
            args=[i32(z.reg_read(k)) for k in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)]
            args.append(i32(m.word(z.reg_read(UC_MIPS_REG_SP)+16)))
            expected=reserve(q,*args,text);seed=m.word(0x800d6270);caller=z.reg_read(UC_MIPS_REG_RA);self.pending+=1
            def check():
                assert m.read(0x80137970,8000)==q and i32(z.reg_read(UC_MIPS_REG_V0))==expected
                assert m.word(0x800d6270)==seed
                self.checks.append(dict(clock=m.word(0x800cd93c),caller=hex(caller),args=args,slot=expected,
                                       text_sha256=hashlib.sha256(text).hexdigest(),queue_sha256=hashlib.sha256(q).hexdigest()))
                self.pending-=1
            runner.onreturn(caller,check)
        self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=0x8003ecd8,end=0x8003ecd8)]
    def dispose(self):
        assert self.pending==0
        for h in self.hooks:self.u.hook_del(h)
