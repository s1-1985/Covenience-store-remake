"""80036AC0 selected whole-function paths; unsupported target-choice paths raise."""
import struct
from finance_close import word,rword
from inventory_callers import sb
from staff_energy import active_energy,rest_energy
from staff_walk import walking_step,commit_position
from staff_rest import enter_rest
from staff_refill_finish import finish as refill_finish
from staff_work import no_relevant_customers,clean_floor
from cashier import fixture_at
from extended import staff_growth

def update(store,pool,meta,summary,cash,flags,seed,clock,fixtures,products,images,month,direction_images,target_callback=None):
    width=rword(store,0x44);height=rword(store,0x48);refs=struct.unpack_from('<3h',store,0xdd8);dimensions=[tuple(f[9:11]) for f in fixtures]
    word(meta,0x10,sum(ref!=-1 and sb(pool[ref],0x28)==1 for ref in refs))
    def words():return {(x,y):struct.unpack_from('<I',store,0x108+y*112+x*4)[0] for y in range(height) for x in range(width)}
    effects=[]
    for slot in (2,1,0):
        if refs[slot]==-1:continue
        staff=pool[refs[slot]];position=tuple(sb(staff,o) for o in (0x29,0x2a,0x2b));newpos=position;state=sb(staff,0x28)
        struct.pack_into('<3i',meta,0xb74,*position)
        def call(name):
            nonlocal seed
            if target_callback is None:raise ValueError('unmodeled target choice: '+name)
            result=target_callback(name,slot,staff,meta,seed)
            if isinstance(result,tuple):ret,seed=result;return ret
            return result
        if state==0:
            if sb(staff,0x19)<sb(staff,0x18):
                grid=words();origin=fixture_at(width,height,grid,dimensions,*position[:2])
                # Native indexes (-1,-1) too if lookup fails; fixture placement valid here.
                if origin==(-1,-1):raise ValueError('selected rest position requires fixture')
                kind=grid[origin]>>12&1023
                staff[0x19],seed=rest_energy(sb(staff,0x19),sb(staff,0x18),kind,seed);effects.append('rest_recovery')
            elif ((clock&0xffffffff)//2)%3==slot:
                if call('gate')==0 and call('checkout')==0:
                    staff[0x28]=1;word(meta,0x10,rword(meta,0x10)+1);flags|=0x80
                elif call('refill')==0:staff[0x28]=2
                elif call('clean')==0:staff[0x28]=4
                effects.append('rest_departure_choice');newpos=struct.unpack_from('<3i',meta,0xb74)
        else:
            energy,goal,flags,seed=active_energy(sb(staff,0x19),state,tuple(staff[0x2c:0x2f]),flags,seed);staff[0x19]=energy;staff[0x2c:0x2f]=bytes(goal)
            if 255 in staff[0x2c:0x2e]:
                if sb(staff,0x19)<=0:call('rest');staff[0x28]=3
                elif call('gate')==0 and call('checkout')==0:
                    staff[0x28]=1;word(meta,0x10,rword(meta,0x10)+1)
                elif call('refill')==0:staff[0x28]=2
                elif call('clean')==0:staff[0x28]=4
                else:call('rest');staff[0x28]=3
                effects.append('active_target_choice');newpos=struct.unpack_from('<3i',meta,0xb74)
            else:
                goal=tuple(sb(staff,o) for o in (0x2c,0x2d,0x2e))
                if position[:2]==goal[:2]:
                    if position[2]!=goal[2]:newpos=(position[0],position[1],goal[2]);effects.append('turn')
                    elif state==1:
                        customers=[]
                        for j in range((10,10,15,15,20,20)[rword(store,0xc70)]):
                            a=0xf04+j*32;customers.append((sb(store,a),sb(store,a+0xc),sb(store,a+0xd)))
                        floor=[[sb(store,0x50+y*14+x) for x in range(14)] for y in range(14)]
                        if no_relevant_customers(customers,floor):staff[0x2c:0x2f]=b'\xff'*3;flags|=0x100
                        effects.append('service_arrival')
                    elif state==2:
                        manager=sb(pool[refs[0]],0x1d)
                        seed,cash,flags,ret=refill_finish(store,staff,seed,cash,flags,manager,rword(summary,4),((0,-1),(0,1),(-1,0),(1,0)),fixtures,products,images,month);effects.append('refill_'+str(ret))
                    elif state==3:
                        ret,after=enter_rest(width,height,words(),dimensions,slot,1,staff,((0,2),(0,1),(1,1)));staff[:]=after;newpos=tuple(sb(staff,o) for o in (0x29,0x2a,0x2b));staff[0x29:0x2c]=bytes(v&255 for v in position);effects.append('rest_arrival_'+str(ret))
                    elif state==4:
                        x,y,d=position;offset=0x50+(y//2)*14+x//2
                        ret,tile,d,out,dirty,seed=clean_floor(sb(store,offset),sb(staff,0x21),d,clock,seed,store[1],newpos[2]);store[offset]=tile&255;staff[0x2e]=d;store[1]=dirty;newpos=(x,y,out)
                        if ret:
                            flags|=0x800;staff[0x2c:0x2f]=b'\xff'*3;v={j:sb(staff,j) for j in range(0x1a,0x28)};v,seed=staff_growth(v,4,sb(pool[refs[0]],0x1d),rword(summary,4),seed)
                            for off,value in v.items():staff[off]=value&255
                        effects.append('clean_'+str(ret))
                else:
                    grid=words();occ=[[grid[x,y] for x in range(width)] for y in range(height)]
                    newpos,goal,route,seed=walking_step(occ,width,height,position,goal,staff[0x2f:0x39],sb(staff,0x1b),seed);staff[0x2c:0x2f]=bytes(v&255 for v in goal);staff[0x2f:0x39]=route;effects.append('walk')
        struct.pack_into('<3i',meta,0xb74,*newpos)
        current=tuple(sb(staff,o) for o in (0x29,0x2a,0x2b))
        grid,final,dirty=commit_position(words(),current,newpos,struct.unpack_from('<h',staff,6)[0],direction_images,store[1]);staff[0x29:0x2c]=bytes(v&255 for v in final);store[1]=dirty
        for (x,y),v in grid.items():word(store,0x108+y*112+x*4,v)
    return cash,flags,seed,effects
