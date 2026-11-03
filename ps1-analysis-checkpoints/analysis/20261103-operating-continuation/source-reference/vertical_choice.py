"""Independent original4E578 vertical selection requests; InputWait supplies raw-frame polling."""
import struct
from settings_visuals import s16
from confirmation_dialog import cursor_record

def select(x,y,w,h,group,count,cursor_x,initial,model,prior):
 q=initial;y=(y+16*q)&65535;cursor=cursor_record(s16(cursor_x),s16(y+11),prior);events=[('cursor',s16(cursor_x),s16(y+11)),('rect',x&65535,y,w&65535,h&65535,group&255,0)]
 for _ in range(100):
  model.poll();events.append(('input',0))
  if model.directions&0x1000 and q>0:
   y=(y-16)&65535;q-=1;events.append(('rect',x&65535,y,w&65535,h&65535,group&255,0));b=bytearray(cursor);struct.pack_into('<H',b,6,(struct.unpack_from('<H',b,6)[0]-16)&65535);cursor=bytes(b)
  if model.directions&0x4000 and q<count-1:
   y=(y+16)&65535;q+=1;events.append(('rect',x&65535,y,w&65535,h&65535,group&255,0));b=bytearray(cursor);struct.pack_into('<H',b,6,(struct.unpack_from('<H',b,6)[0]+16)&65535);cursor=bytes(b)
  if model.buttons&0x20:return dict(result=q+1,events=events+[('sound',)],cursor=cursor,sound=1)
  if model.buttons&0x40:return dict(result=0,events=events,cursor=cursor,sound=2)
 raise AssertionError('fixture nonterminating')
