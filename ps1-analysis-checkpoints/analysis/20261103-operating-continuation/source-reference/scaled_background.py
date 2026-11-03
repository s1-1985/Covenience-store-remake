"""83338 quad segmentation and OT link; GTE outputs supplied by explicit boundary."""
import struct
from recovered import i32
from quad_packet import quad_packet

def scaled_background(record,header,tiles,indices,ox,oy,base,oldlink,initial,vector=None):
 b=bytearray(initial);off=0;metas=[];flags=struct.unpack_from('<I',record)[0];cols,rows=struct.unpack_from('<2H',header,2)
 if flags&0x80000000 or not cols or not rows:return bytes(b),0,metas
 tw=header[0] or 256;th=header[1] or 256;x,y,w,h,sx,sy=struct.unpack_from('<6h',record,4);px,py=struct.unpack_from('<2h',record,24)
 assert w>0 and h>0
 sx%=tw*cols;sy%=th*rows
 transform=not flags&0x08000000 and (struct.unpack_from('<I',record,28)[0]!=0x10001000 or struct.unpack_from('<I',record,32)[0]!=0)
 assert not transform or vector is not None
 pagebits=((flags>>17)&0x180)|((flags>>23)&0x60);cmd=0x2c|((flags>>29)&2)|((flags>>6)&1)
 yy=0
 while yy<h:
  fy=(sy+yy)%th;dh=min(th-fy,h-yy);row=((sy+yy)%(th*rows))//th;xx=0;col=sx//tw;fx=sx%tw;dw=min(tw-fx,w)
  first=True
  while True:
   index=indices[row*cols+col]
   if index!=65535:
    u,v,clut,flip,tp=struct.unpack('<BBHHH',tiles[index]);uvx=(u if flip&2 else u+fx) if first else (u+tw-dw if flip&2 else u)
    uvy=v+th-dh-fy if flip&1 else v+fy
    meta=bytearray(28);meta[0:4]=bytes([cmd,*record[16:19]]);struct.pack_into('<2H',meta,4,pagebits|(tp&31),clut);meta[8:10]=bytes([uvx&255,uvy&255]);struct.pack_into('<8H',meta,10,x&65535,y&65535,dw&65535,dh&65535,(xx-px)&65535,(yy-py)&65535,flip,int(transform));struct.pack_into('<I',meta,24,int(transform))
    metas.append(bytes(meta));struct.pack_into('<I',b,off,((base+off+40)&0xffffff)|0x09000000)
    out,_=quad_packet(meta,b[off+4:off+40],ox,oy,vector if transform else None);b[off+4:off+40]=out;off+=40
   # Native first and following quads test the current start before advancing.
   if not xx<w:break
   xx+=dw;col=(col+1)%cols;dw=min(tw,w-xx);first=False
  yy+=dh
 if off:struct.pack_into('<I',b,off-40,(oldlink&0xffffff)|0x09000000)
 return bytes(b),off,metas
