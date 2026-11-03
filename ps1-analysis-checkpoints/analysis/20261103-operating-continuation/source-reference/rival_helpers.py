"""Original cost and layout helper rules, not general simulation assumptions."""
import struct
from recovered import i32,truncdiv
from town_growth import building_kind,s8
from store_lifecycle import word
def rword(b,a):return struct.unpack_from('<i',b,a)[0]
def product_image(image,images):
 target=truncdiv(i32(image),3)
 for product,row in enumerate(images):
  for v in row:
   if v==-1:break
   if truncdiv(v,3)==target:return product
 return 0
def equipment_total(store,prices):
 total=0
 for y in range(rword(store,0x48)):
  for x in range(rword(store,0x44)):
   v=struct.unpack_from('<I',store,0x108+y*112+x*4)[0];kind=(v>>12)&1023
   if v&0x80000000 and kind<53:total=i32(total+prices[kind])
 return total
def inventory_total(store,products,images):
 total=0
 for y in range(rword(store,0x48)):
  for x in range(rword(store,0x44)):
   v=struct.unpack_from('<I',store,0x108+y*112+x*4)[0]
   if not v&0x80000000 or (v>>12&1023)>=53:continue
   stock=struct.unpack_from('<I',store,0x178+y*112+x*4)[0];image=stock>>12&1023
   if not image:continue
   product=product_image(image,images);base,factor=products[product]
   total=i32(total+i32(truncdiv(i32(base*factor),100)*(stock>>24&127)))
 return total
def premises_total(store,mode,prices,products,images):
 unit=i32(truncdiv(rword(store,0xc70),2)+1)
 if mode==0:return i32(i32(unit*3000000)+equipment_total(store,prices)+inventory_total(store,products,images))
 if mode==1:return i32(unit*6000000)
 return 0
def land_total(town,rect):
 if not any(rect):return 0
 x0,y0,x1,y1=rect;total=0
 for y in range(y0,y1+1):
  for x in range(x0,x1+1):
   if 0<=x<60 and 0<=y<50:total=i32(total+i32(s8(town[(y*60+x)*8+2])*1000000))
 return total
def demolition_total(town,rect,table):
 mask=bytearray(3000);total=0
 if not any(rect):return total,mask
 x0,y0,x1,y1=rect
 for y in range(y0,y1+1):
  for x in range(x0,x1+1):
   if not (0<=x<60 and 0<=y<50) or mask[y*60+x]:continue
   tile=struct.unpack_from('<h',town,(y*60+x)*8)[0];d=table[building_kind(tile,table)]
   total=i32(total+i32(d['width']*d['height']*s8(d['attribute'])*1000000))
   n=tile-d['lower'];left=x-(n-truncdiv(n,d['width'])*d['width'])
   tile2=struct.unpack_from('<h',town,(y*60+left)*8)[0];top=y-truncdiv(tile2-d['lower'],d['width'])
   for yy in range(top,top+d['height']):
    for xx in range(left,left+d['width']):mask[yy*60+xx]=1
 return total,mask
def capital_post(cash,ledger,amount,flags=None):
 side=1 if flags is None else flags>>15&1
 cash[side]=i32(cash[side]-amount);ledger[side]=i32(ledger[side]+amount)
 return cash,ledger
def normalize_floor(store):
 w,h=rword(store,0x44),rword(store,0x48);state=s8(store[0xc77])
 for y in range(truncdiv(h,2)):
  for x in range(truncdiv(w,2)):
   a=0x50+y*14+x;v=s8(store[a])
   if not state and v in (28,30,32,34):store[a]=v+1
   elif state and v in (29,31,33,35):store[a]=v-1
def load_layout(store,mode,layouts,custom):
 kind=rword(store,0xc70)
 data=custom[kind] if mode==1 else layouts[kind*5+(mode-1 if mode else 0)]
 for dst,src,n in ((0x44,0,4),(0x48,4,4),(0x4c,8,4),(0x50,12,182),(0x108,196,2912)):store[dst:dst+n]=data[src:src+n]
 store[0xc77]=0;normalize_floor(store)
