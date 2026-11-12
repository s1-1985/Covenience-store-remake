#!/usr/bin/env python3
"""Independently recompute a naturally captured town transition, text and queue."""
import hashlib,json,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
from source_town_monthly_monitor_20261102 import FIELDS,BYTE,TABLE
from town_monthly import monthly,population
from text_buffer import TextBuffer
from event_queue import reserve

def sha(b):return hashlib.sha256(b).hexdigest()
def word(b,a):return struct.unpack_from('<I',b,a&0x1fffffff)[0]
def readstate(b):return {**{k:b[a&0x1fffffff] if k in BYTE else word(b,a) for k,a in FIELDS.items()},'history':[word(b,0x800e36a8+j*4) for j in range(60)]}
rows=[]
for path in sorted((ROOT/'town-boundaries').glob('*-before.ram.zlib')):
 before=zlib.decompress(path.read_bytes());after=zlib.decompress(path.with_name(path.name.replace('-before.','-after.')).read_bytes());assert len(before)==len(after)==2097152
 read=lambda a,n:before[(a&0x1fffffff):(a&0x1fffffff)+n]
 groups=[list(zip(*[iter(struct.unpack_from('<10h',before,0x9ff1c+j*20))]*2)) for j in range(144)]
 town=bytearray(read(0x801398f0,24000));oldtown=bytes(town);pool=read(0x8012b2f8,50800);staff=read(0x80143ff8,2100);stores=[]
 for j in range(10):
  p=j*5080;stores.append(dict(active=pool[p],rect=list(struct.unpack_from('<4i',pool,p+8)),value=struct.unpack_from('<i',pool,p+0xd5c)[0],c74=pool[p+0xc74],c75=pool[p+0xc75],c76=pool[p+0xc76]))
 order=[]
 for j in struct.unpack_from('<10i',before,0xce61c):
  if j==-1:break
  order.append(j)
 queue=bytearray(read(0x80137970,8000));text=TextBuffer(read(0x800e4020,120),word(before,0x800cd8c8),read);notifications=[]
 def notify(kind,tier):
  if kind is None:text.append(0x8009926c if tier==6 else 0x80099294,4);event=(0,0,100,1,0)
  else:
   if kind==20:text.append(0x80099258,4)
   elif kind in (22,23,24):text.append(word(before,0x800993f8+tier*4),4);text.append(0x80098f3c,0)
   else:text.lookup(struct.unpack_from('<h',before,0x98768+kind*2)[0]+98,4);text.append(0x80098f2c,0)
   event=(2,struct.unpack_from('<h',bytes.fromhex(TABLE[kind]['raw_hex']),52)[0],30,1,0)
  reserve(queue,*event,text.data);notifications.append(dict(kind=kind,tier=tier,event=event))
 state=readstate(before);expected,events,actions=monthly(town,TABLE,groups,stores,order,state,notify_text=notify)
 assert bytes(town)==after[0x1398f0:0x1398f0+24000] and readstate(after)==expected
 assert bytes(queue)==after[0x137970:0x137970+8000]
 assert text.data==after[0xe4020:0xe4020+120] and text.pos==word(after,0x800cd8c8)
 assert pool==after[0x12b2f8:0x12b2f8+50800] and staff==after[0x143ff8:0x143ff8+2100]
 changes=[]
 for k in range(3000):
  b=oldtown[k*8:k*8+8];a=town[k*8:k*8+8]
  if b!=a:changes.append(dict(cell=[k%60,k//60],before_hex=b.hex(),after_hex=a.hex(),level_before=struct.unpack_from('<b',b,2)[0],level_after=struct.unpack_from('<b',a,2)[0]))
 rows.append(dict(input=str(path.relative_to(ROOT)),clock=word(before,0x800cd93c),calendar=[word(before,a) for a in (0x800ce608,0x800ce60c,0x800ce610,0x800ce614,0x800ce618)],input_ram_sha256=sha(before),captured_output_sha256=sha(after),state_before=state,state_after=expected,events=events,actions=actions,notifications=notifications,population_before=population(oldtown,0,groups),population_after=population(town,0,groups),changed_cells=len(changes),level_changes=sum(c['level_before']!=c['level_after'] for c in changes),tile_changes=sum(oldtown[k*8:k*8+2]!=town[k*8:k*8+2] for k in range(3000)),town_sha256=sha(town),queue_sha256=sha(queue),changes=changes))
assert rows,'No natural town boundary captured'
(ROOT/'natural-town-audit.json').write_text(json.dumps(dict(all_passed=True,cases=rows,limits=['Natural function-entry RAM, no injected clock, RNG, levels, roster or cash.', 'Independent recovered policy, text and event queue; no GPU pixels or physical timing.']),indent=2)+'\n')
print(json.dumps([{k:r[k] for k in ('clock','changed_cells','level_changes','tile_changes','population_before','population_after','events','actions')} for r in rows]))
