"""SLPS_007.82 cursor state and raw render-record reconstruction."""
import struct
X,Y,SX,SY,VIEW=0x800cda42,0x800cda44,0x800cd7d6,0x800cd7d8,0x800cd9a4
IX,IY,W,H,OX,OY=0x800cd7d0,0x800cd7d2,0x800cd84c,0x800cd84e,0x800cda4c,0x800cda4e
GRID=0x8014be3c;DRAW=0x800dae38
HALVES=[X,Y,SX,SY,IX,IY,W,H,OX,OY]
def s16(v):
 v&=65535
 return v-65536 if v&32768 else v
def seth(s,a,v):s[a]=v&65535
def render(record,x,y):
 b=bytearray(record)
 struct.pack_into('<I',b,0,0x01000000)
 for off,v in [(4,x+3-160),(6,y+3-112),(8,16),(10,16),(12,7),(16,0),(18,492),(24,0),(26,0),(28,4096),(30,4096)]:struct.pack_into('<H',b,off,v&65535)
 b[14:16]=bytes([96,16]);b[20:23]=bytes([128]*3)
 struct.pack_into('<I',b,32,0)
 return bytes(b)
def town(s,mask,grid,draw):
 for bit,axis,scroll,delta,limit,margin in [(0x1000,Y,SY,-1,0,4),(0x4000,Y,SY,1,49,20),(0x8000,X,SX,-1,0,6),(0x2000,X,SX,1,59,33)]:
  v=s16(s[axis])
  if mask&bit and (v>limit if delta<0 else v<limit):
   seth(s,axis,v+delta);v=s16(s[axis]);q=s16(s[scroll])
   if v<q+margin if delta<0 else q+margin<v:seth(s,scroll,q+delta)
 if s[VIEW]==0:
  x=s16((s16(s[X])-s16(s[SX]))*8);y=s16((s16(s[Y])-s16(s[SY]))*8+25)
  b=bytearray(grid)
  for row in range(5):
   for col in range(6):struct.pack_into('<HH',b,(row*6+col)*36,(col*64-s[SX]-192)&65535,(row*64-s[SY]-144)&65535)
  grid=bytes(b)
 else:x=s16(s16(s[X])*4+38);y=s16(s16(s[Y])*4+23)
 return grid,render(draw,x,y)
def interior(s,mask,draw):
 for bit,axis,delta,limit in [(0x1000,IY,-1,0),(0x4000,IY,1,s16(s[H])-1),(0x8000,IX,-1,0),(0x2000,IX,1,s16(s[W])-1)]:
  v=s16(s[axis])
  if mask&bit and (v>limit if delta<0 else v<limit):seth(s,axis,v+delta)
 return render(draw,s16((s16(s[IX])+s16(s[OX]))*8),s16((s16(s[IY])+s16(s[OY]))*8+10))
def initialize(s,a0,a1,a2,a3,width,height):
 for a,v in [(IY,a1),(OX,a2),(OY,a3),(W,width),(H,height)]:seth(s,a,v)
 # a0 is stored on stack but never assigned to IX by original65FF4.
