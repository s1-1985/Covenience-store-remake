"""Connect original five staff target algorithms to parent updater model."""
import struct
from finance_close import word,rword
from inventory_callers import sb
from staff_work import staffing_gate,no_relevant_customers
from staff_targets import cleaning_targets,refill_targets,refill_reservations
from staff_route import staff_start,staff_route
from movement import prepare_grid
from cashier import fixture_at
from use_sides import mark_use_sides
from route_codec import encode_route

def target(name,slot,p,meta,seed,store,pool,summary,fixtures,clock):
    refs=struct.unpack_from('<3h',store,0xdd8)
    if name=='gate':
        people=[None if ref==-1 else dict(service=sb(pool[ref],0x1e),state=sb(pool[ref],0x28)) for ref in refs]
        return staffing_gate(rword(meta,0x10),sb(summary,0x28),people,slot,seed)
    w=rword(store,0x44);h=rword(store,0x48);x,y,state=sb(p,0x29),sb(p,0x2a),sb(p,0x28)
    floor=[[sb(store,0x50+yy*14+xx) for xx in range(14)] for yy in range(h//2)]
    if name in ('checkout','clean') and (clock&0xffffffff)%100<100-sb(p,0x20):return 1,seed
    if name=='checkout':
        customers=[(sb(store,0xf04+j*32),sb(store,0xf10+j*32),sb(store,0xf11+j*32)) for j in range((10,10,15,15,20,20)[rword(store,0xc70)])]
        if no_relevant_customers(customers,floor):return 1,seed
    words={(xx,yy):struct.unpack_from('<I',store,0x108+yy*112+xx*4)[0] for yy in range(h) for xx in range(w)}
    occupancy=[[words[xx,yy] for xx in range(w)] for yy in range(h)]
    base=[list(struct.unpack_from('<28h',meta,0x14+yy*56)) for yy in range(26)]
    grid=prepare_grid(base,occupancy,w,h,floor[y//2][x//2],0)
    dimensions=[tuple(f[9:11]) for f in fixtures];origin=fixture_at(w,h,words,dimensions,x,y) if state==0 else (0,0)
    if state==0 and origin==(-1,-1):raise ValueError('Resting staff must be within fixture for this model')
    grid=staff_start(grid,w,h,x,y,state,origin)
    compact=[(f[0]&255,f[9],f[10],f[3]) for f in fixtures]
    if name in ('checkout','rest'):
        off=0x20 if name=='checkout' else 0x18;tx=rword(summary,off);ty=rword(summary,off+4);value=words[tx,ty];kind=value>>12&1023;cat,fw,fh,cap=compact[kind]
        grid=mark_use_sides(grid,w,h,tx,ty,value>>22&3,cat,fw,fh,1)
    else:
        abilityoff=0x21 if name=='clean' else 0x1f
        others=[None if ref==-1 else dict(self=ref==refs[slot],state=sb(pool[ref],0x28),ability=sb(pool[ref],abilityoff),goal=(sb(pool[ref],0x2c),sb(pool[ref],0x2d)),direction=sb(pool[ref],0x2e)) for ref in refs]
        if name=='clean':grid,seed=cleaning_targets(grid,w,h,floor,others,seed)
        else:
            grid=refill_targets(grid,w,h,words,compact,sb(store,0xc77),sb(p,0x20));grid,seed=refill_reservations(grid,w,h,words,compact,others,seed)
    ret,goal,grid=staff_route(grid,w,h,x,y,state,origin);p[0x2c:0x2f]=bytes(goal);p[0x2f:0x39]=b'\xff'*10
    if ret==0:
        route,start,_=encode_route(grid,w,h,*goal);p[0x2f:0x39]=route;struct.pack_into('<3i',meta,0xb74,*start)
    for yy,row in enumerate(grid):struct.pack_into('<28h',meta,0x5c4+yy*56,*row)
    return ret,seed
