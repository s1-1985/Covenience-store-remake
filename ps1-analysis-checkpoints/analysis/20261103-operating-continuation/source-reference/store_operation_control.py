"""60418 operation menu, independent panel and branch control."""
import struct
from recovered import i32,truncdiv
from cursor_control import s16
from numeric_display_width import units
from sprite_record import record
S=0x8012b2f8

def panel(m,store,last,child):
 child(0x80065974);child(0x80017b18,180|(16<<16),9|(12<<16),0);child(0x8004e494,196,32,384)
 if m.word(0x8013796c)==0:child(0x8004e494,196,48,12)
 else:m.wordset(0x800cd938,int.from_bytes(m.read(store+4,2),'little')&127);child(0x8004e494,196,48,366)
 value=m.word(store+0xd98);m.wordset(0x800e4000,value);child(0x8004e494,s16(306-units(value)*8),64,272)
 child(0x80067338,196,80,(0x80099958+m.word(store+0xc78)*48)&0xffffffff)
 m.write(0x800cd8e6,struct.pack('<H',truncdiv(i32(m.word(store+0xc68)),20)&65535));child(0x8004e494,196,112,310);child(0x80067338,226,128,0x80099898)
 child(0x80018940,8,1);child(0x800419e0)
 for j in range(3):
  count=struct.unpack('<h',m.read(0x800cda34,2))[0];p=0x800dae60+36*count;tint=128 if m.byte(store+0xc74+j)==1 else 64
  m.write(p,record(m.read(p,36),96+j*16,-64,16,16,7,128+j*16,16,0,492,(tint,)*3,1));m.write(0x800cda34,struct.pack('<H',(count+1)&65535))
 child(0x80018940,0x5ee,1)
 return child(0x8004e578,194|(128<<16),112|(16<<16),0,4,260,last)-1

def run(m,child,draw=panel):
 choice=0;channel=struct.unpack('<h',m.read(0x800cd7f8,2))[0];child(0x8008eaec,channel,100,100);states=[]
 for _ in range(100):
  if choice==-1:return -1,states
  index=i32(m.word(0x8013796c));store=(S+index*5080)&0xffffffff;old=choice;choice=draw(m,store,choice,child);states.append([index,old,choice])
  closed=m.byte(store+0xc77)!=0
  if choice in(0,3) and closed:
   answer=child(0x80066fcc,0x80099aa8 if choice==0 else 0x80099d14)
   if answer==1:m.wordset(store+0xc78,6);return i32(store),states
   return answer,states
  if choice==0:child(0x80075514,store,1);m.byteset(0x801398bc,1)
  elif choice==1:child(0x80062bd8,store)
  elif choice==2:child(0x80061938,store)
  elif choice==3:child(0x80063e44,store)
  child(0x80065974)
 raise AssertionError('operation menu nontermination')
