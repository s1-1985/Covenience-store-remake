"""Independent source-derived title Start gate and ten-strip transition policies."""
from check_machine import *
from unicorn import UC_HOOK_CODE
class TitleIntroMonitor:
    def __init__(self,u,runner):
        self.u=u;self.runner=runner;self.checks=[];self.hooks=[]
        def half(a):return struct.unpack('<h',u.mem_read(a&0x1fffffff,2))[0]
        def halves(a):return list(struct.unpack('<10h',u.mem_read(a&0x1fffffff,20)))
        def heights(base):return [half(base+i*36) for i in range(10)]
        def observe(z,a,n,d):
            fp=z.reg_read(UC_MIPS_REG_FP);old=halves(fp+0x60);values=list(old);count=half(fp+0x5a)
            if a==0x80057ec0:
                started=half(fp+0x58);edge=get(z,0x800cd9c0)
                if edge&0x800:started=1
                beforexy=list(struct.unpack('<2H',z.mem_read(0xe441c,4)))
                expectedxy=[(beforexy[0]-1)&65535,(beforexy[1]+1)&65535]
                prevheights=heights(0x800d8fda)
                if started:
                    for i in range(count):
                        if values[i]:values[i]-=1
                    count=min(count+1,10)
                done=bool(started and values[9]==0)
                def check():
                    assert halves(fp+0x60)==values and half(fp+0x5a)==count and half(fp+0x58)==started
                    assert heights(0x800d8fda)==(old if started else prevheights)
                    assert list(struct.unpack('<2H',z.mem_read(0xe441c,4)))==expectedxy
                    self.checks.append(['hide',edge,started,count,values,done])
                runner.onreturn(0x800580ec if done else 0x800580bc,check)
            elif a==0x80058134:
                for i in range(9,9-count,-1):
                    if values[i]<16:values[i]+=1
                count=min(count+1,10);done=values[0]==16
                def check():
                    assert halves(fp+0x60)==values and half(fp+0x5a)==count
                    assert heights(0x800db2ea)==values
                    self.checks.append(['reveal',count,values,done])
                runner.onreturn(0x80058318 if done else 0x800582d8,check)
        for a in (0x80057ec0,0x80058134):self.hooks.append(u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a))
    def dispose(self):
        for h in self.hooks:self.u.hook_del(h)
