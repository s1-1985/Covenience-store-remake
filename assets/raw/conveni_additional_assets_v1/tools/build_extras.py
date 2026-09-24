from pathlib import Path
import fitz,json,hashlib,zipfile,math
from PIL import Image,ImageDraw
import numpy as np
from scipy import ndimage as nd
ROOT=Path('/workspace/scratch/058b0d3bf5df');W=ROOT/'work/extras';O=ROOT/'output/conveni_additional_assets_v1';O.mkdir(exist_ok=True)
for f in ['source_crops','sprites','icons_32','icons_64','icons_128','previews','tools']: (O/f).mkdir(exist_ok=True)
assets=[];pdf=fitz.open(W/'downloadfile(1)(7).PDF');pages={}
def put(id,name,category,raw,im,source,notes='',icon=False):
 raw.save(O/'source_crops'/f'{id}.png');files={}
 if icon:
  for s in [32,64,128]:
   r=im.resize((s,s),Image.Resampling.LANCZOS);r.putalpha(r.getchannel('A').point(lambda x:255 if x>=200 else 0));r.save(O/f'icons_{s}/{id}.png');files[str(s)]=f'icons_{s}/{id}.png'
  runtime=files['64']
 else:
  im.save(O/f'sprites/{id}.png');runtime=f'sprites/{id}.png'
 assets.append({'id':id,'name_ja':name,'category':category,'file':runtime,'size':list(Image.open(O/runtime).size),'source_crop':f'source_crops/{id}.png','native_crop_size':list(raw.size),'variants':files,'source':source,'notes':notes,'sha256':hashlib.sha256((O/runtime).read_bytes()).hexdigest()})
def guide_icon(id,name,page,box,cat):
 if page not in pages:
  p=pdf[page-1].get_pixmap(matrix=fitz.Matrix(3,3));pages[page]=Image.frombytes('RGB',[p.width,p.height],p.samples)
 bbox=tuple(round(x*3/1.4) for x in box);raw=pages[page].crop(bbox);a=np.array(raw).astype(int);r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
 mask=(b>r+12)&(b>g-30)&(b>70);lab,n=nd.label(mask);c=np.bincount(lab.ravel());c[0]=0;mask=lab==c.argmax();ys,xs=np.where(mask);bb=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1));mask=nd.binary_closing(mask,iterations=2)
 for y in range(mask.shape[0]):
  x=np.where(mask[y])[0]
  if len(x)>1:mask[y,x[0]:x[-1]+1]=True
 mask=nd.binary_erosion(nd.binary_fill_holes(mask),iterations=2);im=raw.convert('RGBA');im.putalpha(Image.fromarray((mask*255).astype('uint8')));im=im.crop(bb)
 put(id,name,cat,raw,im,{'type':'guide','file':'downloadfile(1)(7).PDF','pdf_page':page,'printed_page':{17:107,18:108 if box[0]<600 else 109,24:121}[page],'render_scale':3,'crop_xyxy':bbox},'攻略本のメニュー図。青い枠・内部背景を保持。マップ配置用ではない。',True)
for n,p,b in [(1,17,[992,67,1102,177]),(2,17,[994,450,1104,560]),(3,18,[445,69,555,179]),(4,18,[442,454,552,564]),(5,18,[994,64,1104,174]),(6,18,[995,447,1105,557])]:guide_icon(f'store_type_{n:02}',f'店舗{n}の選択アイコン',p,b,'store_menu')
for id,name,y in [('direct_mail','ダイレクトメール',122),('newspaper','新聞広告',273),('airship','飛行船',425),('radio','ラジオCM',577),('television','テレビCM',728)]:guide_icon('advertising_'+id,name,24,[645,y-56,757,y+56],'advertising_menu')
def video(id,name,box,cat='interior',t=900,poly=None,hole=None,notes='',size=None):
 frame=Image.open(W/f'frame_{t}.png').convert('RGB');raw=frame.crop(box);im=raw.convert('RGBA')
 if poly:
  m=Image.new('L',im.size);d=ImageDraw.Draw(m);d.polygon([(x-box[0],y-box[1]) for x,y in poly],fill=255)
  if hole:d.polygon([(x-box[0],y-box[1]) for x,y in hole],fill=0)
  im.putalpha(m)
 if size:im=im.resize(size,Image.Resampling.NEAREST)
 put(id,name,cat,raw,im,{'type':'video','file':'【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps(6).mp4','timestamp_seconds':t,'frame_size':[1280,720],'crop_xyxy':box,'alpha_polygon_absolute':poly,'alpha_hole_absolute':hole},notes)
video('entrance_in','入店側の入口',[410,240,456,285],t=904,notes='下向き赤矢印・マット・敷居を含む。不透明な建築部材。')
video('entrance_out','退店側の入口',[456,240,503,285],t=904,notes='上向き赤矢印・マット・敷居を含む。不透明な建築部材。')
video('floor_blue_repeat','店内の青い床',[342,532,389,579],notes='無人の床を切り出した反復用候補。映像の拡大・圧縮で境界に微差あり。ゲームの1マスと同義ではない。')
video('ground_exterior_gray','店舗外の灰色舗装',[600,125,647,172],notes='舗装の反復用候補。ゲームの1マスと同義ではない。')
video('ground_perimeter_tan','店舗周囲の茶色地面',[190,350,210,370],notes='外周帯の地面。細い帯からの切り出しで、小面積向け。')
# Narrow border strips and corners, kept at capture scale rather than pretending to be one tile.
for id,name,box in [
 ('wall_west','左外周線',[211,350,222,397]),('wall_east','右外周線',[689,350,700,397]),
 ('wall_north','上外周線',[550,277,597,286]),('wall_south','下外周線',[550,624,597,637]),
 ('wall_nw','外周左上角',[211,277,223,290]),('wall_ne','外周右上角',[688,277,700,290]),
 ('wall_sw','外周左下角',[211,624,224,637]),('wall_se','外周右下角',[688,624,700,637])]:
 video(id,name,box,notes='動画の外周線部材。元画面の拡大率に依存する。辺は長辺方向だけを伸縮・反復し、角は伸縮しない。隣の什器色が端に残る可能性あり。')
