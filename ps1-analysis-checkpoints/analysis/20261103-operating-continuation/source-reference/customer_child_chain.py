"""Connect destination, sidestep, patience, service to customer updater state."""
import struct
from customer_queue_state import s8
from finance_close import rword,word
from recovered import i32
from destination_full import destination_search
from movement import sidestep
from checkout import wait_resolution
from cashier import cashier_service

def child(name,arg,j,p,cash,flags,seed,store,meta,summary,pool,profiles,fixtures,images,dirs):
    w=rword(store,0x44);h=rword(store,0x48);profile=profiles[struct.unpack_from('<h',p,2)[0]]
    words={(x,y):struct.unpack_from('<I',store,0x108+y*112+x*4)[0] for y in range(h) for x in range(w)}
    if name=='destination':
        base=[list(struct.unpack_from('<28h',meta,0x14+y*56)) for y in range(26)];x,y=s8(p,0xc),s8(p,0xd);floor=s8(store,0x50+(y//2)*14+x//2)
        ret,goal,route,grid,start=destination_search(base,words,w,h,floor,s8(p,0),s8(p,1),struct.unpack_from('<h',p,0xa)[0],x,y,arg,(rword(summary,0x20),rword(summary,0x24)),[(f[0]&255,f[9],f[10]) for f in fixtures],images)
        p[0xf:0x12]=bytes(goal);p[0x12:0x1c]=route
        for y,row in enumerate(grid):struct.pack_into('<28h',meta,0x5c4+y*56,*row)
        if start is not None:struct.pack_into('<3i',meta,0xb74,*start)
    elif name=='move':
        occupancy=[[words[x,y] for x in range(w)] for y in range(h)]
        ret,start,seed=sidestep(occupancy,w,h,s8(p,0xc),s8(p,0xd),p[0x12]>>6,s8(profile,18),seed)
        if start is not None:struct.pack_into('<3i',meta,0xb74,*start)
    else:
        refs=struct.unpack_from('<3h',store,0xdd8);staff=[None if ref==-1 else {off:s8(pool[ref],off) for off in range(60)} for ref in refs]
        if name=='wait':
            result=wait_resolution(s8(p,0x1c),arg,struct.unpack_from('<h',p,0xa)[0],s8(p,0x1e),rword(store,0xc68),s8(store,0x12e1),staff,seed)
            ret=result['return_value'];seed=result['seed'];staff=result['staff'];p[0x1c]=result['patience']&255;struct.pack_into('<H',p,0xa,result['cart']&65535);word(store,0xc68,result['rating']);store[0x12e1]=result['counter']&255
            if result['flag']:
                revenue=i32(result['revenue']);word(store,0xd98,i32(rword(store,0xd98)+revenue));side=struct.unpack_from('<H',store,4)[0]>>15;cash=cash.copy();cash[side]=i32(cash[side]+revenue);flags|=0x20
        elif name=='service':
            busy=[rword(meta,4+k*4) for k in range(3)];manager=s8(pool[refs[0]],0x1d)
            ret,staff,busy,seed=cashier_service(w,h,words,[f[9:11] for f in fixtures],dirs,tuple(s8(p,k) for k in (0xc,0xd,0xe)),staff,busy,s8(profile,18),manager,seed)
            for k,v in enumerate(busy):word(meta,4+k*4,v)
        else:raise ValueError(name)
        for k,values in enumerate(staff):
            if values is not None:
                for off,v in values.items():pool[refs[k]][off]=v&255
    return ret,cash,flags,seed
