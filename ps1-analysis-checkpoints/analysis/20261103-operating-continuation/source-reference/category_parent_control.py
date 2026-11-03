"""Recovered75514 outercontrol. Explicitcall boundary; child formulas verified separately."""
from recovered import i32,truncdiv
import struct
SLOT_BASE=0x8013f6c0

def run(mem,store,argument,call):
 rw=lambda a:i32(mem.word(a));ww=mem.wordset;rb=mem.byte;wb=mem.byteset
 def stock(a):return struct.unpack('<h',mem.read(a,2))[0]
 def half(a,v):mem.write(a,struct.pack('<H',v&65535))
 def cl(a,*args):return i32(call(a,*args))
 cl(0x80018940,1,0);cl(0x80018940,0x5ee,1)
 for a,v in ((0x800cda48,8),(0x800cda30,0),(0x800cda24,store),(0x800cd978,0),(0x800cd8e0,0)):ww(a,v)
 policy=int(argument!=0);refs=[]
 for slot in range(3):
  sid=stock(store+0xdd8+slot*2);refs.append(sid);ww(0x800e35e0+slot*4,sid);half(store+0xdd8+slot*2,-1)
  if sid!=-1:
   person=0x80143ff8+sid*60
   if rb(person+40):
    x=rb(person+41);y=rb(person+42);x=x-256 if x>=128 else x;y=y-256 if y>=128 else y;a=store+264+y*112+x*4;ww(a,mem.word(a)&0xffc00fff)
 for j in range(20):
  person=store+0xf04+j*32
  if not rb(person):continue
  wb(person,0);x=rb(person+12);y=rb(person+13);x=x-256 if x>=128 else x;y=y-256 if y>=128 else y
  if x!=-1 and y!=-1:
   a=store+264+y*112+x*4;ww(a,mem.word(a)&0xffc00fff)
 cl(0x800230e8,store);cl(0x80041218,store);state=7 if argument==1 else 1;ww(0x800cd924,255);states=[]
 for loop in range(200):
  if state==255:break
  states.append(state);cl(0x8004095c,0)
  if state==1:
   cl(0x8001b678,store,0);cl(0x80065974);cl(0x80041218,store);cl(0x80065690);slot=rw(store+0xc70);selection=cl(0x80044d20,int(rw(SLOT_BASE+slot*3108+8)!=-1));ww(0x800cd8cc,selection);cl(0x80018940,6,1)
   if selection==0:return -1,states
   if selection in (1,3):
    cl(0x8001b678,store,2 if selection==1 else 1)
    if selection==3:cl(0x8001d1ac,store)
    ww(0x800cd978,cl(0x8001d018,store));ww(0x800cd8e0,cl(0x8001d618,store))
    if selection==1:cl(0x80065974)
    cl(0x80041218,store);total=i32(rw(0x800cd978)+rw(0x800cd8e0))
    if total<rw(0x800cd9f8):ww(0x800cd9f8,i32(rw(0x800cd9f8)-total));policy=1;state=7
    else:cl(0x80065080);cl(0x80066c64,0x800b9688)
   elif selection==2:state=3
  elif state==2:
   cl(0x80065974);cl(0x80041218,store)
   if cl(0x80045228)==1:
    ww(0x800cd978,cl(0x8001d018,store));ww(0x800cd8e0,cl(0x8001d618,store));state=255
   else:state=7
  elif state==3:
   cl(0x80065690);cl(0x80065974);selection=cl(0x80045404,store,0);ww(0x800cd8cc,selection)
   if selection==-1:state=7 if policy==1 else 3
   else:
    ww(store+76,selection);cl(0x800230e8,store);cl(0x80041218,store);state=7 if policy==1 else 4
  elif state in (4,5):
   if state==5:cl(0x80065690)
   for a,v in ((0x800cda08,16),(0x800cd878,0),(0x800cd804,0),(0x800cda30,0),(0x800cd830,2 if state==4 else 4),(0x800cd7f0,state)):ww(a,v)
   if state==4:ww(0x800cd8cc,0);cl(0x80065974);selection=cl(0x8004594c,store,1)
   else:selection=cl(0x8006966c)
   ww(0x800cd8cc,selection)
   if selection!=-1:
    ww(0x800cda30,selection)
    if cl(0x80076b68,store)==0:
     if state==5:policy=1;state=7
     else:state=7 if policy==1 else 5
  elif state==6:
   for a,v in ((0x800cda08,16),(0x800cd878,0),(0x800cd804,0),(0x800cd830,39)):ww(a,v)
   prior=rw(0x800cda30);q=truncdiv(prior,15);ww(0x800cd8cc,prior-q*15);ww(0x800cda38,q);ww(0x800cd7f0,state);selection=cl(0x80067c80,store);ww(0x800cda30,selection)
   if selection==-1:state=7
   else:
    kind=rw(0x800b9920+selection*4)
    if 0<=kind<22 or 29<=kind<33:
     answer=cl(0x80068978,store,-1,-1,kind)
     if answer==-1:state=6;continue
    state=6 if cl(0x80076b68,store)==1 else 7
  elif state==7:
   ww(0x800cda08,16);selection=cl(0x80060b90,0);ww(0x800cd8cc,selection);ww(0x800cd924,selection)
   if selection==4:
    answer=cl(0x800788c8,store)
    if answer==0:state=10
    else:cl(0x80065080);cl(0x80066c64,mem.word(0x800b98a4+answer*4))
   else:state=6 if selection==0 else 8
  elif state==8:
   ww(0x800cd878,0);answer=cl(0x80077de4,store);state={1:3,2:4,3:5}.get(answer,7);cl(0x80041218,store)
  elif state==9:pass
  elif state==10:
   if cl(0x80066fcc,0x800b98d0)==1:cl(0x8001b8c4,store,1)
   state=255;cl(0x80065690)
 else:raise AssertionError('control fixture exceeds200 states')
 for p in range(27):ww(store+0x11a0+p*12,0)
 for slot in range(3):
  sid=stock(0x800e35e0+slot*4);half(store+0xdd8+slot*2,sid)
  if sid!=-1:cl(0x8003dda8,store,slot,0)
 cl(0x80022d28,store);wb(0x801398bc,1);return 0,states
