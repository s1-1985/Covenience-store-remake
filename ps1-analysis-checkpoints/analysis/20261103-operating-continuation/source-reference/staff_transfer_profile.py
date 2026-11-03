"""73100/74150 independent transfer-profile call production.
Only offsets/indices are named; no inferred stat names. Native discarded
conversion of uninitialized right local+68 has no effect on emitted calls.
"""
import struct
from recovered import i32
from cursor_control import s16
from opening_staff_display import bar_width
from staff_transfer_binding import TEMP

def profile(m,x,y,right,child):
 index=m.word(0x800cd9c8 if right else 0x800cd9c4);row=m.word(0x800cd9b0 if right else 0x800cd9ac);store=m.word(0x800cda1c if right else 0x800cda18)
 pulse=struct.unpack('<b',m.read(0x800cda21 if right else 0x800cda20,1))[0]
 child(0x80070194,s16(x+88 if right else x),s16(y+16),index,row,pulse)
 child(0x8006b780,i32(x+(72 if right else 8)),i32(y),store)
 for msg,dx in ((270,64 if right else 0),(269,120 if right else 56)):child(0x800155d0,msg|(((x+dx)&65535)<<16),y&65535)
 sid=s16(m.word(TEMP+index*12+row*4))
 if sid==-1:return
 p=0x80143ff8+sid*60
 sb=lambda off:struct.unpack('<b',m.read(p+off,1))[0]
 hours=struct.unpack('<b',m.read(0x800cd750+m.word(store+0xc78),1))[0]
 def text(dx,dy,msg):child(0x8004e494,s16(x+dx),s16(y+dy),s16(msg))
 def rect(width,dy,mode):
  xx=s16(x+56-width if right else x+72);yy=s16(y+dy);n=child(0x800182d0,(xx&65535)|((yy&65535)<<16),(width&65535)|(16<<16),m.byte(0x800cda14),mode)
  count=int.from_bytes(m.read(0x800cda14,2),'little');m.write(0x800cda14,struct.pack('<H',(count+n)&65535))
 text(0 if right else 48,16,150+sb(2));m.wordset(0x800cd938,sb(3));text(0 if right else 48,32,294+sb(4))
 for off,dy in ((25,48),(26,64),(30,80),(31,96),(34,112),(33,128),(32,144)):
  m.wordset(0x800cd938,sb(off));text(56 if right else 48,dy,369);rect(bar_width(sb(off)),dy,3)
  if off==25:rect(bar_width(sb(24)),dy,4)
 m.wordset(0x800e4000,i32(m.word(p+12)*hours));text(16 if right else 48,160,296)
