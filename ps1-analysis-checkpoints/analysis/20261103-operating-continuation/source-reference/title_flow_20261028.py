"""Independent policies recovered from the source title/menu/top dispatcher."""
GP=0x800cd6c4
HANDLERS=(0x80011d28,0x80012520,0x80012548,0x80012800,
          0x80012828,0x80012848,0x800128b4,0x80012d90)
def menu_step(selected,directions,buttons):
    moves=[]
    if directions&0x1000 and selected==2: selected=1;moves.append(-16)
    if directions&0x4000 and selected==1: selected=2;moves.append(16)
    if buttons&32: return selected,moves,'confirm',True
    if buttons&64: return 0,moves,'cancel',True
    return selected,moves,None,False
def wrapper(state,result):
    if state==1:return 2,False
    if state==3:return 4,False
    if state==4:return 4,False
    if state==5:return (2,True) if result&0xffffffff==0xffffffff else (7,False)
    if state==7:return 2,True
    raise ValueError(state)

class TitleMenuMonitor:
    """Assert each original input poll, navigation state and rectangle/cursor movement."""
    def __init__(self,u,runner):
        from check_machine import get
        from unicorn import UC_HOOK_CODE
        from unicorn.mips_const import UC_MIPS_REG_FP,UC_MIPS_REG_RA
        from input_wait import InputWait
        from recovered import i32
        import struct
        self.u=u;self.runner=runner;self.checks=[];self.inputs=[];self.hooks=[];self.active=False
        def hook(z,a,n,d):
            if a==0x80059254:
                self.active=True
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),lambda:setattr(self,'active',False));return
            if not self.active:return
            fp=z.reg_read(UC_MIPS_REG_FP)
            if a==0x80041374:
                ctx=runner.contexts[-1];tick=ctx['tick']
                iw=InputWait(get(z,0x800cd9cc),get(z,0x800cd9c0),i32(get(z,0x800cd8fc)),get(z,0x800cd990),ctx['raws'][tick:],get(z,0x800d6270),(struct.unpack('<H',z.mem_read(0xcd7d0,2))[0],struct.unpack('<H',z.mem_read(0xcd8e4,2))[0]));iw.poll()
                def check_input():
                    assert ctx['tick']==tick+iw.ticks
                    assert [get(z,p) for p in (0x800cd9cc,0x800cd9c0,0x800cda28,0x800cda0c,0x800d6270)]==[iw.held,iw.edge,iw.buttons,iw.directions,iw.seed]
                    self.inputs.append([iw.buttons,iw.directions,iw.ticks,iw.seed])
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check_input);return
            if a==0x80059484:
                old=get(z,fp+0x28);directions=get(z,0x800cda0c);buttons=get(z,0x800cda28)
                selected,moves,sound,done=menu_step(old,directions,buttons)
                y=struct.unpack('<H',z.mem_read((fp+0x1a)&0x1fffffff,2))[0]
                cy=struct.unpack('<H',z.mem_read(0xdae3e,2))[0]
                def check():
                    assert get(z,fp+0x28)==selected
                    assert struct.unpack('<H',z.mem_read((fp+0x1a)&0x1fffffff,2))[0]==(y+sum(moves))&65535
                    assert struct.unpack('<H',z.mem_read(0xdae3e,2))[0]==(cy+sum(moves))&65535
                    self.checks.append([old,directions,buttons,selected,moves,sound,done])
                runner.onreturn(0x80059688 if done else 0x80059468,check)
        for a in (0x80059254,0x80041374,0x80059484):self.hooks.append(u.hook_add(UC_HOOK_CODE,hook,begin=a,end=a))
    def dispose(self):
        for h in self.hooks:self.u.hook_del(h)
