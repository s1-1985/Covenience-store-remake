"""182D0 rectangle decomposition ->185A4 36byte records, native templateUV."""
import struct
from settings_visuals import s16
UV=bytes.fromhex('703080309030b010c010d030c030e030')
def s8(v):v&=255;return v-256 if v&128 else v
def rectangle(x,y,w,h,group,mode):
 w=s16(w);h=s16(h);start=s8(group);x=s16(x-160);y=s16(y-112);out=[]
 if w==0:return out
 if w<16:return [(start,x,y,2 if w==1 else w,mode)]
 cols=w//16;rows=max(0,int(h/16));rem=w%16;index=start
 for row in range(rows):
  for col in range(cols):
   out.append((index,s16(x+16*col),s16(y+16*row),16,mode));index+=1
   if col==cols-1 and rem:out.append((index,s16(x+16*(col+1)),s16(y+16*row),rem,mode));index+=1
 return out
def record(initial,x,y,width,mode):
 assert 0<=mode<8;b=bytearray(initial);struct.pack_into('<I',b,0,0x1000000)
 for o,v in ((4,x),(6,y),(8,width),(10,16),(12,7),(16,0),(18,492),(24,0),(26,0),(28,4096),(30,4096)):struct.pack_into('<H',b,o,v&65535)
 b[14:16]=UV[2*mode:2*mode+2];b[20:23]=bytes((128,128,128));struct.pack_into('<I',b,32,0);return bytes(b)
def apply_records(shadow,base_index,calls):
 for index,x,y,w,mode in calls:
  offset=(index-base_index)*36;shadow[offset:offset+36]=record(shadow[offset:offset+36],x,y,w,mode)
