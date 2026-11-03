"""19870 building tile to image index, including retained stack-half fallback."""
import struct
from cursor_control import s16
from recovered import i32
TABLE=[524,525,526,527,528,529,530,531,532,533]
SPECIAL={4:(True,0),5:(False,10),6:(True,32),7:(False,42),16:(True,64),17:(False,74),18:(True,96),19:(False,106)}
def tile_image(tile,x,y,stores,retained):
 tile=s16(tile)
 if tile not in SPECIAL:return tile,retained
 for b in stores:
  if b[0]==0:continue
  left,top,right,bottom=struct.unpack_from('<4i',b,8)
  if left<=i32(x)<=right and top<=i32(y)<=bottom:
   retained=struct.unpack_from('<H',b,4)[0]&127;break
 tens,offset=SPECIAL[tile];index=retained//10 if tens else retained%10
 if tens and index>=10:return tile,index
 return TABLE[index]+offset,index
