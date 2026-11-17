"""Original indexed4-bit font assets; CPU preview, not PS GPU compositing."""
import struct

def parse_font(blob):
 magic,flags=struct.unpack_from('<II',blob);assert magic==16 and flags==8
 plen,cx,cy,cw,ch=struct.unpack_from('<I4H',blob,8);assert plen==12+cw*ch*2 and cw==16 and ch==1
 palette=struct.unpack_from('<16H',blob,20);pos=8+plen
 length,x,y,width,height=struct.unpack_from('<I4H',blob,pos);assert length==12+width*height*2 and pos+length==len(blob)
 assert width==64 and height==256
 packed=blob[pos+12:];pixels=bytes(n for byte in packed for n in (byte&15,byte>>4))
 return {'flags':flags,'palette':palette,'palette_rect':(cx,cy,cw,ch),'pixel_rect':(x,y,width,height),'pixels':pixels,'width':width*4,'height':height}
def preview_rgba(font):
 def color(v):return ((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31,0 if v==0 else 255)
 return bytes(c for index in font['pixels'] for c in color(font['palette'][index]))
def glyph_indices(fonts,code,height=15):
 assert 0<=code<672 and height in (15,16)
 f=fonts[code//336];k=code%336;u=12*(k%21);v=16*(k//21)
 return b''.join(f['pixels'][(v+y)*256+u:(v+y)*256+u+12] for y in range(height))

def preview_records(fonts,records,count,size=(320,240),offset=(160,112)):
 """Opaque preview of selected fixed-font records. Preserve raw palette elsewhere.
 Ignores GPU blend, STP flags, modulation, dither, texture window, mask and backgrounds.
 """
 from PIL import Image
 im=Image.new('RGBA',size,(35,35,35,255))
 for i in range(count):
  b=records[i*36:(i+1)*36];flags,x,y,w,h,page,u,v,cx,cy=struct.unpack_from('<I4hHBB2H',b)
  assert flags==0 and w==12 and h in (15,16) and page in (15,31) and (cx,cy)==(0,480)
  f=fonts[0 if page==15 else 1];rgba=preview_rgba(f);image=Image.frombytes('RGBA',(256,256),rgba).crop((u,v,u+w,v+h));im.alpha_composite(image,(x+offset[0],y+offset[1]))
 return im
