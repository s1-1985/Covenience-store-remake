"""80029334 core with external UI/audio/text calls abstracted, original order retained."""
import struct
from recovered import i32,truncdiv,rng_next,ledger_profit
from operating_costs import daily_debit,rword
from event_queue import reserve

def word(b,a,v):struct.pack_into('<I',b,a,v&0xffffffff)
def s8(v):return v if v<128 else v-256
def history(b,a,n=3):
    for j in range(n,0,-1):b[a+20*j:a+20*(j+1)]=b[a+20*(j-1):a+20*j]
    b[a:a+20]=bytes(20)

def annual_staff(staff,seed):
    for s in staff:
        if s8(s[3])<127:s[3]=(s[3]+1)&255
        value=s8(s[3]);boost=value>=127
        if not boost and value>=80:
            seed,v=rng_next(seed);boost=v%5==0
        if boost:
            for a in (0x18,0x1a,0x1b,0x1c,0x1d):s[a]=100
    return seed

def close(stores,staff,order,state,queue,text,schedules,rates,notification_text=None,pending_ui=None):
    """State keys are exact RAM addresses; values stored as unsigned words/bytes."""
    events=[];ui=[]
    def notify(kind,param,sound,mode,variant,spec=None):
        nonlocal text
        if notification_text is not None:text=notification_text(spec)
        events.append((kind,param,sound,mode,variant))
        reserve(queue,kind,param,sound,mode,variant,text)
    def add(a,v):state[a]=(state[a]+v)&0xffffffff
    def shift_scalar(a):
        for j in range(3,0,-1):state[a+4*j]=state[a+4*(j-1)]
        state[a]=0
    stage=state[0x800ce610];month=state[0x800ce60c]
    if state[0x800ce618] or state[0x800ce614]:return events,ui
    state[0x800cda00]=0
    if stage==4 and month==8:
        ui.append((0x80052270,2,0,0));state[0x800cda00]=1
    if i32(state[0x800cd8b8])>0 and not state[0x800cda00]:
        state[0x800cd8b8]=0;state[0x800d6270],v=rng_next(state[0x800d6270])
        request=(0x80052dbc,v%2);ui.append(request)
        if pending_ui is not None:pending_ui(request,state)
        for s in stores:
            if s[0] or not struct.unpack_from('<H',s,4)[0]&0x8000:word(s,0xc6c,100)
    sum_profit=0;own_count=0;monthly_flag=1;annual_flag=1
    cash=[i32(state[0x800cd9f8]),i32(state[0x800cd9fc])]
    for k in order[:10]:
        if k==-1:break
        s=stores[k];side=struct.unpack_from('<H',s,4)[0]>>15
        cash=daily_debit(s,staff,schedules,rates,cash)
        for j in range(5):word(s,0xd38+j*4,rword(s,0xd38+j*4)+rword(s,0xd88+j*4))
        history(s,0xd88)
        if stage==1:
            current=list(struct.unpack_from('<5i',s,0xd38));profit=ledger_profit(current)
            cash[side]=i32(cash[side]+7*profit)
            for j,v in enumerate(current):
                v=i32(v*8);word(s,0xd38+j*4,v);word(s,0xce8+j*4,rword(s,0xce8+j*4)+v)
            history(s,0xd38)
            for j in range(59,0,-1):word(s,0x12e8+j*4,rword(s,0x12e8+(j-1)*4))
            p=ledger_profit(list(struct.unpack_from('<5i',s,0xd4c)));word(s,0x12e8,p)
            if not side:
                sum_profit=i32(sum_profit+p);own_count=(own_count+1)&255;monthly_flag|=2
                if p<=0:monthly_flag=0
                if s8(state[0x800cd835]) and rword(s,0xd5c)>2999999:
                    ref=struct.unpack_from('<h',s,0xdd8)[0]
                    param=struct.unpack_from('<h',staff[ref],8)[0]
                    notify(3,param,28,1,0,('manager',k,rword(s,0xd5c)))
        if stage==1 and month==1:
            history(s,0xce8)
            for ref in struct.unpack_from('<3h',s,0xdd8):
                if ref!=-1:word(staff[ref],12,truncdiv(i32(i32(rword(s,0x12dc)+100)*rword(staff[ref],12)),100))
            if not side:
                annual_flag|=2
                if ledger_profit(list(struct.unpack_from('<5i',s,0xcfc)))<=0:annual_flag=0
    state[0x800cd9f8]=cash[0]&0xffffffff;state[0x800cd9fc]=cash[1]&0xffffffff
    if s8(own_count)>0:
        for j in range(59,0,-1):
            state[0x800e3c28+j*4]=state[0x800e3c28+(j-1)*4]
            state[0x800e43d0+j]=state[0x800e43d0+j-1]
        state[0x800e3c28]=sum_profit&0xffffffff;state[0x800e43d0]=own_count
    if stage==1 and month==1:state[0x800d6270]=annual_staff(staff,state[0x800d6270])
    for a,b,c in ((0x800d8f68,0x800da970,0x800df080),(0x800d8f78,0x800da980,0x800df090)):
        add(b,state[a]);shift_scalar(a)
        if stage==1:add(c,state[b]);shift_scalar(b)
        if stage==1 and month==1:shift_scalar(c)
    if monthly_flag==3:notify(0,0,28,1,0,('monthly',))
    if annual_flag==3:notify(0,0,28,1,0,('annual',))
    serial=struct.unpack('<h',struct.pack('<H',state[0x800cd9e0]))[0]
    if i32(state[0x800cd9f8])<0 or i32(state[0x800ce608])>=99 or serial>=99:
        state[0x800cd9b4]=4;state[0x800cd948]=255
    return events,ui
