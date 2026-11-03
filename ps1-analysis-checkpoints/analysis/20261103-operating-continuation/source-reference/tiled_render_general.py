"""83B4C positive-dimension path, including odd-phase raw memory writes."""
import struct
from cursor_control import s16

def tiled_general(record,header,tiles,indices,ox,oy,base,oldlink,initial):
 b=bytearray(initial);offset=0;quads=0;rects=0;t=struct.unpack_from('<I',record)[0]
 if t&0x80000000:return bytes(b),0,0,0
 tw=header[0] or 256;th=header[1] or 256;cols,rows=struct.unpack_from('<HH',header,2)
 x,y,w,h,sx,sy=struct.unpack_from('<6h',record,4);px,py=struct.unpack_from('<hh',record,24)
 assert cols>0 and rows>0 and w>0 and h>0
 sx%=tw*cols;sy%=th*rows
 attrs=((t>>5)&0x02000000)|((t<<18)&0x01000000)
 rgb=(record[18]<<16)|(record[17]<<8)|record[16]
 color=0x64000000|attrs|rgb;quadcolor=0x2c000000|attrs|rgb
 pagebits=((t>>17)&0x180)|((t>>23)&0x60)
 def word(o,v):struct.pack_into('<I',b,offset+o,v&0xffffffff)
 def half(o,v):struct.pack_into('<H',b,offset+o,v&65535)
 def byte(o,v):b[offset+o]=v&255
 yy=0
 while yy<h:
  fy=(sy+yy)%th;dh=min(th-fy,h-yy);xx=0
  while xx<w:
   fx=(sx+xx)%tw;dw=min(tw-fx,w-xx)
   index=indices[((sy+yy)%(th*rows)//th)*cols+((sx+xx)%(tw*cols)//tw)]
   if index!=65535:
    u,v,clut,unused,tp=struct.unpack('<BBHHH',tiles[index]);xx0=(x-px+s16(ox)+xx)&65535;yy0=(y-py+s16(oy)+yy)&65535
    if xx==0 and (sx&1):
     # 40-byte one-pixel strip; +1E/+26 are untouched padding.
     word(0,((base+offset+40)&0xffffff)|0x09000000);word(4,quadcolor)
     for o,a,c in [(8,xx0,yy0),(16,xx0+1,yy0),(24,xx0,yy0+dh),(32,xx0+1,yy0+dh)]:half(o,a);half(o+2,c)
     for o,vy in [(12,v+fy),(20,v+fy),(28,v+fy+dh),(36,v+fy+dh)]:byte(o,u+fx);byte(o+1,vy)
     half(14,clut);half(22,pagebits|(tp&31));offset+=40;quads+=1
    rw=(dw&65534) if xx==0 else dw
    if rw:
     shift=(sx&1) if xx==0 else 0
     word(0,((base+offset+24)&0xffffff)|0x05000000);word(4,0xe1000200|pagebits|(tp&31));word(8,color)
     word(12,((xx0+shift)&65535)|(yy0<<16))
     uvx=((u+fx+1)&254) if xx==0 else u
     word(16,uvx|(((v+fy)&255)<<8)|(clut<<16));word(20,rw|(dh<<16));offset+=24;rects+=1
   xx+=dw
  yy+=dh
 if offset:
  # Native84260 subtracts24 unconditionally, even if the final packet was40 bytes.
  struct.pack_into('<I',b,offset-24,(oldlink&0xffffff)|0x05000000)
 return bytes(b),offset,quads,rects
