"""Full store initialization, staff unlink/rebind, and town-side closure."""
import struct
from town_mutation import place,rebuild_flags
SIZE=5080
def word(b,a,v):struct.pack_into('<I',b,a,v&0xffffffff)
def initialize(store,mode,template,defaults):
 store[:]=bytes(SIZE)
 for a,v in ((0x30,16),(0xc68,10),(0xc6c,20),(0x12dc,3)):word(store,a,v)
 for j in range(3):struct.pack_into('<h',store,0xdd8+j*2,-1)
 store[0x12e0]=1
 for j in range(60):word(store,0x12e8+j*4,0x80000000)
 word(store,0xc78,2 if mode else struct.unpack_from('<I',template,0xc78)[0])
 for j in range(27):word(store,0xc7c+j*4,defaults[j] if mode else struct.unpack_from('<I',template,0xc7c+j*4)[0])

def staff_binding(store,staff,mode):
 ids=struct.unpack_from('<3h',store,0xdd8)
 for j,k in enumerate(ids):
  if k==-1:continue
  if mode:
   staff[k][:2]=store[4:6]
  else:
   staff[k][:2]=b'\0\0';staff[k][0x19]=staff[k][0x18];struct.pack_into('<h',store,0xdd8+j*2,-1)
 if not mode:return
 for a in (0xce8,0xd38,0xd88):store[a:a+80]=bytes(80)
 store[0x1184:0x1186]=bytes(2)
 for a in (0x1188,0x118c,0x1194):word(store,a,0)
 store[0x1190]=0;store[0x1198:0x12dc]=bytes(0x144);store[0x12e1:0x12e5]=bytes(4)
 for j in range(60):word(store,0x12e8+j*4,0x80000000)

def close(town,table,stores,index,seed,template,defaults):
 store=stores[index];x,y,x2,y2=struct.unpack_from('<4i',store,8)
 for xx,yy in ((x,y),(x2,y),(x,y2),(x2,y2)):seed=place(town,xx,yy,12,0,table,seed)
 initialize(store,0,template,defaults)
 descriptors=[]
 for s in stores:
  descriptors.append(dict(active=s[0],rect=struct.unpack_from('<4i',s,8),c74=s[0xc74],c75=s[0xc75],c76=s[0xc76]))
 rebuild_flags(town,descriptors)
 return seed
