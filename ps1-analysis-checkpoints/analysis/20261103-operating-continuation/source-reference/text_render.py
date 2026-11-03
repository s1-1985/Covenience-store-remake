"""Selected153EC/155D0 glyph render chain. Glyph IDs, not Unicode decoding."""
import struct
from cursor_control import s16

def glyph_state(code,style,initial):
 b=bytearray(initial);v=s16(code)
 if style==2:
  q=int(v/16);uv=((v-q*16)*16&255,q*16&255);page=15;width=16
 else:
  assert 0<=v<672
  page=15 if v<336 else 31;v%=336;uv=(12*(v%21)&255,16*(v//21)&255);width=12
 struct.pack_into('<H',b,0,width);struct.pack_into('<H',b,4,page);b[6:8]=bytes(uv);struct.pack_into('<2H',b,8,0,480)
 return bytes(b)

def glyph_record(x,y,state,initial,fixed):
 b=bytearray(initial);struct.pack_into('<I',b,0,0);struct.pack_into('<4H',b,4,x&65535,y&65535,12 if fixed else struct.unpack_from('<H',state)[0],15 if fixed else 16)
 b[12:20]=state[4:12];b[20:23]=bytes([128]*3);struct.pack_into('<4HI',b,24,0,0,4096,4096,0)
 return bytes(b)

def advance(x,y,linebase,code,style,flags):
 if flags&1:return linebase&65535,(y+16)&65535,flags&65534
 if code&0x4000:return x&65535,y&65535,flags
 add=([8,12,14][style] if style in [0,1,2] else 0) if s16(code)<63 else 12
 return (x+add)&65535,y&65535,flags

def render_selected(codes,style,x,y,flags,state,prior,fixed):
 out=bytearray(prior);x=(x-160)&65535;y=(y-112)&65535;linebase=x;n=0
 for c in codes:
  if c&0x4000:
   if c==0x4002:flags|=1
   if c==0x40ff:flags|=0x8000
  else:
   state=glyph_state(c,style,state);out[n*36:(n+1)*36]=glyph_record(x,y,state,out[n*36:(n+1)*36],fixed);n+=1
  x,y,flags=advance(x,y,linebase,c,style,flags)
  if flags&0x8000:flags&=0x7fff;break
 return bytes(out),n,state,flags
