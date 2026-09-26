from pathlib import Path
import json,base64,html,zipfile
from PIL import Image,ImageDraw
BASE=Path(__file__).resolve().parents[1];out=BASE.parent/'output';out.mkdir(exist_ok=True)
def embedded(p):return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode()
def image(p,cls=''):return f'<img class="{cls}" src="{embedded(p)}" alt="{html.escape(p.stem)}" loading="lazy">'
tim=json.load(open(BASE/'tim-index.json'));inv=json.load(open(BASE/'inventory.json'))
css='''*{box-sizing:border-box}body{margin:0;color:#e7e8e8;background:#151e26;font:16px/1.7 system-ui,sans-serif}header,main{max-width:1280px;margin:auto;padding:24px}h1{font-size:30px;margin:0}p{max-width:1000px}.muted{color:#adb9c2}nav{display:flex;gap:8px;flex-wrap:wrap;margin:22px 0}button,input{font:inherit;padding:10px 16px;border:1px solid #617887;color:inherit;background:#243644;border-radius:6px}button{cursor:pointer}button[aria-selected=true]{background:#126d65}.panel{display:none}.panel.active{display:block}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}figure{margin:0;padding:16px;background:#24323d;border:1px solid #425360;border-radius:8px;overflow:auto}img{image-rendering:pixelated;max-width:100%}figure img{background:#aab7bf;min-width:256px;width:100%;object-fit:contain}figcaption{font-size:14px;color:#d1d9df}h2{font-size:23px}.map img{min-width:480px}.msg{display:flex;gap:16px;align-items:center;border-bottom:1px solid #415463;padding:9px 0;overflow:auto}.msg img{max-width:none;background:#e8e3cf;padding:6px}.msg code{min-width:130px}.msg small{min-width:90px}table{border-collapse:collapse;width:100%;font-size:14px}td,th{border-bottom:1px solid #425360;padding:8px;text-align:left}a{color:#70d8c8}pre{overflow:auto;background:#243644;padding:16px}.notice{border-left:4px solid #65bfad;padding:10px 18px;background:#243644}'''
body='''<header><p class="muted">SLPS_00782 ・ 読み取り専用の静的解析</p><h1>初代 ザ・コンビニ — PS版の内部資料</h1><p>77ファイルを識別し、原作画像34枚、街4マップ、メッセージ502件とスタッフロール102件を復号した。</p><p class="notice">ここに表示する画像は提供ディスクから復号したもの。街は基礎タイルの再構成で、ゲーム画面のキャプチャではない。経営計算・アニメーション速度・原作UI全体は未解読。</p><nav>'''
for key,label in [('overview','解析結果'),('maps','街4マップ'),('images','画像34枚'),('messages','メッセージ604件'),('files','ファイル77個')]:body+=f'<button data-tab="{key}" aria-selected="{str(key=="overview").lower()}">{label}</button>'
body+='</nav></header><main><section id="overview" class="panel active"><h2>再現に使える、確かな手掛かり</h2><ul><li>街は横60×縦50。8バイトの配置レコードが3,000件並び、MIPSコードの行列ループとも一致。</li><li>棚・商品・床・壁・人物・街タイル・顔・フォントをPNGへ復号。原作の見た目を直接参照できる。</li><li>独自の16bit文字番号を12×16ピクセルの原作フォントに対応させ、メッセージを可視化。</li><li>音楽SEQ 7本、音色バンク9組。音色のサイズ表は全組で実データ長と一致。</li></ul><h2>街配列を裏付ける命令</h2><pre>'+html.escape((BASE/'map-grid-disassembly.txt').read_text())+'</pre><h2>未解読・未検証</h2><p>売上・需要・客の選択・経路探索・スタッフ成長・イベント確率は未解読。音声再生と原作起動は未検証。画像のPS1半透明ブレンドは閲覧用PNGに完全再現していない。今回の資料はAPKへまだ組み込んでいない。</p><p>詳細な根拠、ファイル位置、再実行方法は同梱の REPORT.md を参照。形式確認：<a href="https://psx-spx.consoledev.net/cdromfileformats/">PSX-SPX CDROM File Formats</a>。ゲーム固有の情報は提供BINの実測による。</p></section><section id="maps" class="panel"><h2>60×50区画の配置</h2><p>道路・地形・建物の基礎タイルを再構成。ゲーム実行時の重ね描きやUIを含まない。</p><div class="grid">'
for p in sorted((BASE/'maps').glob('*width60.png')):body+=f'<figure class="map">{image(p)}<figcaption>{p.stem} / 480×400 px</figcaption></figure>'
body+='</div></section><section id="images" class="panel"><h2>原作の画像部品</h2><p>拡大時はドットを保持する。半透明色の合成は簡略化している。</p><div class="grid">'
for r in tim:body+=f'<figure>{image(BASE/"images"/r["png"])}<figcaption>{r["source"]}<br>{r["width"]}×{r["height"]} / {r["bpp"]}bit</figcaption></figure>'
body+='</div></section><section id="messages" class="panel"><h2>原作フォントで読むメッセージ</h2><p>改行・数値差し込みなどの制御コードは省略。文言の確認用であり、原画面と同じ組版ではない。IDで絞り込める（例 MSG00-032）。</p><input id="filter" placeholder="MSG00-032 / STAFF / 400">'
for name in ['MSG00','STAFF']:
 for r in json.load(open(BASE/f'{name}-messages.json')):
  key=f'{name}-{r["id"]:03}';body+=f'<div class="msg" data-key="{key}"><code>{key}</code><small>{r["offset"]}</small>{image(BASE/"messages"/(key+".png"))}</div>'
