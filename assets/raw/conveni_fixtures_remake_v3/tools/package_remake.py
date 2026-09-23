from pathlib import Path
from PIL import Image, ImageDraw
import numpy as np, scipy.ndimage as ndi, json, re, shutil, zipfile, hashlib
from functools import lru_cache
ROOT=Path(__file__).resolve().parents[1]; R=ROOT/'recovered'; O=ROOT/'output'
brief=R/'chatgpt-fixtures-products-brief-2026-09-23(1).md'; text=brief.read_text()
fixtures=[]; products=[]
for line in text.splitlines():
 cells=[c.strip() for c in line.strip('|').split('|')]
 if len(cells)==4 and re.fullmatch(r'\d+×\d+',cells[1]):
  fixtures.append(dict(id=cells[0],footprint=list(map(int,cells[1].split('×'))),size=list(map(int,cells[2].split('×'))),description=cells[3]))
 if len(cells)==5 and cells[0].isdigit():products.append(dict(id=cells[1],name_ja=cells[2],description=cells[3],notes=cells[4]))
assert len(fixtures)==44 and len(products)==25
names={'ambient':'7種の空の陳列面ピクセルアート.png','cold':'空の冷蔵棚・ワゴン配置図.png','frozen':'俯瞰の冷凍ショーケース4種.png','special':'空の屋台トレイ5種.png','vending':'真上視点・6種自販機ドット絵.png','register':'レジとディスペンサーの平面図.png','copier':'真上から見た2種のコピー機.png','amenity':'90年代風トップダウン公園・駐車場スプライト.png','break':'2つのドット絵休憩室.png','p1':'店舗用トップビュー商品在庫スプライトシート.png','p2':'5段3列のレトロ商品ピクセルオーバーレイ.png','p3':'真上構図の商品ピクセルアートシート.png','p4':'90年代風商品ドット絵グリッド.png','p5':'5カテゴリの商品ピクセル素材シート.png','drink':'ドリンク蓋のピクセルアート三列.png','plain':'無地パッケージの食品・薬品スプライトシート.png'}
@lru_cache(None)
def opened(code):return Image.open(R/names[code]).convert('RGBA')
def cut(code,box):
 a=np.array(opened(code).crop(box)); mask=a[:,:,3]>=200
 labs,n=ndi.label(mask);counts=np.bincount(labs.ravel());counts[0]=0
 if n:mask=np.isin(labs,np.where(counts>=max(3,counts.max()*.002))[0])
 a[:,:,3]=mask.astype('uint8')*255;a[~mask,:3]=0
 im=Image.fromarray(a); bb=im.getbbox()
 if not bb:raise ValueError((code,box))
 return im.crop(bb)
