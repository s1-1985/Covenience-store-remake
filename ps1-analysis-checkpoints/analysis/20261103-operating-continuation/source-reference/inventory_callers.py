"""Full 8003B278 / 8003B420 callers, valid direction and product inputs."""
from inventory_full import update
from recovered import rng_next,i32,truncdiv
from finance_close import word,rword
import struct

def sb(b,o):return struct.unpack_from('<b',b,o)[0]
def refill(store,staff,seed,cash,dirs,fixtures,products,images,month):
    seed,v=rng_next(seed)
    ability=sb(staff,0x1f)
    if v%100+1>ability:return 1,seed,cash
    dx,dy=dirs[sb(staff,0x2b)]
    ret,cost=update(store,sb(staff,0x29)+dx,sb(staff,0x2a)+dy,truncdiv(ability,10)+1,-1,fixtures,products,images,month)
    if ret!=2:
        word(store,0xd94,i32(rword(store,0xd94)+cost));side=struct.unpack_from('<H',store,4)[0]>>15
        cash=cash.copy();cash[side]=i32(cash[side]-cost)
    return ret,seed,cash

def take(store,customer,dirs,fixtures,products,images,month):
    dx,dy=dirs[sb(customer,0xe)]
    ret,_=update(store,sb(customer,0xc)+dx,sb(customer,0xd)+dy,-sb(customer,0x1e),sb(customer,1),fixtures,products,images,month)
    if ret!=2:return 0
    if sb(store,0x12e2)<127:store[0x12e2]=(store[0x12e2]+1)&255
    return 1
