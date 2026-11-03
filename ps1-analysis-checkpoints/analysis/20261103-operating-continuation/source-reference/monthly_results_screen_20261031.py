"""Independent whole6C048 monthly results layout and numeric-slot orchestration.

Requests preserve original raw32 numeric coordinates versus sign-label signed16
coordinates; glyph/window primitives are separate components.
"""
from numeric_display_width import units
from recovered import i32
from settings_visuals import s16
import struct

def plan(x,y,values,template):
 x=i32(x);y=i32(y);values=[i32(v) for v in values];out=[]
 window=bytearray(template);struct.pack_into('<2H',window,0,x&65535,y&65535)
 out.append(dict(address=0x80017b18,args=list(struct.unpack('<2I',window[:8]))+[struct.unpack_from('<H',window,8)[0]]))
 def text(dx,dy,pointer):out.append(dict(address=0x80067338,args=[s16(x+dx)&0xffffffff,s16(y+dy)&0xffffffff,pointer]))
 def number(dx,dy,index,slot,value):out.append(dict(address=0x8004e494,args=[(x+dx)&0xffffffff,(y+dy)&0xffffffff,index],slot=slot,value=value&0xffffffff))
 for dx,dy,p in [(88,16,0x800b9540),(208,16,0x800b9548),(16,32,0x800b9554),(16,64,0x800b9564)]:text(dx,dy,p)
 e4000=None;cd938=None
 for j,(dx,dy) in enumerate([(64,32),(200,32),(64,48),(200,48)]):
  v=values[j];pad=(11-units(v))*8
  if j!=2:
   if v>0:text(dx+pad,dy,0x800b9570)
   if v<0:
    pad+=8;text(dx+pad,dy,0x800b956c);v=i32(-v)
  number(dx+8+pad,dy,272,0x800e4000,v);e4000=v
 number(106,64,372,0x800cd938,values[4]);cd938=values[4]
 text(152,64,0x800b94d4)
 v=values[5];pad=(7-units(v))*8
 if v>0:text(230+pad,64,0x800b9570)
 if v<0:
  pad+=8;text(230+pad,64,0x800b956c);v=i32(-v)
 number(240,64,372,0x800cd938,v);cd938=v
 text(288,64,0x800b94d4)
 return dict(requests=out,final_slots={0x800e4000:e4000&0xffffffff,0x800cd938:cd938&0xffffffff})
