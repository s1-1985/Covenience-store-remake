"""Independent original spawn core checks on source-initialized stores."""
from check_machine import *
from caller_connection_harness import Memory
from active_main_fixture import profiles,calendar as season_calendar,times,appearances
from customer_spawn_core import spawn
from hud_display import calendar
from unicorn import UC_HOOK_CODE
class SourceSpawnMonitor:
    def __init__(self,u):
        self.u=u;self.pending=None;self.checks=[];self.hooks=[]
        def observe(z,a,n,d):
            if a==0x800319ac:
                assert self.pending is None
                p=z.reg_read(UC_MIPS_REG_A0);slot=(p-0x8012b2f8)//5080;q=get(z,0x800cecec+slot*2948)
                store=bytearray(Memory(z).read(p,5080));summary=bytearray(Memory(z).read(q,168))
                flags=struct.unpack('<H',z.mem_read(0xcd790,2))[0];c=calendar(get(z,0x800cd93c))
                seed,flags,info=spawn(store,summary,get(z,0x800d6270),flags,c[1],c[2],c[3],profiles,season_calendar,times,appearances)
                self.pending=(p,q,store,summary,seed,flags,info,slot);return
            if self.pending is None:return
            p,q,store,summary,seed,flags,info,slot=self.pending
            if a != (0x800320cc if info['reason']=='created' else 0x80032814):return
            assert Memory(z).read(p,5080)==store and Memory(z).read(q,168)==summary,('source spawn bytes',slot,info)
            assert get(z,0x800d6270)==seed and struct.unpack('<H',z.mem_read(0xcd790,2))[0]==flags
            self.checks.append(dict(clock=get(z,0x800cd93c),store_slot=slot,seed=seed,**info));self.pending=None
        for a in (0x800319ac,0x800320cc,0x80032814):self.hooks.append(u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a))
    def dispose(self):
        assert self.pending is None
        for h in self.hooks:self.u.hook_del(h)
