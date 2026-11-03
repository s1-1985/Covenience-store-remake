"""Independent773BC pickup/removal checks on actual source UI states."""
from check_machine import *
from unicorn import UC_HOOK_CODE
from cashier import fixture_at
from caller_connection_harness import Memory
from interior_catalog import DESCRIPTORS,PRODUCTS
from operation_runtime import TILES,IMAGES
from preview_producer import produce
from rival_helpers import product_image
from recovered import i32,truncdiv
import hashlib

class SourceInteriorSelectionMonitor:
    def __init__(self,u,runner):
        self.u=u;self.checks=[];self.pending=0
        def observe(z,a,n,d):
            mode=get(z,0x800cd924)
            if mode not in (1,3,4):return
            addr=z.reg_read(UC_MIPS_REG_A0);m=Memory(z)
            before=m.read(addr,5080);expected=bytearray(before)
            backup=m.read(0x8014bda0,256);copy=bytearray(backup)
            preview=m.read(0x800e3f58,256);ep=bytearray(preview)
            px,py=map(i32,(get(z,0x800cd960),get(z,0x800cd964)))
            width,height=struct.unpack_from('<ii',before,68)
            cells={(x,y):struct.unpack_from('<I',before,264+y*112+x*4)[0]
                   for y in range(height) for x in range(width)}
            dimensions=[struct.unpack_from('<ii',desc,36) for desc in DESCRIPTORS]
            x,y=fixture_at(width,height,cells,dimensions,truncdiv(px,8),truncdiv(py,8))
            cash,eq,stock=map(i32,(get(z,0x800cd9f8),get(z,0x800cd978),get(z,0x800cd8e0)))
            kind=rotation=image=quantity=None;bounds=None;dims=None;ret=255
            if x!=-1 and y!=-1:
                anchor=cells[x,y];kind=anchor>>12&1023;rotation=anchor>>22&3
                item=struct.unpack_from('<I',before,376+y*112+x*4)[0]
                image=item>>12&1023;quantity=item>>24&127;desc=DESCRIPTORS[kind]
                w,h=dimensions[kind]
                if rotation>=2:w,h=h,w
                w*=2;h*=2;bounds=[x,y,x+w-1,y+h-1]
                rejected=mode==3 and (struct.unpack_from('<I',desc)[0]&255) in (4,6)
                if not rejected:
                    for yy in range(h):
                        for xx in range(w):
                            at=264+(y+yy)*112+(x+xx)*4
                            copy[yy*24+xx*4:yy*24+xx*4+4]=expected[at:at+4]
                            expected[at:at+4]=bytes(4)
                    struct.pack_into('<4I',ep,144,*bounds)
                    if mode==3:
                        ret=0;price=struct.unpack_from('<i',desc,4)[0]
                        cash=i32(cash+price);eq=i32(eq-price)
                        if image:
                            product=product_image(image,IMAGES);base,factor=PRODUCTS[product]
                            cost=i32(truncdiv(i32(base*factor),100)*quantity)
                            cash=i32(cash+cost);stock=i32(stock-cost)
                    else:
                        ret=254;ep,w,h=produce(ep,kind,rotation,image,quantity,desc,TILES);dims=[w,h]
            self.pending+=1
            def check():
                assert m.read(addr,5080)==bytes(expected),('selection store',mode,kind,x,y)
                assert m.read(0x8014bda0,256)==bytes(copy),('selection backup',mode,kind)
                assert m.read(0x800e3f58,256)==bytes(ep),('selection preview',mode,kind)
                assert z.reg_read(UC_MIPS_REG_V0)==ret,('selection return',mode,kind,ret,z.reg_read(UC_MIPS_REG_V0))
                assert [get(z,p) for p in (0x800cd9f8,0x800cd978,0x800cd8e0)]==[v&0xffffffff for v in (cash,eq,stock)]
                if ret==254:
                    assert [get(z,p) for p in (0x800cd960,0x800cd964,0x800cd9e8,0x800cd9ec)]==[x*8,y*8,*dims]
                self.checks.append(dict(mode=mode,kind=kind,rotation=rotation,image=image,quantity=quantity,
                    bounds=bounds,result=ret,cash=cash,equipment=eq,inventory=stock,
                    store_sha256=hashlib.sha256(expected).hexdigest()))
                self.pending-=1
            runner.onreturn(z.reg_read(UC_MIPS_REG_RA),check)
        self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=0x800773bc,end=0x800773bc)]
    def dispose(self):
        assert self.pending==0
        for h in self.hooks:self.u.hook_del(h)
