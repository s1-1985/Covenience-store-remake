"""Recovered51174 two-choice confirmation and its checksum-result continuation."""
def decision(selected,directions,buttons):
    if directions&0x2000 and selected==0:selected=1
    if directions&0x8000 and selected==1:selected=0
    if buttons&32:return selected,('attempt' if selected==0 else 'cancel')
    if buttons&64:return selected,'cancel'
    return selected,'repeat'

class LoadConfirmationMonitor:
    def __init__(self,u,runner):
        from check_machine import get,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_V0
        from unicorn import UC_HOOK_CODE
        from input_wait import InputWait
        from recovered import i32
        import struct
        self.u=u;self.hooks=[];self.checks=[];self.inputs=[];self.pending=None;self.active=False
        def observe(z,a,n,d):
            if a==0x80051174:
                self.active=True
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),lambda:setattr(self,'active',False));return
            if not self.active:return
            fp=z.reg_read(UC_MIPS_REG_FP)
            if a==0x80041374:
                ra=z.reg_read(UC_MIPS_REG_RA)
                if not 0x80051174<=ra<0x8005188c:return
                ctx=runner.contexts[-1];tick=ctx['tick']
                iw=InputWait(get(z,0x800cd9cc),get(z,0x800cd9c0),i32(get(z,0x800cd8fc)),get(z,0x800cd990),ctx['raws'][tick:],get(z,0x800d6270),
                             (struct.unpack('<H',z.mem_read(0xcd7d0,2))[0],struct.unpack('<H',z.mem_read(0xcd8e4,2))[0]));iw.poll()
                def check_input():
                    assert ctx['tick']==tick+iw.ticks
                    assert [get(z,p) for p in (0x800cd9cc,0x800cd9c0,0x800cda28,0x800cda0c,0x800d6270)]==[iw.held,iw.edge,iw.buttons,iw.directions,iw.seed]
                    self.inputs.append([ra,iw.buttons,iw.directions,iw.ticks,iw.seed])
                runner.onreturn(ra,check_input);return
            if a==0x800513b8:
                assert self.pending is None
                before=z.mem_read((fp+0x2c)&0x1fffffff,1)[0];dirs=get(z,0x800cda0c);buttons=get(z,0x800cda28)
                selected,action=decision(before,dirs,buttons)
                self.pending=dict(before=before,directions=dirs,buttons=buttons,selected=selected,action=action,attempt=None);return
            if a==0x80051524:
                assert self.pending and self.pending['action']=='attempt'
                p=self.pending
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),lambda:p.update(attempt=i32(z.reg_read(UC_MIPS_REG_V0))));return
            if self.pending is None:return
            p=self.pending;terminal=p['action']=='cancel' or (p['action']=='attempt' and p['attempt']==0)
            assert z.mem_read((fp+0x2c)&0x1fffffff,1)[0]==p['selected']
            assert (a==0x800514fc)==terminal,(hex(a),p)
            if terminal:assert i32(get(z,fp+0x28))==(-1 if p['action']=='cancel' else 0)
            if p['action']=='attempt':assert p['attempt'] is not None and get(z,0x800cda28)==0
            self.checks.append(dict(p,terminal=terminal));self.pending=None
        for a in (0x80051174,0x80041374,0x800513b8,0x80051524,0x80051264,0x800514fc):
            self.hooks.append(u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a))
    def dispose(self):
        assert self.pending is None
        for h in self.hooks:self.u.hook_del(h)
