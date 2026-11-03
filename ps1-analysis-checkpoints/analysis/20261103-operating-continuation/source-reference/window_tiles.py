"""17B18/17C3C/17FD4 frame grid; dimensions are16pixel cellcounts."""
import struct
from settings_visuals import s16
from settings_rectangles import s8,record
def window(x,y,width,height,group):
 w,h=s16(width),s16(height);start=s8(group)
 if w<2 or h<2:return []
 out=[]
 for row in range(h):
  for col in range(w):
   uv=(0x60 if row==0 else 0xc0 if row==h-1 else 0x90)+(0 if col==0 else 0x20 if col==w-1 else 0x10)
   out.append((start+len(out),s16(x-160+col*16),s16(y-112+row*16),uv))
 return out
def apply_window(shadow,base_index,calls):
 for index,x,y,uv in calls:
  o=(index-base_index)*36;b=bytearray(record(shadow[o:o+36],x,y,16,0));b[14:16]=bytes((uv,32));shadow[o:o+36]=b
