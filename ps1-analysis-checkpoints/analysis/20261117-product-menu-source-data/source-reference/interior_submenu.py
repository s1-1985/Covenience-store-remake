import struct
from recovered import i32,truncdiv
from cursor_control import s16
from sprite_record import record
def choices(desc):
 values=list(struct.unpack_from('<12i',desc,84));return values[:next((i for i,v in enumerate(values) if v==-1),12)]
def blocked(product,flags):
 result=0
 for p,flag,reason in zip((8,2,22),flags,(1,2,3)):
  if flag==0 and product==p:result=reason
 return result
def navigate(index,count,buttons):
 if buttons&0x1000 and index>=4:index-=4
 if buttons&0x4000 and index<8 and index+4<count:index+=4
 if buttons&0x2000 and index not in (3,7,11) and index+1<count:index+=1
 if buttons&0x8000 and index not in (0,4,8):index-=1
 return i32(index)
def icon(prior,x,y,product,disabled,first_image):
 cell=truncdiv(i32(first_image-360),3)
 if product==20:cell=81
 if product==25:cell=80
 page=27 if cell<64 else 29
 if cell>=64:cell-=64
 row=truncdiv(cell,8);column=cell-row*8
 return record(prior,s16(x-144),s16(y-96),32,32,page,column*32,row*32,0,488,((64,)*3 if disabled else (128,)*3),1)
def restore_selection(store,backup,bounds):
 b=bytearray(store);x0,y0,x1,y1=bounds
 for y in range(y0,y1+1):
  for x in range(x0,x1+1):
   a=264+y*112+x*4;c=(y-y0)*24+(x-x0)*4;b[a:a+4]=backup[c:c+4]
 return bytes(b)
