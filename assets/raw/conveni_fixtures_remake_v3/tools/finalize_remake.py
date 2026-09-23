from pathlib import Path
from PIL import Image,ImageDraw
import json, shutil, zipfile, hashlib, numpy as np
ROOT=Path(__file__).resolve().parents[1];O=ROOT/'output'
F=O/'conveni_fixtures_remake_v3';P=O/'conveni_products_remake_v3'
fm=json.loads((F/'manifest.json').read_text());pm=json.loads((P/'manifest.json').read_text())
for e in fm['assets']:
 id=e['id'];w,h=e['size']
 e['normalization']='fit_preserving_aspect' if id in ['potted_plant','bench','fountain','copier_a','copier_b'] else 'normalized_to_footprint_inner_canvas'
 if any(x in id for x in ['shelf','wagon','case']):
  e['overlay_slots']=[{'origin':[x*64,y*64],'size':[64,64]} for y in range(h//64) for x in range(w//64)]
 elif id in ['register_2','register_4']:
  e['overlay_slots']=[{'origin':[w-31,18],'size':[26,26],'category':'parcel_delivery_form'}]
 else:e['overlay_slots']=[]
 if 'refrigerated' in id or 'frozen' in id:
  e['overlay_slots']=[{'origin':[x*64+6,y*64+10],'size':[52,52]} for y in range(h//64) for x in range(w//64)]
(F/'manifest.json').write_text(json.dumps(fm,ensure_ascii=False,indent=2))
pairs=[('small_ambient_shelf','snacks'),('medium_ambient_shelf','books'),('small_refrigerated_shelf','cold_drink'),('small_frozen_wagon','ice_cream'),('oden_case','oden'),('steamed_bun_case','chinese_steamed_bun'),('event_shelf','event_goods'),('register_2','parcel_delivery_form')]
out=Image.new('RGB',(1000,len(pairs)*155),'#edf0f2');d=ImageDraw.Draw(out)
for row,(fixture,prod) in enumerate(pairs):
 e=next(e for e in fm['assets'] if e['id']==fixture)
 for c,state in enumerate(['high','medium','low']):
  im=Image.open(F/e['file']).convert('RGBA');ov=Image.open(P/'sprites'/f'{prod}_{state}.png')
  for slot in e['overlay_slots']:
   part=ov.resize(tuple(slot['size']),Image.Resampling.NEAREST);im.alpha_composite(part,tuple(slot['origin']))
  im=im.resize((im.width*2,im.height*2),Image.Resampling.NEAREST)
  x=c*330;y=row*155;d.rectangle((x,y,x+325,y+134),fill='#283543' if c%2 else '#faf5df');out.paste(im,(x+10,y+3),im)
  d.text((x+5,y+137),fixture+' / '+state,fill='black')
out.save(F/'previews/composite_examples.jpg',quality=92);shutil.copy(F/'previews/composite_examples.jpg',P/'previews/composite_examples.jpg')
intro='''# Claudeへの引継ぎ：什器・商品リメーク v3

2026-09-23の添付仕様書に対応。客・店員・建物パッケージは変更しない。
本データは原作から抜き出した画像ではなく、新規生成画像を切り出し・整形した素材である。
仕様書にある原資料のfootprintと、今回定義された64px換算・新規の外観を区別すること。

## 共通仕様

- 1タイル64px。PNGはRGBA、アルファは0/255の二値。ラベルは個別PNGに含めない。
- 元画像のアルファを使い、半透明の輪郭・孤立ノイズを整理した。背景色によるクロマキー処理は使っていない。
- 什器は上面を基準とした表示。多段棚の正面図や斜めの旧生成版は収録対象から外した。
- 四角い什器は最終キャンバスの内側2pxを除く枠へ正規化。元生成シートの不正確な比率をそのまま実装に使わない。
- 植物・ベンチ・噴水・コピー機は元の縦横比を維持してキャンバス内へ配置。
- 拡大表示はnearest-neighborを推奨。回転は両レイヤーを同一原点で90度単位に回転する。

## ファイル

sprites/ が実装用。manifest.json がID・寸法・参照元の対応表。
previews/contact_sheet.jpg は明暗背景での一覧。
previews/composite_examples.jpg は商品を重ねた表示例。
sources/ は採用した生成シート。そこにあるラベルや在庫の並びを実装用PNGと混同しない。
reference/claude_brief.md はユーザーから受領した仕様書。

## 商品の重ね方

商品は25カテゴリ×high/medium/lowの75枚、全て64×64px。
同じ切り出し商品を同じ位置・大きさで使い、在庫段階では表示数のみ減らす。
表示個数はゲーム上の在庫数そのものではない。manifestのvisible_unitsは見た目の個数である。
通常は9→5→2、下着・おでんは6→3→2。冷蔵・冷凍は上面の通気部を避けるためスロット内で52×52pxに縮小する。
什器のoverlay_slotsに商品をalpha合成する。2×1や3×1はタイルごとに繰り返す。
parcel_delivery_formはregister_2/4の指定領域だけに縮小配置する。
自販機・ATMは上面の筐体表示であり、正面パネルは見せない。商品オーバーレイを屋根へ自動で重ねない。
copy_paper、cash、汎用vending_machineは独立商品・什器として追加していない。

## 確認範囲

攻略本の印刷82〜83ページの店内画面、110〜119ページの設備資料を参照した。
PS5動画の25分付近の配置画面を拡大確認し、ほか10・15・40・60・80分付近の静止画を照合した。
動画全編の解析や原作ピクセルの完全一致を意味しない。
今回の整形時には送信済み・生成済みのデータだけを用い、追加の画像生成は行っていない。
実ゲームへの組込み動作確認は未実施。商品配置の実装例と実際の利用面・当たり判定は分けて扱う。
'''
for root,manifest in [(F,fm),(P,pm)]:
 (root/'README_CLAUDE.md').write_text(intro)
 (root/'sources').mkdir(exist_ok=True)
 for name in sorted(set(e['source_file'] for e in manifest['assets'])):shutil.copy(ROOT/'recovered'/name,root/'sources'/name)
 checks=[]
 for e in manifest['assets']:
  p=root/e['file'];im=Image.open(p);im.load();a=np.array(im)
  assert im.mode=='RGBA' and list(im.size)==e['size']
  assert set(np.unique(a[:,:,3])).issubset({0,255})
  assert np.all(a[a[:,:,3]==0,:3]==0)
  assert im.getbbox() is not None
  checks.append({'file':e['file'],'size':list(im.size),'alpha_values':sorted(map(int,np.unique(a[:,:,3]))),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 (root/'validation.json').write_text(json.dumps({'count':len(checks),'all_checks_passed':True,'checks':checks},indent=2))
 zpath=root.with_suffix('.zip')
 with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,9) as z:
  for p in sorted(root.rglob('*')):
   if p.is_file():z.write(p,p.relative_to(root.parent))
 assert zpath.stat().st_size<30_000_000
 with zipfile.ZipFile(zpath) as z:assert z.testzip() is None
 print(zpath,zpath.stat().st_size)
