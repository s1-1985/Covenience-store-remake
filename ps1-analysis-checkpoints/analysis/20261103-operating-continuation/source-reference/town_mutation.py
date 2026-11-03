"""Full helpers: placement, demolition, flags, nearby-building search."""
import struct
from recovered import rng_next,truncdiv
from town_growth import building_kind,s8

def descriptors(table):
 out=[]
 for t in table:
  b=bytes.fromhex(t['raw_hex']);d=dict(t)
  d.update(width=struct.unpack_from('<i',b,24)[0],height=struct.unpack_from('<i',b,28)[0],attribute=b[41],groups=list(struct.unpack_from('<5h',b,42)))
  out.append(d)
 return out

def tile(town,x,y):return struct.unpack_from('<h',town,(y*60+x)*8)[0]
def replace_cell(town,x,y,d,tile_id,seed):
 k=(y*60+x)*8
 struct.pack_into('<h',town,k,tile_id)
 town[k+3]=d['attribute'];town[k+4]=d['category']&255
 town[k+5]=(town[k+5]|24) if d['category']>0 else (town[k+5]&~24)
 seed,r=rng_next(seed);struct.pack_into('<h',town,k+6,d['groups'][r%5])
 return seed

def demolish(town,x,y,mode,table,seed):
 d=table[building_kind(tile(town,x,y),table)];w=d['width']
 v=tile(town,x,y)-d['lower'];x-=v-truncdiv(v,w)*w
 # Original re-reads tile at corrected x, original y before correcting y.
 y-=truncdiv(tile(town,x,y)-d['lower'],w)
 for yy in range(y,y+d['height']):
  for xx in range(x,x+w):
   if mode==1:seed,r=rng_next(seed);replacement=table[9+r%5]
   else:replacement=table[12]
   seed=replace_cell(town,xx,yy,replacement,replacement['lower'],seed)
 return seed

def place(town,x,y,kind,mode,table,seed):
 d=table[kind];tid=d['lower']
 for yy in range(y,y+d['height']):
  for xx in range(x,x+d['width']):
   if not(0<=xx<60 and 0<=yy<50):continue
   if s8(town[(yy*60+xx)*8+4])>0:seed=demolish(town,xx,yy,mode,table,seed)
   seed=replace_cell(town,xx,yy,d,tid,seed);tid+=1
 return seed

def rebuild_flags(town,stores):
 for k in range(3000):
  c=s8(town[k*8+4]);town[k*8+5]=0 if c<=0 else (16 if c in (3,4,5) else 24)
 for s in stores:
  if not s['active']:continue
  l,t,r,b=s['rect']
  for y in range(max(0,t-10),min(49,b+10)+1):
   for x in range(max(0,l-10),min(59,r+10)+1):
    k=(y*60+x)*8+5
    if s['c76']:town[k]|=1
    if l-7<=x<=r+7 and t-7<=y<=b+7 and s['c75']:town[k]|=2
    if l-5<=x<=r+5 and t-5<=y<=b+5 and s['c74']:town[k]|=4
    if l-4<=x<=r+4 and t-4<=y<=b+4:town[k]|=8

def nearby(town,x,y,kind,radius,table):
 d=table[kind];lo,hi=(table[20]['lower'],table[21]['upper']) if kind in (20,21) else (d['lower'],d['upper'])
 for yy in range(max(0,y-radius),min(49,y+d['height']+radius-1)+1):
  for xx in range(max(0,x-radius),min(59,x+d['width']+radius-1)+1):
   if lo<=tile(town,xx,yy)<=hi:return 1
 return 0

def feasibility(town,x,y,kind,table):
 d=table[kind];c=d['category'];w,h=d['width'],d['height']
 if x<0 or y<0 or x+w>60 or y+h>50:return 1
 if c==0 or (c==1 and kind not in (20,21)):return 0
 for yy in range(y,y+h):
  for xx in range(x,x+w):
   k=(yy*60+xx)*8;flags=town[k+5];existing=s8(town[k+4]);tid=tile(town,xx,yy)
   if c==1:
    if not table[17]['lower']<=tid<=table[17]['upper']:return 1
   elif c==2:
    if flags&8:return 1
   elif c==3 and kind==49:
    if flags&16 and not table[43]['lower']<=tid<=table[48]['upper']:return 1
   elif 3<=c<=5:
    if flags&16:return 1
   elif 6<=c<=10:
    if flags&16 and not 3<=existing<=5:return 1
 return 0
