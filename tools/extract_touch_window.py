"""Build the shipped 48px nine-piece KYOU frame from the original r2 archive.
Original binding image8/KYOU.TIM, UV96..224 row32; source analysis 20261117.
Not needed to run/build: resulting window_frame.png is committed.
"""
import argparse,struct,zipfile,hashlib
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('archive');p.add_argument('output');a=p.parse_args()
with zipfile.ZipFile(a.archive) as z:
 b=z.read('algorithm-analysis/source/KYOU.TIM')
assert struct.unpack_from('<II',b)==(16,9)
n=struct.unpack_from('<I',b,8)[0];palette=struct.unpack('<256H',b[20:8+n]);offset=8+n;size,x,y,w,h=struct.unpack_from('<I4H',b,offset)
rgba=[tuple(((c>>s)&31)*255//31 for s in (0,5,10))+(0 if c==0 else 255,) for c in palette]
im=Image.new('RGBA',(w*2,h));im.putdata([rgba[c] for c in b[offset+12:offset+size]])
frame=Image.new('RGBA',(48,48))
for i in range(9):frame.paste(im.crop((96+i*16,32,112+i*16,48)),((i%3)*16,(i//3)*16))
frame.save(a.output)
print(hashlib.sha256(Path(a.output).read_bytes()).hexdigest())
