from pathlib import Path
import json,math,hashlib,shutil,zipfile
from PIL import Image,ImageDraw
import numpy as np
R=Path('/workspace/scratch/058b0d3bf5df');W=R/'work/remaining';O=R/'output/conveni_remaining_assets_v1';O.mkdir(exist_ok=True)
for f in ['extracted','source_crops','generated_optional','reference','previews','tools']: (O/f).mkdir(exist_ok=True)
assets=[]
def source(t):
 p=W/f'frame_{t}.png'
 if not p.exists():p=R/f'work/extras/frame_{t}.png'
 return Image.open(p).convert('RGBA')
def add(id,name,t,b,group,notes='',confirmed=True):
 im=source(t).crop(b);im.save(O/f'source_crops/{id}.png');im.save(O/f'extracted/{id}.png')
 assets.append({'id':id,'name_ja':name,'group':group,'file':f'extracted/{id}.png','size':list(im.size),'origin':'video_crop','source_video':'【作業用BGM】ザ・コンビニ　1時間【プレイ動画】_HD_60fps(6).mp4','timestamp_seconds':t,'source_frame_size':[1280,720],'crop_xyxy':b,'name_confirmed':confirmed,'notes':notes})
for id,name,t,b in [('map_blue_hq','青・本店',150,[766,170,813,215]),('map_blue_02','青・02',150,[197,213,245,262]),('map_red_hq','赤・本店',2070,[480,263,529,312]),('map_red_02','赤・02',150,[834,507,882,553])]:
 add(id,name,t,b,'map_store_marker','文字込みの原表示。色だけで所有者の内部IDを決めない。店舗の建築タイプ1〜6とは別。')
# Keep slot identities where the recorded video never names the item.
known={(1,1,2):'消防署',(1,1,3):'マンション',(1,1,4):'会社',(1,2,2):'運動場',(1,2,3):'イベント会場',(2,1,3):'大学',(2,2,1):'公園'}
for page,cols,t in [(1,5,155),(2,4,165)]:
 for row in [1,2]:
  for col in range(1,cols+1):
   key=(page,row,col);tm=157 if key==(1,1,2) else 167 if key==(2,1,3) else t
   x=[375,493,611,729,847][col-1];y=240 if row==1 else 360
   name=known.get(key,f'誘致メニュー{page}頁・{row}行{col}列（名称未照合）')
   add(f'induce_p{page}_r{row}_c{col}',name,tm,[x,y,x+94,y+96],'induction_menu','カーソルが重ならない別時刻を選択。名称が未照合の枠は位置IDで保持。似た図柄でもメニュー上は別項目。',key in known)
for col,id in enumerate(['direct_mail','newspaper','airship','radio','television']):
 x=[375,493,611,729,847][col]
 add(f'ad_{id}_unchecked',f'{id}・未選択',191 if col==0 else 189,[x,288,x+94,384],'advertising_state','暗い表示は動画で観測した未選択状態。操作不能・無効状態とは断定しない。')
add('ad_direct_mail_checked','ダイレクトメール・選択済み',187,[375,288,469,384],'advertising_state')
# Selected newspaper is reference-only because the cursor overlaps its corner.
# Nine source pieces: corners and borders from the same opaque beige menu.
parts={'nw':[324,135,334,145],'n':[940,135,972,145],'ne':[997,135,1007,145],
'w':[324,397,334,429],'center':[950,397,982,429],'e':[997,397,1007,429],
'sw':[324,483,334,493],'s':[940,483,972,493],'se':[997,483,1007,493]}
for pos,b in parts.items():add('panel_beige_'+pos,'ベージュ窓・'+pos,155,b,'ui_panel','不透明なパネル部材。9分割画像として使用。文字を含まない部分を採用。')
add('menu_highlight_pink','メニュー選択行のピンク色',150,[433,278,470,301],'ui_selection','行背景用の不透明な色片。文字は別描画。')
# A practical panel assembled solely from the extracted pieces.
def panel(width,height):
 out=Image.new('RGBA',(width,height));s=10
 for pos,(x,y,w,h) in {'nw':(0,0,s,s),'n':(s,0,width-2*s,s),'ne':(width-s,0,s,s),'w':(0,s,s,height-2*s),'center':(s,s,width-2*s,height-2*s),'e':(width-s,s,s,height-2*s),'sw':(0,height-s,s,s),'s':(s,height-s,width-2*s,s),'se':(width-s,height-s,s,s)}.items():
  im=Image.open(O/f'extracted/panel_beige_{pos}.png');out.paste(im.resize((w,h),Image.Resampling.NEAREST),(x,y))
 return out
