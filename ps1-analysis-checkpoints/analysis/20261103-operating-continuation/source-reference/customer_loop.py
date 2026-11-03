"""Whole post-spawn customer loop 80032814..800330E4, four child callbacks."""
import struct
from customer_entry_init import begin
from purchase_full import purchase
from customer_queue_state import control,s8
from customer_dispatch import finish
from customer_position import commit
from finance_close import word
CAPACITY=(10,10,15,15,20,20)

def update(store,meta,summary,cash,flags,seed,clock,month,profiles,products,seasons,fixtures,images,dirs,direction_images,callback):
    level=struct.unpack_from('<i',store,0xc70)[0]
    for j in range(CAPACITY[level]):
        a=0xf04+j*32;p=store[a:a+32];state=p[0]
        if state==0:continue
        struct.pack_into('<iii',meta,0xb74,*(s8(p,o) for o in (0xc,0xd,0xe)))
        if getattr(callback,'with_state',False):
            def call(name,arg,cash,flags,seed):return callback(name,arg,j,p,cash,flags,seed)
            call.with_state=True
        else:
            def call(name,arg):return callback(name,arg,j,p)
        if state==1:seed,_=begin(store,p,meta,seed,clock,profiles)
        elif state in (2,4):
            ret,cash,flags,seed=purchase(store,p,meta,summary,cash,flags,seed,clock,month,profiles,products,seasons,fixtures,images,dirs,call);finish(p,state,ret)
        elif state in (3,5):
            profile=profiles[struct.unpack_from('<h',p,2)[0]];ret,cash,flags,seed=control('checkout' if state==3 else 'exit',store,p,meta,cash,flags,seed,dirs,s8(profile,18),call);finish(p,state,ret)
        commit(store,p,meta,direction_images);store[a:a+32]=p
    return cash,flags,seed
