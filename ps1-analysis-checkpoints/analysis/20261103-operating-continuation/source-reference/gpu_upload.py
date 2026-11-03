"""82200 rectangle mutation and CPU/DMA writes; controlled readiness boundary."""
import struct
from cursor_control import s16
from recovered import i32
PORTS=[0x800caef0,0x800caeec,0x800caef4,0x800caef8,0x800caefc]

def plan(rect,width_limit,height_limit,data,source,ready=True,timeout=False):
 b=bytearray(rect);w,h=struct.unpack_from('<hh',b,4);wl,hl=s16(width_limit),s16(height_limit)
 w=0 if w<0 else min(w,wl);h=0 if h<0 else min(h,hl)
 struct.pack_into('<HH',b,4,w&65535,h&65535)
 product=i32(w*h+1);adjusted=i32(product+(1 if product<0 else 0));words=adjusted>>1;blocks=adjusted>>5
 if words<=0 or (not ready and timeout):return bytes(b),[],0xffffffff
 tail=words-blocks*16;writes=[(0,0x04000000),(1,0x01000000),(1,0xa0000000),(1,struct.unpack_from('<I',b)[0]),(1,struct.unpack_from('<I',b,4)[0])]
 for j in range(tail):writes.append((1,struct.unpack_from('<I',data,j*4)[0]))
 if blocks:writes += [(0,0x04000002),(2,(source+tail*4)&0xffffffff),(3,((blocks<<16)|16)&0xffffffff),(4,0x01000201)]
 return bytes(b),writes,0