body+='</section><section id="files" class="panel"><h2>ISO内ファイル一覧</h2><p>全ファイルのSHA-256・抽出方式は inventory.json / CSV に収録。Form2を含むストリームは2352バイトの生セクタで保持する。</p><div style="overflow:auto"><table><tr><th>パス</th><th>LBA</th><th>ISOサイズ</th><th>抽出</th></tr>'
for r in inv:body+=f'<tr><td>{r["path"]}</td><td>{r["lba"]}</td><td>{r["size"]:,}</td><td>{"raw2352" if "raw2352" in r["extraction"] else "2048"}</td></tr>'
body+='</table></div></section></main>'
js="""document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('.panel').forEach(p=>p.classList.toggle('active',p.id===b.dataset.tab));document.querySelectorAll('[data-tab]').forEach(x=>x.setAttribute('aria-selected',String(x===b)));}));document.querySelector('#filter').addEventListener('input',e=>{const q=e.target.value.toUpperCase();document.querySelectorAll('.msg').forEach(x=>x.hidden=!x.dataset.key.includes(q));});"""
# Explicit [hidden] wins over the flex display rule.
css+='[hidden]{display:none!important}'
page='<!doctype html><html lang="ja"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>PS版ザ・コンビニ ディスク解析</title><style>'+css+'</style>'+body+'<script>'+js+'</script></html>'
(BASE/'index.html').write_text(page);(out/'Conveni-PS1-Analysis.html').write_text(page);(out/'Conveni-PS1-Report.md').write_text((BASE/'REPORT.md').read_text())
# Preview is a labeled contact sheet of decoded source images, not a mock gameplay screenshot.
im=Image.new('RGB',(1060,540),'#202f3a');d=ImageDraw.Draw(im);d.text((20,15),'PS1 DISC / RESTORED TOWN + ORIGINAL SPRITE SHEETS',fill='white')
for src,xy in [('maps/TOWN0001-width60.png',(20,70)),('images/TIM0_SYOP_S00.png',(530,70)),('images/TIM0_MAN0.png',(790,70)),('images/TIM0_SHOPTYP1.png',(530,385))]:
 p=Image.open(BASE/src);im.paste(p,xy,p if p.mode=='RGBA' else None);d.text((xy[0],xy[1]-20),Path(src).stem,fill='white')
d.text((20,500),'60 x 50 tiles | 34 TIM images | 502 messages + 102 credits',fill='white');im.save(out/'Conveni-PS1-Preview.png')
with zipfile.ZipFile(out/'Conveni-PS1-Analysis.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(BASE.rglob('*')):
  if not p.is_file():continue
  rel=p.relative_to(BASE)
  if p.name=='format-reference.md' or p.name.startswith('msg-') or p.name=='message-preview.png':continue
  if rel.parts[0]=='files' and (p.name=='3MIN.BIN' or p.suffix=='.raw2352'):continue
  if '__pycache__' in rel.parts:continue
  z.write(p,'Conveni-PS1-Analysis/'+str(rel))
print('Viewer:',len(tim),'images; 604 message images; 4 maps; inventory',len(inv));print('ZIP bytes',(out/'Conveni-PS1-Analysis.zip').stat().st_size)
(BASE/'viewer-script.js').write_text(js)
