"""Opening-state floor codes, floor reset and queue mode4 predicate."""
import struct
from recovered import truncdiv

def floor_cells(store):
    w,h=struct.unpack_from('<ii',store,0x44)
    for y in range(max(0,truncdiv(h,2))):
        for x in range(max(0,truncdiv(w,2))):yield 0x50+y*14+x

def switch_floor(store):
    mapping={28:29,30:31,32:33,34:35} if store[0xc77]==0 else {29:28,31:30,33:32,35:34}
    for a in floor_cells(store):store[a]=mapping.get(store[a],store[a])

def reset_floor(store):
    for a in floor_cells(store):
        if 0<=store[a]<16:store[a]=store[0x4c]

def mode4_pending(queue,first,second):
    for j in range(50):
        k=j*160
        if queue[k] and queue[k+2]==4:
            if first==-1:return 1
            a,b=struct.unpack_from('<ii',queue,k+144)
            if a==first and (second==-1 or b==second):return 1
    return 0

def opening_step(store,hour,schedules,flags):
    state=store[0xc77];schedule=struct.unpack_from('<i',store,0xc78)[0]
    is_open=schedules[schedule][hour]!=0
    if state in (0,2):
        if is_open:state=3;flags|=1
    elif not is_open:state=2;flags|=2
    if state==3:
        state=1;store[0xc77]=state;switch_floor(store)
    if state==2 and not any(store[0xf04+j*32] for j in range(20)):
        state=0;store[0xc77]=state;switch_floor(store)
    store[0xc77]=state
    return flags
