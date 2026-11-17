#!/usr/bin/env python3
"""Join known fixture/product image rules to exact original TIM crops.
Static extraction only. Does not execute source CPU or expand gameplay tests.
"""
import argparse,collections,hashlib,json,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 oldroot=ROOT.parent/'20261113-product-stock-data'
 prior=json.loads((oldroot/'product-fixture-data.json').read_text());plans=json.loads((oldroot/'android-stock-bridge.json').read_text())['plans']
 fixtures=prior['fixtures'];products=prior['products']
 assert sha(raw(0x80099f0c,53*196))==sha((oldroot/'source/fixture-master.bin').read_bytes())
 assert sha(raw(0x8009cdf0,27*88))==sha((oldroot/'source/product-master.bin').read_bytes())
 table=[list(struct.unpack('<4i',raw(0x8009c7a0+i*16,16))) for i in range(101)]
 runtime=[[v+60 for v in row] for row in table]
 thresholds=list(struct.unpack('<3i',raw(0x80010a98,12)));draw_kinds=list(struct.unpack('<3i',raw(0x80010aa4,12)))
 assert thresholds==[256,512,768] and draw_kinds==[9,11,13]
 binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows']
 sheets=[];source_files=[]
 for j in range(3):
  name=f'SYOP_S0{j}.TIM';blob=z.read('algorithm-analysis/source/'+name);b=binding[j+3];assert sha(blob)==b['source_sha256']
  magic,flags=struct.unpack_from('<II',blob);assert (magic,flags)==(16,9)
  clen,cx,cy,cw,ch=struct.unpack_from('<I4H',blob,8);assert(cw,ch)==(256,1)
  palette=blob[20:8+clen];words=struct.unpack('<256H',palette);p=8+clen;plen,px,py,pw,ph=struct.unpack_from('<I4H',blob,p);pix=blob[p+12:p+plen]
  assert p+plen==len(blob) and len(pix)==pw*ph*2 and pw*2==256
  assert [pw,ph]==b['destination_pixel_rect_words'][2:]
  rgba=[tuple(((w>>s)&31)*255//31 for s in (0,5,10))+(0 if w==0 else 255,) for w in words]
  im=Image.new('RGBA',(pw*2,ph));im.putdata([rgba[v] for v in pix])
  sheets.append(dict(image_id=j+3,name=name,width=pw*2,height=ph,pixels=pix,palette=palette,words=words,image=im))
  source_files.append(dict(image_id=j+3,archive_path='algorithm-analysis/source/'+name,sha256=sha(blob),dimensions=[pw*2,ph],pixel_sha256=sha(pix),palette_sha256=sha(palette),destination_pixel_rect_words=b['destination_pixel_rect_words'],destination_clut_rect_words=b['destination_clut_rect_words']))
 fixture_views=[];fixture_codes=set();tile_ids=set()
 for f in fixtures:
  w,h=f['size'];assert list(struct.unpack('<49i',raw(0x80099f0c+f['id']*196,196)))==f['raw_words']
  for direction in range(4):
   ww,hh=(w,h) if direction<2 else(h,w);cells=[]
   for y in range(h):
    for x in range(w):
     tid=f['raw_words'][11+y*3+x];code=runtime[tid][direction];dx,dy=(x,y) if direction<2 else(y,x)
     tile_ids.add(tid);fixture_codes.add(code);cells.append(dict(logical_tile=tid,pixel_offset=[dx*16,dy*16],image_code=code))
   fixture_views.append(dict(fixture=f['id'],name=f['name'],direction=direction,size_pixels=[ww*16,hh*16],cells=cells))
 normal_bases=collections.defaultdict(set)
 for plan in plans:
  for v in plan['variants']:normal_bases[plan['product']].update(v['runtime_image_bases'])
 product_usage=[];normal_codes=set();all_declared_codes=set()
 for p in products:
  base=list(struct.unpack_from('<12i',raw(0x8009cdf0+p['id']*88,88),36));assert base==p['disc_image_ids'];converted=[v*3+360 if v>=0 else v for v in base];assert converted==p['runtime_image_bases']
  declared={v for v in converted if v>=0};normal=normal_bases[p['id']];assert normal<=declared
  normal_codes.update(v+phase for v in normal for phase in range(3));all_declared_codes.update(v+phase for v in declared for phase in range(3))
  product_usage.append(dict(product=p['id'],name=p['name'],declared_image_bases=converted,normal_plan_bases=sorted(normal),normal_plan_codes=sorted(v+phase for v in normal for phase in range(3)),declared_not_in_normal_plans=sorted(declared-normal),meaning='Normal means bases referenced by existing688 refill plans, not observed play frequency. Image phases are0/1/2; quantity0 suppresses drawing.'))
 allcodes=fixture_codes|all_declared_codes;crops=[];pictures={}
 for code in sorted(allcodes):
  page=next(i for i,t in enumerate(thresholds) if code<=t);sheet=sheets[page];x=(code&15)*16;y=code&240
  assert 0<=x<=sheet['width']-16 and 0<=y<=sheet['height']-16
  pix=b''.join(sheet['pixels'][(y+dy)*sheet['width']+x:(y+dy)*sheet['width']+x+16] for dy in range(16));colors=b''.join(struct.pack('<H',sheet['words'][n]) for n in pix)
  crops.append(dict(image_code=code,draw_kind=draw_kinds[page],source_image_id=sheet['image_id'],source_file=sheet['name'],source_rect=[x,y,16,16],indices_sha256=sha(pix),raw_color_words_sha256=sha(colors),palette_sha256=sha(sheet['palette']),source_complete=True,fixture_reference=code in fixture_codes,normal_product_plan_reference=code in normal_codes,declared_product_reference=code in all_declared_codes))
  pictures[code]=sheet['image'].crop((x,y,x+16,y+16))
 js('image-source-crops.json',dict(rows=crops,sheets=source_files,thresholds_inclusive=thresholds,draw_kinds=draw_kinds,uv_rule='x=(code&15)*16;y=code&240',quantity0='Product draw branch suppresses records at quantity0, even if a retained code exists.',scope='Fixture descriptors and declared product table entries only. Not all possible interior/UI codes, scenes or actor sprites.'))
 js('fixture-direction-crops.json',dict(rows=fixture_views,source_table_address='0x8009C7A0',runtime_conversion='eachof101x4sourcevalues+60 once',used_logical_tile_ids=sorted(tile_ids),directions='Original0..3; directions2/3 transpose placement axes and select prerendered art; do not rotate pixels generically.'))
 js('product-source-usage.json',dict(rows=product_usage,existing_refill_plans='../20261113-product-stock-data/android-stock-bridge.json',plans_reused=len(plans),existing_distinct_month_variants=sum(len(p['variants']) for p in plans),render_references='Join persisted per-cell imagecode to image-source-crops; do not choose a new month art on every draw.'))
 # Compose catalog directly from source frames, not GPU compositing.
 fontpath=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');font=ImageFont.truetype(str(fontpath),14) if fontpath.exists() else ImageFont.load_default()
 atlas=Image.new('RGB',(1320,18*128),(38,40,44));draw=ImageDraw.Draw(atlas)
 for f in fixtures:
  ox=f['id']%3*440;oy=f['id']//3*128
  draw.text((ox+4,oy+2),f"{f['id']:02d} {f['name']}",font=font,fill='white')
  for direction in range(4):
   view=fixture_views[f['id']*4+direction];sample=Image.new('RGBA',tuple(view['size_pixels']))
   for c in view['cells']:sample.paste(pictures[c['image_code']],tuple(c['pixel_offset']))
   sample=sample.resize((sample.width*2,sample.height*2),Image.Resampling.NEAREST)
   x=ox+4+direction*108;y=oy+30;draw.text((x,y-13),str(direction),fill='#d6d6d6');atlas.paste(sample,(x,y),sample)
 atlas.save(ROOT/'fixture-four-direction-preview.png')
 boundary=[];preview=Image.new('RGB',(6*112,110),(38,40,44));bd=ImageDraw.Draw(preview)
 for i,code in enumerate(range(510,516)):
  row=next(c for c in crops if c['image_code']==code);boundary.append(row);sample=pictures[code].resize((64,64),Image.Resampling.NEAREST);preview.paste(sample,(i*112+4,40),sample);bd.text((i*112+4,4),f"code {code}",fill='white');bd.text((i*112+4,20),row['source_file'][:8],fill='white')
 preview.save(ROOT/'frozen-page-boundary-preview.png')
 js('page-boundary-source.json',dict(known_before='Inclusive256/512/768 rule already decoded and tested in r2. This result joins it to exact original source pixels and actual normal product17 references.',product=17,name=products[17]['name'],normal_bases=sorted(normal_bases[17]),frames=boundary,code512='SYOP_S01.TIM at0,0 with drawkind11, not SYOP_S02. Code513 uses SYOP_S02 at16,0. Preserve source mapping; this is not a new renderer correction.',natural_play_observation=False))
 spans=[('fixture_tile_table',0x8009c7a0,0x8009c7a0+101*16),('draw_thresholds_and_kinds',0x80010a98,0x80010ab0),('tile_record_reader',0x8005670c,0x80056a3c),('preview_source_reader',0x800799ac,0x80079d68)]
 evidence=[];asm=[];cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
 for name,a,e in spans:
  b=raw(a,e-a);fn='source/'+name+'.bin';(ROOT/fn).write_bytes(b);evidence.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(b)))
  if 'reader' in name:
   asm.append('# '+name);asm.extend(f'{i.address:08x}: {i.bytes.hex():8s} {i.mnemonic} {i.op_str}' for i in cs.disasm(b,a))
 (ROOT/'interior-image-readers.asm').write_text('\n'.join(asm)+'\n')
 js('source-provenance.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],source_images=source_files,raw_exe_ranges=evidence,reused_assets=[dict(path=str((oldroot/name).relative_to(ROOT.parent.parent)),sha256=sha((oldroot/name).read_bytes())) for name in ['product-fixture-data.json','android-stock-bridge.json']],known_before=['53fixtures,27products,172allowed pairs and688refillplans/2016month variants','Original101x4image conversion and799AC fixture orientation placement','Inclusive source image thresholds andUVrule','Product17 image bases and quantity phases'],new_result='Join exact source crop/hash andvalidpixelextent to212fixtureviews and normal/declared product references,including explicitcode512 mapping.',verification='Single static extraction: source hashes, previous master overlap, required code/crop bounds. No source CPUcalls or gameplay updates.'))
 js('summary.json',dict(fixtures=53,fixture_direction_views=len(fixture_views),logical_tile_ids_referenced=len(tile_ids),unique_fixture_codes=len(fixture_codes),normal_product_bases=len({v for vs in normal_bases.values() for v in vs}),normal_product_codes=len(normal_codes),declared_product_codes=len(all_declared_codes),declared_only_codes=sorted(all_declared_codes-normal_codes),all_bound_source_codes=len(crops),normal_fixture_and_product_codes=len(fixture_codes|normal_codes),source_images=3,missing_crops=0,original_cpu_calls=0,gameplay_updates=0,known_refill_plans_reused=len(plans),existing_variants_reused=sum(len(p['variants']) for p in plans),android_code_changed=False))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