panel(400,180).save(O/'previews/panel_demo.png')
(O/'panel_9slice.json').write_text(json.dumps({'border_px':10,'parts':{k:f'extracted/panel_beige_{k}.png' for k in parts},'mode':'opaque','edge_resize':'nearest stretch','center_resize':'nearest stretch'},indent=2))
# Fire is newly generated; no invented claim about original frame timing.
fire=R/'generated_images/exec-4fdf524e-8ba6-4fd4-9b20-09a887240655.png'
if fire.exists():
 im=Image.open(fire).convert('RGBA');shutil.copy(fire,O/'generated_optional/fire_source.png');w,h=im.size;crops=[]
 for i in range(4):
  c=im.crop((round(i*w/4),0,round((i+1)*w/4),h));c.putalpha(c.getchannel('A').point(lambda a:255 if a>=200 else 0));bb=c.getbbox();crops.append((c,bb))
 scale=min(28/max(b[2]-b[0] for c,b in crops),44/max(b[3]-b[1] for c,b in crops))
 frames=[];sheet=Image.new('RGBA',(128,48))
 for i,(c,b) in enumerate(crops):
  art=c.crop(b);art=art.resize((max(1,round(art.width*scale)),max(1,round(art.height*scale))),Image.Resampling.NEAREST);out=Image.new('RGBA',(32,48));out.paste(art,((32-art.width)//2,46-art.height));id=f'fire_{i:02}';out.save(O/f'generated_optional/{id}.png');frames.append(out);sheet.paste(out,(i*32,0));assets.append({'id':id,'name_ja':f'火災補完フレーム{i+1}','group':'optional_effect','file':f'generated_optional/{id}.png','size':[32,48],'origin':'newly_generated','notes':'原作のフレームではない。採用判断が必要。','pivot':[16,46]})
 sheet.save(O/'generated_optional/fire_sheet.png');frames[0].save(O/'previews/fire_preview.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,disposal=2)
 (O/'generated_optional/fire_animation.json').write_text(json.dumps({'image':'fire_sheet.png','frame_size':[32,48],'count':4,'pivot':[16,46],'suggested_frame_ms':120,'timing_reconstructed':False,'original_frames':False},indent=2))
# Airship path is supplied after generation completes.
airfiles=list((W/'airship_ready').glob('*.png')) if (W/'airship_ready').exists() else []
if airfiles:
 im=Image.open(airfiles[0]).convert('RGBA');shutil.copy(airfiles[0],O/'generated_optional/airship_source.png');im.putalpha(im.getchannel('A').point(lambda a:255 if a>=200 else 0));im=im.crop(im.getbbox());im.thumbnail((62,30),Image.Resampling.NEAREST);out=Image.new('RGBA',(64,32));out.paste(im,((64-im.width)//2,(32-im.height)//2));out.save(O/'generated_optional/airship_left.png');assets.append({'id':'airship_left','name_ja':'広告飛行船・左向き（補完候補）','group':'optional_effect','file':'generated_optional/airship_left.png','size':[64,32],'origin':'newly_generated','notes':'広告アイコンの配色を参考に生成。原作の移動演出の存在・形状は未確認。画面移動は座標更新で実装し、静止画を原作アニメーションと呼ばない。','pivot':[32,16]})
for a in assets:a['sha256']=hashlib.sha256((O/a['file']).read_bytes()).hexdigest()
(O/'manifest.json').write_text(json.dumps({'asset_count':len(assets),'extracted_count':sum(a['origin']=='video_crop' for a in assets),'generated_frame_count':sum(a['origin']=='newly_generated' for a in assets),'assets':assets},ensure_ascii=False,indent=2))
cols=6;cw=190;ch=134;preview=Image.new('RGB',(cols*cw,math.ceil(len(assets)/cols)*ch),'#263340');d=ImageDraw.Draw(preview)
for i,a in enumerate(assets):
 im=Image.open(O/a['file']).convert('RGBA');im.thumbnail((96,90),Image.Resampling.NEAREST);x=i%cols*cw;y=i//cols*ch;preview.paste(im,(x+(cw-im.width)//2,y+3),im);d.multiline_text((x+4,y+98),'\n'.join(a['id'][j:j+27] for j in range(0,len(a['id']),27)),fill='white')
preview.save(O/'previews/contact_sheet.jpg',quality=94)
# Separate atlases to avoid accidentally treating newly generated replacements as verified originals.
for origin,stem in [('video_crop','extracted'),('newly_generated','optional')]:
 group=[a for a in assets if a['origin']==origin];at=Image.new('RGBA',(600,math.ceil(len(group)/6)*104));frames={}
 for i,a in enumerate(group):
  im=Image.open(O/a['file']);x=i%6*100+2;y=i//6*104+2;at.paste(im,(x,y));frames[a['id']]={'x':x,'y':y,'w':im.width,'h':im.height}
 at.save(O/f'atlas_{stem}.png');(O/f'atlas_{stem}.json').write_text(json.dumps({'image':f'atlas_{stem}.png','frames':frames},indent=2))
print('assets',len(assets))
