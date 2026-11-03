"""80023438 outer sequencing; child algorithms supplied as callbacks."""
from store_shift import opening_step
from finance_close import word
S=0x8012b2f8
ARGS={0x8004095c:1,0x80023c20:0,0x8003ef44:0,0x800275f8:0,0x80029020:0,0x80029334:0,0x8002a8e0:0,0x8002bd54:0,0x8002619c:0,0x8003ceac:0,0x8001bc54:0,0x800248b0:1,0x800319ac:1,0x80036ac0:1,0x80031498:1,0x8003b570:2,0x8003bf28:1,0x800645ac:0,0x8008eaec:3,0x80064e4c:1,0x80022d28:1}
JOBS=(0x800319ac,0x80036ac0,0x80031498,0x8003b570,0x8003bf28)
def update(stores,order,g,month,stage,hour,minute,schedules,enabled,channel,extra,tones,call):
    g['clock']=(g['clock']+2)&0xffffffff
    call(0x8004095c,0);call(0x80023c20)
    if call(0x8003ef44)==1:return 'notification'
    for address in (0x800275f8,0x80029020,0x80029334,0x8002a8e0,0x8002bd54):call(address)
    if minute==0 and hour==0:call(0x8002619c)
    call(0x8003ceac);selected=call(0x8001bc54);count=0
    for index in order[:10]:
        g['index']=index
        if index==-1:break
        store=stores[index];pointer=S+index*5080
        if minute==0 and hour==0 and stage==1:
            store[2]=0
            for j in range(27):word(store,0x1198+j*12,0);word(store,0x119c+j*12,0)
        g['flags']=0;call(0x800248b0,pointer);count+=1
        state=store[0xc77];schedule=int.from_bytes(store[0xc78:0xc7c],'little',signed=True);op=schedules[schedule][hour]!=0
        planned=(3 if op else state) if state in (0,2) else (2 if not op else state)
        floor_call=planned==3 or (planned==2 and not any(store[0xf04+j*32] for j in range(20)))
        g['flags']=opening_step(store,hour,schedules,g['flags'])
        if floor_call:call(0x80022d28,pointer)
        for address in JOBS:call(address,pointer,*([index] if address==0x8003b570 else []))
        value=32 if call(0x800645ac)==1 else 100;call(0x8008eaec,channel,value,value)
        if store[0xc77]!=0 and minute==0 and hour==12:g['flags']|=4 if stage%2==1 else 8
        if enabled and index==selected:
            bit=0
            while g['flags']:
                if g['flags']&1:call(0x80064e4c,{0:50,1:49,2:month+36,3:extra+51}.get(bit,tones[bit]))
                g['flags']>>=1;bit+=1
    if (g['max'] if g['max']<128 else g['max']-256)<count:g['max']=count&255
    g['regen']=0
    return 'normal'
