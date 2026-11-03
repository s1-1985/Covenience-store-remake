"""Native645AC flag predicate and3FF00 outer display state, draw calls abstracted."""
def status(disabled,value):return int(disabled==0 and value!=0)
def s16(v):v&=65535;return v if v<32768 else v-65536
def control(active,timer,disabled,value,kind,mode,view,x,y):
    if active!=1:return active,timer,'inactive',[]
    if not status(disabled,value):return 0,timer,'close',[(0x80064e4c,(-1,))]
    calls=[]
    if view==1:calls.extend([(0x80062a4c,(0,0)),(0x80065974,())])
    calls.append((0x80018940,(6,1)))
    if kind in (7,8):timer=0
    mode=mode&255;mode=mode if mode<128 else mode-256
    if mode==1:
        dx=32 if kind==0 else 72 if kind==3 else 56
        calls.append((0x80067338,(s16(x+dx),s16(y+16),0x800e3aa0)))
    elif mode==2:calls.append((0x8006c048,(0,64)))
    elif mode==3:calls.append((0x8006c8b0,(16,48)))
    return active,timer,'draw',calls
