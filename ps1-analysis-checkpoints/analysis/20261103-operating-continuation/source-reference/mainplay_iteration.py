"""Independent5CD60 loop body and selected-store input dispatch."""
import struct
from recovered import i32
S=0x8012b2f8

def tail(m,call):
 """Original5D4B0..5D5A4 shared post-action update/repeat gate."""
 call(0x8003ff00);call(0x80018a5c)
 if m.word(0x800cd9cc)==0:
  call(0x80018a5c);m.wordset(0x800cd7e0,0)
  if m.word(0x800cd7f4)==0:call(0x80023438)
  if m.word(0x800cd7e0):m.wordset(0x800cd9d8,m.word(0x800cd7e0));call(0x80013ddc)
 if i32(m.word(0x800cd9b4))!=-1:call(0x8006d8ec,m.word(0x800cd9b4));return 'exit'
 call(0x80065a1c)
 if m.word(0x801398b4):
  for a in(0x800cd884,0x800cd850):m.wordset(a,m.word(a)&0xf00c)
 return 'next'

def half(m,a):return struct.unpack('<h',m.read(a,2))[0]
def selected_store(m,call):
 st=S+i32(m.word(0x8013796c))*5080
 if m.word(0x800cd884)&0x80:call(0x80065000);call(0x80060418)
 if m.word(0x800cd884)&32:call(0x80065000);call(0x80066818,st,half(m,0x800cd7d0),half(m,0x800cd7d2))
 if m.word(0x800cd884)&64:call(0x80065040);m.wordset(0x8013796c,-1);call(0x80062a4c,0,0)
 call(0x8004a27c,st)
 return st

def town_click(m,call):
 st=None
 x,y=half(m,0x800cda42),half(m,0x800cda44);tile=call(0x80020238,x,y)
 if tile<3:
  for index in range(10):
   candidate=S+index*5080
   if not m.byte(candidate):continue
   box=[i32(m.word(candidate+8+j*4)) for j in range(4)]
   if not(box[0]<=half(m,0x800cda42)<=box[2] and box[1]<=half(m,0x800cda44)<=box[3]):continue
   call(0x80065000);call(0x80018940,0x5ee,1);call(0x80018940,17,0);call(0x80062a4c,2,index);st=candidate;call(0x80041218,st);call(0x8004a27c,st);call(0x80018a5c);break
 elif tile<9:call(0x80060d6c)
 else:
  call(0x80065000);py=16 if half(m,0x800cda44)-half(m,0x800cd7d8)<10 else 3;call(0x8004d104,72,py*8,x,y);call(0x800656f8);call(0x80041a08)
 return st

def iteration(m,call):
 m.wordset(0x800cd9b4,-1);st=S+i32(m.word(0x8013796c))*5080;view=i32(m.word(0x800cd97c))
 if view==0:
  call(0x80065b9c,m.word(0x800cd850));call(0x8006dbf0);call(0x80066234);call(0x80018940,0x42f,1);call(0x80018940,0x3c0,0)
 elif view==1:
  call(0x8006dbf0);call(0x80066234);call(0x80018940,0x42f,1);call(0x80018940,0x3c0,0);call(0x8004ea68)
 elif view==2:
  call(0x80066070,m.word(0x800cd850));call(0x8004a27c,st);call(0x80041218,st);call(0x80018940,0x5ee,1);call(0x80018940,1,0)
 if m.word(0x800cd884)&0x800:call(0x80065000);m.wordset(0x800cd7f4,m.word(0x800cd7f4)^1)
 view=i32(m.word(0x800cd97c))
 if view==0:
  if m.word(0x800cd884)&12:call(0x800650c0);m.wordset(0x800cd9a4,m.word(0x800cd9a4)^1)
  if m.word(0x800cd884)&0x80:call(0x8005fe54)
  elif m.word(0x800cd884)&16:call(0x80062a4c,1,0);call(0x80065000)
  elif m.word(0x800cd884)&32:
   chosen=town_click(m,call)
   if chosen is not None:st=chosen
 elif view==1:call(0x8005f500)
 elif view==2:st=selected_store(m,call)
 call(0x8003ff00);call(0x80018a5c)
 if m.word(0x800cd9cc)==0:
  call(0x80018a5c);m.wordset(0x800cd7e0,0)
  if m.word(0x800cd7f4)==0:call(0x80023438)
  if m.word(0x800cd7e0):m.wordset(0x800cd9d8,m.word(0x800cd7e0));call(0x80013ddc)
 if i32(m.word(0x800cd9b4))!=-1:call(0x8006d8ec,m.word(0x800cd9b4));return 'exit'
 call(0x80065a1c)
 if m.word(0x801398b4):
  for a in (0x800cd884,0x800cd850):m.wordset(a,m.word(a)&0xf00c)
 return 'next'
