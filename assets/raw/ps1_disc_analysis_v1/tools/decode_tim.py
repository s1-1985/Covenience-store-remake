from pathlib import Path
import struct,json,math
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[1];out=BASE/'images';out.mkdir(exist_ok=True)
rows=[]
def rgb(v):return ((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31,0 if v==0 else 255)
for p in sorted((BASE/'files').rglob('*.TIM')):
 b=p.read_bytes();magic,flags=struct.unpack_from('<II',b);assert magic==16;mode=flags&7;pos=8;pal=[]
 if flags&8:
  length,cx,cy,cw,ch=struct.unpack_from('<I4H',b,pos);assert length==12+cw*ch*2
  pal=list(struct.unpack_from('<'+'H'*(cw*ch),b,pos+12));pos+=length
 length,x,y,ww,h=struct.unpack_from('<I4H',b,pos);assert length==12+ww*h*2;assert pos+length==len(b)
 data=b[pos+12:pos+length];w=ww*{0:4,1:2,2:1}[mode]
 if mode==0:vals=[v for byte in data for v in [byte&15,byte>>4]]
 elif mode==1:vals=list(data)
 else:vals=list(struct.unpack('<'+'H'*(w*h),data))
 colors=[rgb(pal[v] if mode<2 else v) for v in vals];im=Image.new('RGBA',(w,h));im.putdata(colors)
 name=p.parent.name+'_'+p.stem+'.png';im.save(out/name)
 rows.append(dict(source=str(p.relative_to(BASE/'files')),png=name,width=w,height=h,bpp=[4,8,16][mode],vram_x=x,vram_y=y,palette_entries=len(pal),stp_bit='preserved in source; preview opaque except color 0',sha256_source=__import__('hashlib').sha256(b).hexdigest()))
cols=4;cw,ch=280,290;sheet=Image.new('RGB',(cw*cols,ch*math.ceil(len(rows)/cols)), '#abb4bf');d=ImageDraw.Draw(sheet)
for i,r in enumerate(rows):
 im=Image.open(out/r['png']);im.thumbnail((260,256),Image.Resampling.NEAREST);x=(i%cols)*cw+10;y=(i//cols)*ch+25;sheet.paste(im,(x,y),im);d.text((x,y-20),r['source']+' '+str(r['width'])+'x'+str(r['height']),fill='black')
sheet.save(BASE/'contact-sheet.png');(BASE/'tim-index.json').write_text(json.dumps(rows,indent=2));print(len(rows),'TIM decoded')
