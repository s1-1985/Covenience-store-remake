from pathlib import Path
import struct,json
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[1];out=BASE/'maps';out.mkdir(exist_ok=True)
b=(BASE/'files/DAT/TOWN_PR1.CEL').read_bytes();n=struct.unpack_from('<H',b,4)[0];cells=[]
for i in range(n):
 v=struct.unpack_from('<Q',b,8+i*8)[0];cells.append(dict(id=i,u=v&255,v=(v>>8)&255,page=(v>>48)&31,flip_y=bool((v>>32)&1),flip_x=bool((v>>33)&1),attr=struct.unpack_from('<H',b,8+n*8+i*2)[0]))
(BASE/'cells.json').write_text(json.dumps(cells,indent=2));tex=Image.open(BASE/'images/TIM0_TOWN_PR1.png')
print('CEL',n,'pages',sorted(set(c['page'] for c in cells)))
for p in sorted((BASE/'files/DAT').glob('TOWN*.BIN')):
 data=p.read_bytes();records=[]
 for i in range(3000):
  off=17+8*i;tile=struct.unpack_from('<H',data,off)[0];records.append(dict(index=i,offset=hex(off),tile_id=tile,unknown_bytes=list(data[off+2:off+8])))
 (out/(p.stem+'.json')).write_text(json.dumps(dict(header=dict(first_byte=data[0],u32_unaligned=struct.unpack_from('<4I',data,1)),grid_width=60,grid_height=50,records=records),indent=2))
 for width in [60]:
  im=Image.new('RGBA',(width*8,(3000//width)*8),(190,200,180,255))
  for i,r in enumerate(records):
   c=cells[r['tile_id']];tile=tex.crop((c['u'],c['v']-96,c['u']+8,c['v']-96+8))
   if c['flip_x']:tile=tile.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
   if c['flip_y']:tile=tile.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
   im.paste(tile,((i%width)*8,(i//width)*8),tile)
  im.save(out/(p.stem+f'-width{width}.png'))
