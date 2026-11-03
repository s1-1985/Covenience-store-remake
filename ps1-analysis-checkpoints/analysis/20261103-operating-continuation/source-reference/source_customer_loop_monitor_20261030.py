"""Independent complete post-spawn customer loop on naturally reached RAM."""
from check_machine import *
from caller_connection_harness import Memory
from customer_loop import update
from customer_child_chain import child
from recovered import i32
from unicorn import UC_HOOK_CODE
import hashlib
EX=EXE.read_bytes()
def raw(a,n):return EX[a-0x80010000+2048:a-0x80010000+2048+n]
PROFILES=[bytearray(raw(0x800a09d0+j*24,24)) for j in range(144)]
FIXTURES=[list(struct.unpack('<49i',raw(0x80099f0c+j*196,196))) for j in range(53)]
PRODUCTS=[struct.unpack('<2i',raw(0x8009ce08+j*88,8)) for j in range(27)]
SEASONS=[struct.unpack('<i',raw(0x8009ce44+j*88,4))[0] for j in range(27)]
DIRS=[struct.unpack('<2i',raw(0x8009941c+j*8,8)) for j in range(4)]
DIRECTION_IMAGES=list(struct.unpack('<4i',raw(0x8009940c,16)))

class SourceCustomerLoopMonitor:
    def __init__(self,u,runner):
        self.u=u;self.checks=[];self.pending=0
        def observe(z,a,n,d):
            m=Memory(z);fp=z.reg_read(UC_MIPS_REG_FP);p=m.word(fp+0x58)
            slot=(p-0x8012b2f8)//5080;assert 0<=slot<10
            meta_addr=0x800cecec+slot*2948;summary_addr=m.word(meta_addr)
            store=bytearray(m.read(p,5080));meta=bytearray(m.read(meta_addr,2948));summary=m.read(summary_addr,168)
            before=bytes(store);pool=[bytearray(m.read(0x80143ff8+j*60,60)) for j in range(35)]
            images=[list(struct.unpack('<12i',m.read(0x8009ce14+j*88,48))) for j in range(27)]
            cash=[i32(m.word(v)) for v in (0x800cd9f8,0x800cd9fc)];flags=struct.unpack('<H',m.read(0x800cd790,2))[0]
            calls=[]
            def callback(name,arg,j,person,cs,fl,sd):
                result=child(name,arg,j,person,cs,fl,sd,store,meta,summary,pool,PROFILES,FIXTURES,images,DIRS)
                calls.append([name,arg,j,result[0]])
                return result
            callback.with_state=True
            clock=m.word(0x800cd93c)
            ec,ef,eseed=update(store,meta,summary,cash,flags,m.word(0x800d6270),clock,m.word(0x800ce60c),
                             PROFILES,PRODUCTS,SEASONS,FIXTURES,images,DIRS,DIRECTION_IMAGES,callback)
            self.pending+=1
            def check():
                for label,addr,expected in (('store',p,store),('metadata',meta_addr,meta),
                                            ('summary',summary_addr,summary),('staff',0x80143ff8,b''.join(pool))):
                    actual=m.read(addr,len(expected))
                    assert actual==expected,('source customer loop',slot,clock,label,
                        [(i,x,y) for i,(x,y) in enumerate(zip(actual,expected)) if x!=y][:8])
                assert [m.word(v) for v in (0x800cd9f8,0x800cd9fc)]==[v&0xffffffff for v in ec]
                assert struct.unpack('<H',m.read(0x800cd790,2))[0]==ef and m.word(0x800d6270)==eseed
                self.checks.append(dict(clock=clock,store_slot=slot,child_calls=calls,
                    states_before=[before[0xf04+j*32] for j in range(20)],
                    states_after=[store[0xf04+j*32] for j in range(20)],cash_before=cash,cash_after=ec,
                    revenue_before=struct.unpack_from('<i',before,0xd98)[0],revenue_after=struct.unpack_from('<i',store,0xd98)[0],
                    store_sha256=hashlib.sha256(store).hexdigest(),seed=eseed))
                self.pending-=1
            runner.onreturn(m.word(fp+0x54),check)
        self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=0x80032814,end=0x80032814)]
    def dispose(self):
        assert self.pending==0
        for h in self.hooks:self.u.hook_del(h)
