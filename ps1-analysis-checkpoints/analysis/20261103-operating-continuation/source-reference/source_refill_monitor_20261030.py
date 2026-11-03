"""Independent3B278 restocking against naturally reached store/staff state."""
from check_machine import *
from caller_connection_harness import Memory
from inventory_callers import refill
from source_customer_loop_monitor_20261030 import DIRS,FIXTURES,PRODUCTS
from recovered import i32
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
import hashlib

class SourceRefillMonitor:
    def __init__(self,u,runner):
        self.u=u;self.checks=[];self.postings=[];self.accounting_writes=[];self.pending=0
        def observe(z,a,n,d):
            if a==0x8001ca7c:
                m=Memory(z);p=z.reg_read(UC_MIPS_REG_A0);amount=i32(z.reg_read(UC_MIPS_REG_A1));income=z.reg_read(UC_MIPS_REG_A2)
                before=m.read(p,5080);expected=bytearray(before);side=struct.unpack_from('<H',before,4)[0]>>15
                offset=0xd98 if income else 0xd94
                struct.pack_into('<I',expected,offset,(struct.unpack_from('<I',expected,offset)[0]+amount)&0xffffffff)
                cash=[m.word(v) for v in (0x800cd9f8,0x800cd9fc)];ec=list(cash);ec[side]=(ec[side]+(amount if income else -amount))&0xffffffff
                caller=z.reg_read(UC_MIPS_REG_RA);self.pending+=1
                def check_post():
                    assert m.read(p,5080)==expected
                    assert [m.word(v) for v in (0x800cd9f8,0x800cd9fc)]==ec
                    self.postings.append(dict(clock=m.word(0x800cd93c),store_slot=(p-0x8012b2f8)//5080,caller=hex(caller),
                                              amount=amount,income=income,cash_before=cash,cash_after=ec))
                    self.pending-=1
                runner.onreturn(caller,check_post);return
            m=Memory(z);p=z.reg_read(UC_MIPS_REG_A0);person=z.reg_read(UC_MIPS_REG_A1)
            store=bytearray(m.read(p,5080));before=bytes(store);staff=m.read(person,60)
            images=[list(struct.unpack('<12i',m.read(0x8009ce14+j*88,48))) for j in range(27)]
            cash=[i32(m.word(v)) for v in (0x800cd9f8,0x800cd9fc)];seed=m.word(0x800d6270)
            ret,eseed,ec=refill(store,staff,seed,cash,DIRS,FIXTURES,PRODUCTS,images,m.word(0x800ce60c))
            self.pending+=1
            def check():
                assert m.read(p,5080)==store,('source restock bytes',hex(p),hex(person))
                assert m.read(person,60)==staff
                assert i32(z.reg_read(UC_MIPS_REG_V0))==ret
                assert m.word(0x800d6270)==eseed
                assert [m.word(v) for v in (0x800cd9f8,0x800cd9fc)]==[v&0xffffffff for v in ec]
                self.checks.append(dict(clock=m.word(0x800cd93c),store_slot=(p-0x8012b2f8)//5080,
                    staff_id=(person-0x80143ff8)//60,result=ret,seed_before=seed,seed_after=eseed,
                    cash_before=cash,cash_after=ec,goods_before=struct.unpack_from('<i',before,0xd94)[0],
                    goods_after=struct.unpack_from('<i',store,0xd94)[0],store_sha256=hashlib.sha256(store).hexdigest()))
                self.pending-=1
            runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
        self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a) for a in (0x8003b278,0x8001ca7c)]
        def account_write(z,access,a,n,v,d):
            self.accounting_writes.append(dict(clock=get(z,0x800cd93c),address=hex(a),size=n,
                before=int.from_bytes(z.mem_read(a,n),'little'),after=v,pc=hex(z.reg_read(UC_MIPS_REG_PC)),
                caller=hex(z.reg_read(UC_MIPS_REG_RA))))
        for a,n in [(0xcd9f8,8)]+[(0x12b2f8+k*5080+0xd94,4) for k in range(10)]:
            self.hooks.append(u.hook_add(UC_HOOK_MEM_WRITE,account_write,begin=a,end=a+n-1))
    def dispose(self):
        assert self.pending==0
        for h in self.hooks:self.u.hook_del(h)