video('status_tobacco','たばこの表示アイコン',[654,646,696,687],'status',poly=[(655,676),(661,670),(664,663),(679,650),(681,646),(686,647),(690,650),(695,654),(691,660),(677,673),(669,681),(665,687),(660,684),(658,681),(654,680)],notes='煙を含む手動輪郭。販売許可等との正確な表示条件は未確定。')
video('status_alcohol','酒の表示アイコン',[698,643,739,688],'status',poly=[(700,657),(704,652),(703,648),(708,648),(710,643),(719,643),(721,648),(726,647),(730,654),(729,658),(735,661),(738,664),(738,679),(734,683),(730,683),(729,687),(700,687),(698,683),(698,660)],hole=[(729,667),(731,667),(731,675),(729,675)],notes='ビールジョッキ。元映像の小さな持ち手内側を透過。表示条件は未確定。')
video('status_medicine','薬の表示アイコン',[742,644,786,688],'status',poly=[(749,644),(777,644),(777,649),(781,649),(781,656),(785,656),(785,687),(742,687),(742,656),(748,656),(748,649)],hole=[(756,653),(771,653),(771,656),(756,656)],notes='救急箱。取っ手の穴を透過。表示条件は未確定。')
video('cursor_pointer','白い矢印カーソル',[724,349,756,400],'cursor',poly=[(728,351),(730,351),(734,356),(741,362),(748,369),(753,373),(753,377),(743,378),(744,382),(748,388),(752,392),(752,397),(747,398),(743,394),(739,387),(736,379),(734,379),(730,383),(726,383),(726,353)],notes='白い矢印と輪郭を保持。hotspotは元切り出し内[4,2]。映像由来の輪郭のにじみあり。')
# Store data transcribed from printed pages; keep guide inconsistency visible, never silently correct it.
store_data=[{'id':f'store_type_{i+1:02}','interior_wh':a,'building_wh':b,'outside_wh':c} for i,(a,b,c) in enumerate([([5,8],[7,10],[3,10]),([8,5],[10,7],[10,3]),([7,10],[9,12],[3,12]),([10,7],[12,9],[12,3]),([8,12],[10,14],[3,14]),([12,8],[14,10],[14,3])])]
(O/'store_type_reference.json').write_text(json.dumps({'source':'guide PDF17–18 / printed106–109','units':'guide building grid, not image pixels','note':'店舗5の床面積欄108と8×12=96が食い違う。原資料の誤記の可能性があり、実装時に画面と照合すること。','stores':store_data},ensure_ascii=False,indent=2))
manifest={'asset_count':len(assets),'origin':'extracted_from_user_supplied_sources','generated_assets':0,'source_pdf_sha256':hashlib.sha256((W/'downloadfile(1)(7).PDF').read_bytes()).hexdigest(),'assets':assets}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
cols=6;cw,ch=190,136;preview=Image.new('RGB',(cols*cw,math.ceil(len(assets)/cols)*ch),'#27323e');d=ImageDraw.Draw(preview)
for i,a in enumerate(assets):
 im=Image.open(O/a['file']).convert('RGBA');im.thumbnail((90,80),Image.Resampling.NEAREST);x=i%cols*cw;y=i//cols*ch;preview.paste(im,(x+(cw-im.width)//2,y+6),im);d.multiline_text((x+4,y+94),'\n'.join(a['id'][j:j+27] for j in range(0,len(a['id']),27)),fill='white')
preview.save(O/'previews/contact_sheet.jpg',quality=94)
# Runtime atlas (all native runtime rectangles, no rescaling); two transparent pixels of gutter.
ax=ay=2;rowh=0;placements=[]
for a in assets:
 im=Image.open(O/a['file']).convert('RGBA')
 if ax+im.width+2>512: ax=2;ay+=rowh+4;rowh=0
 placements.append((a,im,ax,ay));ax+=im.width+4;rowh=max(rowh,im.height)
at=Image.new('RGBA',(512,ay+rowh+2));frames={}
for a,im,x,y in placements:at.paste(im,(x,y));frames[a['id']]={'x':x,'y':y,'w':im.width,'h':im.height}
at.save(O/'atlas.png');(O/'atlas.json').write_text(json.dumps({'image':'atlas.png','frames':frames},indent=2))
# Texture repetition is shown as an inspection aid, not a claim of exact autotile restoration.
tex=Image.new('RGB',(576,192))
for i,id in enumerate(['floor_blue_repeat','ground_exterior_gray','ground_perimeter_tan']):
 im=Image.open(O/f'sprites/{id}.png').convert('RGB').resize((64,64),Image.Resampling.NEAREST)
 for y in range(3):
  for x in range(3):tex.paste(im,(i*192+x*64,y*64))
tex.save(O/'previews/texture_repeat.png')
print('assets',len(assets))
