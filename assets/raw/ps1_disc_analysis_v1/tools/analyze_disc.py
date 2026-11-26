import struct,json,hashlib,collections
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--bin',type=Path,default=BASE.parent/'upload/SLPS_00782.BIN');args=parser.parse_args()
SRC=args.bin
raw=SRC.read_bytes()
def sector(n):return raw[n*2352+24:n*2352+24+2048]
def payload(lba,size):return b''.join(sector(n) for n in range(lba,lba+(size+2047)//2048))[:size]
def u32(b,o):return struct.unpack_from('<I',b,o)[0]
rows=[]
def walk(lba,size,parent=''):
 directory=payload(lba,size);pos=0
 while pos<len(directory):
  n=directory[pos]
  if not n:pos=(pos//2048+1)*2048;continue
  rec=directory[pos:pos+n];pos+=n
  name=rec[33:33+rec[32]]
  if name in (b'\x00',b'\x01'):continue
  name=name.decode('ascii').split(';')[0];path=parent+'/'+name
  start,length=u32(rec,2),u32(rec,10)
  if rec[25]&2:walk(start,length,path);continue
  content=payload(start,length);dest=BASE/'files'/path.lstrip('/');dest.parent.mkdir(parents=True,exist_ok=True)
  forms=collections.Counter('form2' if raw[k*2352+18]&32 else 'form1' for k in range(start,start+(length+2047)//2048))
  extraction='logical2048'
  if forms.get('form2',0):
   content=raw[start*2352:(start+(length+2047)//2048)*2352]
   dest=dest.with_name(dest.name+'.raw2352');extraction='raw2352; ISO size uses 2048 units, Form2 data preserved'
  dest.write_bytes(content)
  rows.append(dict(extraction=extraction,extracted_name=str(dest.relative_to(BASE/'files')),path=path,lba=start,size=length,sha256=hashlib.sha256(content).hexdigest(),head=content[:32].hex(),sector_forms=dict(forms)))
pvd=sector(16);root=pvd[156:190];walk(u32(root,2),u32(root,10))
(BASE/'inventory.json').write_text(json.dumps(rows,indent=2))
print(f'{len(rows)} files indexed/extracted')
