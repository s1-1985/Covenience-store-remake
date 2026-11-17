"""4095C HUD constructor model; selector meaning remains unnamed."""
import struct
from recovered import i32
from text_controls import ExpandBuffer,expand_stream
from text_render import render_selected
SEASONAL=((0,1,2,3,4),(0,1,2,3,4),(0,1,2,5,6),(0,1,2,5,6),(0,1,2,5,6),(0,1,2,5,6),(0,1,2,5,7),(0,1,2,5,7),(0,1,2,5,8),(0,1,2,5,8),(0,1,2,5,6),(0,1,2,3,4))
def calendar(t):
 t&=0xffffffff;q=((t*0x88888889)>>32)>>5
 return [(((t*0xf2b9d649)>>32)>>16)+1,(((t>>7)*0x05b05b08)>>32)%12+1,((((t>>5)*0x05b05b06)>>32)&3)+1,q%24,(t-60*q)&0xffffffff]
def selection(t,value):
 v=i32(value);col=0 if v==0 else 1 if v<20 else 2 if v<50 else 3 if v<80 else 4
 return 62+SEASONAL[calendar(t)[1]-1][col]
def bars(prior):
 b=bytearray(prior)
 for i in range(2):
  p=36*i;struct.pack_into('<I4hHBB2H',b,p,0x01000000,-160+160*i,-112,160,24,7,96,184,0,492);b[p+20:p+23]=bytes([128]*3);struct.pack_into('<4HI',b,p+24,0,0,4096,4096,0)
 return bytes(b)
def hud(t,money,selector,style,flags,state,prior,buffer,messages):
 cache=calendar(t);out=bytearray(prior);n=0;calls=[]
 for index,x in [(60,8),(selection(t,selector),108),(61,152)]:
  b=ExpandBuffer(buffer,0);used=expand_stream(messages[index],b,{'variable':{0:i32(money)},'two':dict(enumerate(cache))},{},0,0)
  codes=list(struct.unpack_from('<'+'H'*b.pos,b.data,64));tail,count,state,flags=render_selected(codes,style,x,6,flags,state,out[n*36:],True);out[n*36:]=tail;n+=count;buffer=bytes(b.data);calls.append((index,x,6,used))
 return bytes(out),n,state,flags,buffer,cache,calls
