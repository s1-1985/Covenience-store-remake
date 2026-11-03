"""319AC entry through 320CC (before visitor milestone notification) or 32814."""
import struct
from recovered import rng_next,i32
from customer_entry_init import demand_init
from customer_loop import CAPACITY
from customer_queue_state import s8
from finance_close import rword,word

def spawn(store,summary,seed,flags,month,stage,hour,profiles,calendar,times,appearances):
    def out(reason,slot=None,profile=None,qty=None):return seed,flags,dict(reason=reason,slot=slot,profile=profile,quantity=qty)
    if store[0]==0:return out('inactive')
    if store[0xc77]!=1:return out('not_open')
    limit=CAPACITY[rword(store,0xc70)];slot=next((j for j in range(limit) if store[0xf04+j*32]==0),None)
    if slot is None:return out('full')
    seed,v=rng_next(seed)
    if v&3:return out('random_gate')
    seed,v=rng_next(seed);start=v%144;group=calendar[(month-1)*4+stage-1]
    chosen=None
    for distance in range(1,145):
        k=(start+distance)%144;p=profiles[k]
        if times[group*576+hour*24+s8(p,2)]==0:continue
        demand=struct.unpack_from('<h',store,0xde4+k*2)[0]
        if demand>0:chosen=k;qty=min(demand,5);break
    if chosen is None:return out('no_demand')
    if s8(profiles[chosen],12)==3 and rword(summary,16)<i32(rword(summary,20)+qty):
        if s8(store,0x12e3)<127:store[0x12e3]=(store[0x12e3]+1)&255
        a=0xde4+chosen*2;old=struct.unpack_from('<H',store,a)[0];struct.pack_into('<H',store,a,(old-qty)&65535);flags|=0x40;qty=i32(rword(summary,16)-rword(summary,20))
        if qty<=0:return out('parking_no_room',slot,chosen,qty)
    a=0xf04+slot*32;p=store[a:a+32];p[0]=1;struct.pack_into('<H',p,2,chosen);demand_init(p,profiles[chosen],qty);seed,v=rng_next(seed);group=struct.unpack_from('<h',profiles[chosen],0)[0];p[0x1f]=appearances[group*4+v%4];store[a:a+32]=p
    a=0xde4+chosen*2;old=struct.unpack_from('<H',store,a)[0];struct.pack_into('<H',store,a,(old-qty)&65535)
    word(summary,20,i32(rword(summary,20)+qty));word(store,0x1188,i32(rword(store,0x1188)+qty))
    return out('created',slot,chosen,qty)
