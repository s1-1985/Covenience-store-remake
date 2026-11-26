from pathlib import Path
from PIL import Image,ImageDraw
import struct,json
BASE=Path(__file__).resolve().parents[1];out=BASE/'messages';out.mkdir(exist_ok=True)
fonts=[Image.open(BASE/'images'/f'TIM0_PSMOJI{i}.png') for i in range(2)]
for fname in ['MSG00','STAFF']:
 b=(BASE/'files/DAT'/f'{fname}.OBJ').read_bytes();n=struct.unpack_from('<I',b)[0]//4;offsets=struct.unpack_from('<'+'I'*n,b);assert all(n*4<=o<len(b) for o in offsets);rows=[]
 for i,o in enumerate(offsets):
  end=offsets[i+1] if i+1<n else len(b);codes=list(struct.unpack('<'+'H'*((end-o)//2),b[o:end]));img=Image.new('RGBA',(max(1,len(codes))*12,16));x=0;partial=''
  for c in codes:
   if c==0x40ff:break
   if c<672:
    page=c//336;idx=c%336;gx=(idx%21)*12;gy=(idx//21)*16;img.paste(fonts[page].crop((gx,gy,gx+12,gy+16)),(x,0));x+=12
    partial+=str(c) if c<10 else chr(65+c-10) if c<36 else ' ' if c==38 else f'{{{c:04X}}}'
   else:partial+=f'<CTRL:{c:04X}>'
  img=img.crop((0,0,max(1,x),16));img.save(out/f'{fname}-{i:03}.png');rows.append(dict(id=i,offset=hex(o),terminator_at_record_end=bool(codes and codes[-1]==0x40ff),codes=[hex(c) for c in codes],partial_ascii=partial))
 (BASE/f'{fname}-messages.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 if fname=='MSG00':
  sheet=Image.new('RGB',(1000,36*40),'#e8e3cf');d=ImageDraw.Draw(sheet)
  for i in range(40):
   im=Image.open(out/f'{fname}-{i:03}.png');d.text((4,i*36+10),str(i),fill='black');sheet.paste(im,(36,i*36+10),im)
  sheet.save(BASE/'message-preview.png')
 print(fname,n)