def fit(im,size,pad=2):
 w,h=size;r=min((w-2*pad)/im.width,(h-2*pad)/im.height)
 im=im.resize((max(1,round(im.width*r)),max(1,round(im.height*r))),Image.Resampling.NEAREST)
 out=Image.new('RGBA',size);out.alpha_composite(im,((w-im.width)//2,(h-im.height)//2));return out
F=O/'conveni_fixtures_remake_v3';P=O/'conveni_products_remake_v3'
for root in [F,P]:
 for d in ['sprites','previews','reference']:(root/d).mkdir(parents=True,exist_ok=True)
groups=[
 ('ambient',[(110,145,285,301),(410,145,725,301),(768,138,1235,301),(105,425,290,600),(408,425,728,600),(770,422,1235,600),(85,695,453,1047)]),
 ('cold',[(135,55,325,249),(510,55,720,249),(902,55,1465,249),(132,334,325,525),(440,334,800,525),(902,334,1465,525),(64,600,405,931)]),
 ('frozen',[(125,55,505,412),(700,55,1410,412),(125,533,505,895),(700,533,1410,895)]),
 ('special',[(102,77,480,443),(579,77,960,443),(1052,77,1435,443),(55,563,751,857),(786,563,1480,857)]),
 ('vending',[(135,99,418,352),(570,99,1142,352),(135,478,418,729),(570,478,1142,729),(135,875,418,1140),(570,875,1142,1140)]),
 ('register',[(162,77,653,244),(865,77,1375,244),(68,365,750,538),(786,365,1470,538),(274,642,540,929)]),
 ('copier',[(140,145,563,640),(780,145,1645,640)]),
 ('amenity',[(185,125,440,358),(591,151,865,339),(979,15,1350,382),(220,463,427,917),(626,463,837,917),(983,427,1350,931)]),
 ('break',[(205,103,855,723),(917,103,1572,723)])]
fm=[];idx=0
for code,boxes in groups:
 for box in boxes:
  spec=fixtures[idx];idx+=1;src=cut(code,box)
  a=np.array(src);lab,n=ndi.label(a[:,:,3]>0);counts=np.bincount(lab.ravel());counts[0]=0;keep=lab==counts.argmax();a[~keep]=0;src=Image.fromarray(a);src=src.crop(src.getbbox())
  size=tuple(spec['size'])
  if spec['id'] in ['potted_plant','bench','fountain','copier_a','copier_b']:im=fit(src,size)
  else:
   im=Image.new('RGBA',size);im.alpha_composite(src.resize((size[0]-4,size[1]-4),Image.Resampling.NEAREST),(2,2))
  p=F/'sprites'/f"{spec['id']}.png";im.save(p)
  fm.append({**spec,'file':str(p.relative_to(F)),'source_file':names[code],'source_crop':box,'anchor':[0,0],'content_bbox':list(im.getbbox())})
defs={}
def add(cat,code,box,cols=3,rows=3):defs[cat]=(code,box,cols,rows)
for cat,box in zip(['cold_drink','hot_drink','alcohol'],[(50,75,582,615),(671,75,1208,615),(1295,75,1827,615)]):add(cat,'drink',box)
add('bento','p1',(120,774,369,989));add('bread','p1',(115,1010,375,1240))
add('snacks','p2',(140,270,370,492));add('books','p2',(138,520,372,750));add('tobacco','p2',(142,782,371,987))
for cat,ys in zip(['stationery','retort_food','electronics','seasoning','vegetables'],[(95,276),(351,502),(600,762),(849,967),(1064,1205)]):add(cat,'p3',(15,ys[0],527,ys[1]),9,1)
add('frozen_food','p4',(78,32,337,261));add('fish','p4',(79,333,339,541));add('daily_goods','p4',(78,894,341,1131))
add('underwear','p5',(120,19,375,209),3,2);add('event_goods','p5',(112,265,379,481));add('chinese_steamed_bun','p5',(112,527,381,756));add('meat','p5',(107,802,387,1010));add('parcel_delivery_form','p5',(107,1050,383,1236))
add('instant_food','plain',(73,30,582,535));add('ice_cream','plain',(658,40,1188,540));add('medicine','plain',(69,683,606,1131));add('oden','plain',(702,647,1130,1147),2,3)
pm=[]
for spec in products:
 cat=spec['id'];code,box,cols,rows=defs[cat];x0,y0,x1,y1=box;units=[]
 for row in range(rows):
  for col in range(cols):
   b=(round(x0+(x1-x0)*col/cols),round(y0+(y1-y0)*row/rows),round(x0+(x1-x0)*(col+1)/cols),round(y0+(y1-y0)*(row+1)/rows))
   unit=cut(code,b);a=np.array(unit);lab,n=ndi.label(a[:,:,3]>0);counts=np.bincount(lab.ravel());counts[0]=0;a[lab!=counts.argmax()]=0;unit=Image.fromarray(a);units.append(unit.crop(unit.getbbox()))
 layout=[(8+16*c,8+16*r) for r in range(3) for c in range(3)];unit_size=(15,15)
 if cat=='oden':layout=[(10+24*c,9+16*r) for r in range(3) for c in range(2)];unit_size=(19,14)
 if cat=='underwear':layout=[(8+16*c,15+20*r) for r in range(2) for c in range(3)]
 if cat=='parcel_delivery_form':unit_size=(14,10)
 rendered=[fit(im,unit_size,0) for im in units];n=len(units)
 states={'high':list(range(n)),'medium':list(range(min(5,(n+1)//2))),'low':[0,n-1]}
 for state,indices in states.items():
  im=Image.new('RGBA',(64,64))
  for i in indices:im.alpha_composite(rendered[i],layout[i])
  p=P/'sprites'/f'{cat}_{state}.png';im.save(p)
  pm.append({**spec,'state':state,'size':[64,64],'file':str(p.relative_to(P)),'visible_units':len(indices),'unit_indices':indices,'source_file':names[code],'source_crop':box})
def sheet(root,entries,name,cols=5):
 cw,ch=230,205;out=Image.new('RGB',(cols*cw,((len(entries)+cols-1)//cols)*ch),'#ecedef');d=ImageDraw.Draw(out)
 for i,e in enumerate(entries):
  x=i%cols*cw;y=i//cols*ch;im=Image.open(root/e['file']);r=min(3,210/im.width,155/im.height);im=im.resize((round(im.width*r),round(im.height*r)),Image.Resampling.NEAREST)
  d.rectangle((x+4,y+4,x+cw-4,y+165),fill='#202833' if i%2 else '#fff8e8');out.paste(im,(x+(cw-im.width)//2,y+8+(150-im.height)//2),im)
  label=Path(e['file']).stem
  for k in range(0,len(label),31):d.text((x+4,y+171+k//31*13),label[k:k+31],fill='black')
 out.save(root/'previews'/name,quality=92)
for root,entries in [(F,fm),(P,pm)]:
 (root/'manifest.json').write_text(json.dumps({'tile_px':64,'alpha':'0 or 255 only','assets':entries},ensure_ascii=False,indent=2))
 sheet(root,entries,'contact_sheet.jpg');shutil.copy(brief,root/'reference/claude_brief.md')
 print(root.name,len(entries))
