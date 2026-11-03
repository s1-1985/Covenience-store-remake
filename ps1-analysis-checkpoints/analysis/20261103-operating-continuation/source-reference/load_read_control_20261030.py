"""Independent51524 call policy; native children and SDK/card boundaries remain shared.

Observe caller JAL sites (before SDK hooks can alter RA); the original delay
slots at these sites are NOPs. Result acknowledgement input is checked by the
separate InputWait/LoadConfirmation monitor.
"""
def policy(init_status,read_status,checksum_valid):
    assert 0<=init_status<=5
    calls=[]
    def call(a,*args):calls.append([a,[x&0xffffffff for x in args]])
    def draw(y,message):call(0x8004e494,64,y,message)
    def frames(n):
        for _ in range(n):call(0x80018a5c)
    call(0x80089ca4,2);call(0x80064e4c,-1);call(0x80089ca4,2)
    call(0x80018940,16,0);call(0x800157b4);call(0x8004ea68);call(0x800157b4)
    draw(64,0x1e6);draw(96,0x1e2);frames(2)
    call(0x8007b1f8,1);call(0x80089ca4,2)
    if init_status:
        call(0x800157b4);call(0x80050fc8,init_status,64,64)
        result=init_status
    else:
        call(0x800157b4);draw(64,0x1e4);frames(2);call(0x80089ca4,2)
        call(0x8007ab2c,0);call(0x80089ca4,2);call(0x8007ab2c,1);call(0x80089ca4,2)
        call(0x800157b4)
        if read_status:
            draw(80,0x1ec);result=-1
        else:
            call(0x8005188c);draw(64 if checksum_valid else 80,0x1e9 if checksum_valid else 0x1f2)
            result=0 if checksum_valid else -1
        frames(8)
    return calls,result

class LoadReadMonitor:
    def __init__(self,u,runner,init_status,read_status,checksum_valid):
        from check_machine import EXE,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_RA,UC_MIPS_REG_V0
        from unicorn import UC_HOOK_CODE
        from recovered import i32
        import struct
        self.u=u;self.hooks=[];self.checks=[];self.active=None
        statuses=init_status if isinstance(init_status,list) else [init_status]
        counts={0x80089ca4:1,0x80064e4c:1,0x80018940:2,0x800157b4:0,0x8004ea68:0,
                0x8004e494:3,0x80018a5c:0,0x8007b1f8:1,0x8007ab2c:1,0x8005188c:0,0x80050fc8:3}
        data=EXE.read_bytes();sites={}
        for a in range(0x80051524,0x8005188c,4):
            offset=a-0x80010000+2048;word=struct.unpack_from('<I',data,offset)[0]
            if word>>26==3:
                dest=0x80000000|((word&0x3ffffff)<<2)
                assert struct.unpack_from('<I',data,offset+4)[0]==0,('non-NOP delay slot',hex(a))
                if dest==0x80041374:continue
                assert dest in counts,hex(dest)
                sites[a]=dest
        def observe(z,a,n,d):
            if a==0x80051524:
                assert self.active is None
                status=statuses[min(len(self.checks),len(statuses)-1)]
                expected,result=policy(status,read_status,checksum_valid)
                self.active=[]
                def finish():
                    assert self.active==expected,('51524 calls',self.active,expected)
                    actual=i32(z.reg_read(UC_MIPS_REG_V0));assert actual==result,(actual,result)
                    self.checks.append(dict(init_status=status,read_status=read_status,checksum_valid=checksum_valid,
                                            calls=self.active,result=actual));self.active=None
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),finish)
                return
            if self.active is not None:
                dest=sites[a];self.active.append([dest,[z.reg_read(reg) for reg in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)[:counts[dest]]]])
        for a in (0x80051524,*sites):self.hooks.append(u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a))
    def dispose(self):
        assert self.active is None
        for h in self.hooks:self.u.hook_del(h)
