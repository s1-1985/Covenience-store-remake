"""799AC descriptor tiles -> 6x6 packed half-cell buffer, original data supplied."""
import struct
def product_picture(product,random_view,images):
 if product in (20,21,26):slot=0
 else:
  n=next((i for i,z in enumerate(images[product]) if z==-1),12)
  q=((random_view&0xffffffff)>>7)*0x05b05b08>>32
  slot=(q%12)%n
 return images[product][slot]
def produce(prior,kind,mode,product,quantity,descriptor,tile_table):
 b=bytearray(prior);w,h=struct.unpack_from('<ii',descriptor,36)
 width,height=(w*2,h*2) if mode<2 else (h*2,w*2)
 for row in range(h):
  for col in range(w):
   picture=struct.unpack_from('<i',descriptor,44+row*12+col*4)[0];code=tile_table[picture][mode]
   dx,dy=(col*2,row*2) if mode<2 else (row*2,col*2);a=dy*24+dx*4
   anchor=code|((0x80000000|(mode<<22)|(kind<<12)) if row==col==0 else 0)
   for off,z in ((0,anchor),(4,code|0x400),(24,code|0x800|(product<<12)|(quantity<<24)),(28,code|0xc00)):struct.pack_into('<I',b,a+off,z&0xffffffff)
 return bytes(b),width,height
