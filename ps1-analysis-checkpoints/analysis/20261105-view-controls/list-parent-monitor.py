"""Independent original 5F500 list policy over observed, unchanged native children."""
import hashlib
import struct
from check_machine import *
from caller_connection_harness import Memory
from source_play_return_monitor_20261102 import BytesMemory
from store_order import store_order
from unicorn import UC_HOOK_CODE

FIELDS=[(0x8012b2f8,50800),(0x80143ff8,2100),(0x800cd700,0x380),
        (0x8013796c,4),(0x800e4000,4),(0x800dae60,192*36)]


def project(m):
    return [m.read(a,n) for a,n in FIELDS]


def row(m):
    return struct.unpack('<h',m.read(0x800cd99c,2))[0]


def setrow(m,n):
    m.write(0x800cd99c,struct.pack('<H',n&65535))


def policy(m, child, output):
    stores=[m.read(0x8012b2f8+n*5080,5080) for n in range(10)]
    order,count=store_order(stores,0)
    child(0x8001bd78,output,0)
    assert list(struct.unpack('<10i',m.read(output,40)))==order
    assert count>0 and row(m)>=0, 'Reached valid own-store-list precondition'
    if row(m)>=count:
        setrow(m,count-1)
    initial=row(m)
    if m.word(0x800cd884)&32:
        child(0x80065000)
        child(0x80018940,0x5ee,1)
        child(0x80018940,17,0)
        child(0x80062a4c,2,order[row(m)])
        pointer=0x8012b2f8+order[row(m)]*5080
        child(0x80041218,pointer)
        child(0x8004a27c,pointer)
        child(0x80018a5c)
        branch='confirm'
    elif m.word(0x800cd884)&0x50:
        child(0x80065974)
        child(0x80018940,16,0)
        child(0x80062a4c,0,0)
        child(0x80065040)
        branch='cancel'
    elif m.word(0x800cd850)&0x4000:
        setrow(m,0 if row(m)+1>=count else row(m)+1)
        branch='down'
    elif m.word(0x800cd850)&0x1000:
        setrow(m,count-1 if row(m)-1<0 else row(m)-1)
        branch='up'
    else:
        branch='idle'
    if m.word(0x800cd97c)==1:
        child(0x80051918,row(m)+1)
    return dict(order=order,count=count,row_before=initial,row_after=row(m),branch=branch,
                view_after=m.word(0x800cd97c),selected_after=m.word(0x8013796c))


class ListParentMonitor:
    def __init__(self,u,runner):
        self.checks=[]
        self.active=None
        counts={0x8001bd78:2,0x80065000:0,0x80018940:2,0x80062a4c:2,
                0x80041218:1,0x8004a27c:1,0x80018a5c:0,0x80065974:0,
                0x80065040:0,0x80051918:1}
        exe=EXE.read_bytes()
        sites={}
        for pc in range(0x8005f500,0x8005f7f8,4):
            w=struct.unpack_from('<I',exe,pc-0x80010000+2048)[0]
            if w>>26==3:
                target=0x80000000|((w&0x3ffffff)<<2)
                assert target in counts
                sites[pc]=target

        def observe(z,pc,size,data):
            m=Memory(z)
            if pc==0x8005f500:
                assert self.active is None
                event=dict(initial=bytes(z.mem_read(0,0x200000)),rows=[],output=z.reg_read(UC_MIPS_REG_SP)-0x38)
                self.active=event

                def finish():
                    state=BytesMemory(event['initial'])
                    cursor=0

                    def child(target,*args):
                        nonlocal cursor
                        item=event['rows'][cursor]
                        cursor+=1
                        assert target==item['target'] and [x&0xffffffff for x in args]==item['args']
                        assert project(state)==item['before'], ('list parent bytes',cursor,hex(target))
                        state.b[:]=item['after']
                        return item['result']

                    result=policy(state,child,event['output'])
                    assert cursor==len(event['rows']) and project(state)==project(m)
                    result['calls']=[[hex(v['target']),v['args'],v['result']] for v in event['rows']]
                    result['projection_sha256']=[hashlib.sha256(b).hexdigest() for b in project(m)]
                    self.checks.append(result)
                    self.active=None

                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),finish)
                return
            assert self.active is not None
            target=sites[pc]
            item=dict(target=target,args=[z.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1)[:counts[target]]],before=project(m))
            self.active['rows'].append(item)

            def returned():
                item.update(after=bytes(z.mem_read(0,0x200000)),result=z.reg_read(UC_MIPS_REG_V0))

            runner.onreturn(pc+8,returned)

        self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x8005f500,*sites)]
