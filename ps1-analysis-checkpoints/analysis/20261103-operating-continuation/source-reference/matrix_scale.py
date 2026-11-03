"""8546C: signed16 matrix columns and signed16 12-fraction-bit scale."""
import struct
from cursor_control import s16
from recovered import i32

def scale_matrix(matrix,x,y,z):
 b=bytearray(matrix);changed=0
 for column,factor in enumerate([x,y,z]):
  factor=s16(factor)
  if factor==4096:continue
  changed=1
  for row in range(3):
   off=row*6+column*2;v=struct.unpack_from('<h',b,off)[0]
   struct.pack_into('<H',b,off,(i32(v*factor)>>12)&65535)
 return bytes(b),changed
