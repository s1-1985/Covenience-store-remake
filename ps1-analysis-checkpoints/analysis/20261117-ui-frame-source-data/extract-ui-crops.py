#!/usr/bin/env python3
"""Static join of original window/cursor/style/icon UVs to actual TIM payloads.
Known UI producer rules are reused, not re-tested on the source CPU.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent;EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,o):(ROOT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'];images={};sources=[]
 for image_id in [6,8]:
  row=binding[image_id];blob=z.read('algorithm-analysis/source/'+Path(row['path']).name);assert sha(blob)==row['source_sha256'] and struct.unpack_from('<II',blob)==(16,9)
  n,px,py,pw,ph=struct.unpack_from('<I4H',blob,8);assert(pw,ph)==(256,1);pal=blob[20:8+n];words=struct.unpack('<256H',pal);p=8+n;plen,px,py,pw,ph=struct.unpack_from('<I4H',blob,p);pix=blob[p+12:p+plen];assert p+plen==len(blob) and len(pix)==pw*ph*2
  rgba=[tuple(((w>>s)&31)*255//31 for s in (0,5,10))+(0 if w==0 else 255,) for w in words];im=Image.new('RGBA',(pw*2,ph));im.putdata([rgba[v] for v in pix]);images[image_id]=dict(image=im,width=pw*2,height=ph,pixels=pix,palette=pal,words=words)
  sources.append(dict(image_id=image_id,path=row['path'],source_sha256=sha(blob),source_size_pixels=[pw*2,ph],source_pixel_sha256=sha(pix),palette_sha256=sha(pal),destination_pixel_rect_words=row['destination_pixel_rect_words'],destination_clut_rect_words=row['destination_clut_rect_words']))
 crops=[];pictures={}
 def add(key,category,image_id,kind,uv,w,h,metadata):
  # Original8-bit pages: kind low5bits selects64word X and256line Y.
  u,v=uv;vx=(kind&15)*64*2+u;vy=((kind>>4)&1)*256+v;dest=binding[image_id]['destination_pixel_rect_words'];sx=vx-dest[0]*2;sy=vy-dest[1];sheet=images[image_id]
  assert 0<=sx<=sheet['width']-w and 0<=sy<=sheet['height']-h
  idx=b''.join(sheet['pixels'][(sy+y)*sheet['width']+sx:(sy+y)*sheet['width']+sx+w] for y in range(h));colors=b''.join(struct.pack('<H',sheet['words'][n]) for n in idx)
  r=dict(key=key,category=category,source_image_id=image_id,source_file=Path(binding[image_id]['path']).name,draw_record_kind=kind,uv=[u,v],source_rect=[sx,sy,w,h],clut_xy=binding[image_id]['destination_clut_rect_words'][:2],indices_sha256=sha(idx),raw_color_words_sha256=sha(colors),palette_sha256=sha(sheet['palette']),inside_original_pixels=True,fully_transparent=all(sheet['words'][n]==0 for n in idx),metadata=metadata);crops.append(r);pictures[key]=sheet['image'].crop((sx,sy,sx+w,sy+h));return r
 window=[]
 for y,start in enumerate([0x60,0x90,0xc0]):
  for x in range(3):
   key=f'window_{y}_{x}';window.append(add(key,'window',8,7,[start+x*16,32],16,16,dict(position=[x,y],source_reader='80017C3C/80017FD4'))['key'])
 styleuv=raw(0x80010078,16);assert styleuv.hex()=='703080309030b010c010d030c030e030'
 for i in range(8):add(f'rectangle_mode_{i}','rectangle_style',8,7,list(styleuv[2*i:2*i+2]),16,16,dict(mode=i,source_table='0x80010078',source_reader='0x800185A4',width_note='Full16x16sample. Original rectangle may clip/narrow width; doesnot scale thetexture to arbitrarywidth.'))
 add('cursor','selection_cursor',8,7,[96,16],16,16,dict(source_reader='0x8004E938',known_other_users='Existing cursor_control/settings_visuals/confirmation_dialog use sameUV.'))
 for i in range(8):add(f'icon32_{i}','icon32',6,13,[i*32,128],32,32,dict(source_reader='0x80067494',slot=i,index_rule='signed16input low3bits;code&7',caller='0x8004014C',rect_selector='0x80040020 selectsimage6;400F4uploads;4014Cdraws'))
 js('ui-source-crops.json',dict(rows=crops,sources=sources,scope='Nine windowparts,eightrectangle styles,onecursor,eighticon32slots only. Not all UI symbols or control labels.',raw_palette_policy='RawBGR555/STP maintained via sources/hash; PNG reference is not fullGPU compositing.'))
 # Known ninepart tiling, one reference composition, not an additional gameplay test.
 cols,rows=8,5;sample=Image.new('RGBA',(cols*16,rows*16));cells=[]
 for y in range(rows):
  for x in range(cols):
   ry=0 if y==0 else 2 if y==rows-1 else 1;rx=0 if x==0 else 2 if x==cols-1 else 1;key=f'window_{ry}_{rx}';sample.paste(pictures[key],(x*16,y*16));cells.append([x*16,y*16,key])
 sample.save(ROOT/'window-eight-by-five-preview.png')
 js('window-source-composition.json',dict(cell_pixels=[16,16],minimum_size_cells=[2,2],rule='Top/middle/bottom row andleft/middle/right column select oneofnineparts; tile16pixelcells. Sourcewidth/height are cellcounts,notpixels.',known_rule_source='r2 algorithm-analysis/window_tiles.py',example=dict(size_cells=[cols,rows],size_pixels=[cols*16,rows*16],cells=cells,scope='Reference composition only; not originalUI execution or screen claim.'),pixel_origin='Originalscreenx/y convertedbyx-160,y-112; sourcecropping independent ofscreenorigin.',rectangle_styles='Separate185A4 style table, not the9partwindow index space.'))
 atlas=Image.new('RGB',(7*148,4*128),(38,40,44));d=ImageDraw.Draw(atlas)
 for i,c in enumerate(crops):
  x=i%7*148+5;y=i//7*128+24;d.text((x,y-19),c['key'],fill='white');p=pictures[c['key']];scale=2 if p.width==32 else 3;p=p.resize((p.width*scale,p.height*scale),Image.Resampling.NEAREST);atlas.paste(p,(x,y),p);d.text((x,y+70),f"src {c['source_image_id']} {c['source_rect'][:2]}",fill='#bbbbbb')
 atlas.save(ROOT/'ui-crops-preview.png')
 js('source-height-boundaries.json',dict(shoptyp1=dict(source_image_id=6,source_size_pixels=[images[6]['width'],images[6]['height']],requested_height=binding[6]['height_pixels'],normal_icon_uv_y=128,source_rectangles=[[i*32,0,32,32] for i in range(8)],required_source_rows=[0,31],nonexistent_requested_rows_not_required=[32,63]),kyou=dict(source_image_id=8,source_size_pixels=[images[8]['width'],images[8]['height']],requested_height=binding[8]['height_pixels'],max_required_exclusive_y=max(c['source_rect'][1]+c['source_rect'][3] for c in crops if c['source_image_id']==8)),important='Drawkind13 andUVy128 resolve intoSHOPTYP1 atVRAMwordX832,line128; do not labelallkind13frames SYOP_S02. BindingrequirespositionandCLUT aswellaskind.',scope='These26crops only; not proof allUIUV references fit sourceheight.'))
 spans=[('window_reader',0x80017b18,0x800182d0),('rectangle_style_reader',0x800185a4,0x80018940),('rectangle_uv_table',0x80010078,0x80010088),('cursor_reader',0x8004e938,0x8004eaa0),('icon32_reader',0x80067494,0x800675dc),('notification_icon_binding',0x8004000c,0x80040154)]
 evidence=[];asm=[];cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
 for n,a,e in spans:
  b=raw(a,e-a);fn='source/'+n+'.bin';(ROOT/fn).write_bytes(b);evidence.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(b)))
  if n!='rectangle_uv_table':asm.append('# '+n);asm.extend(f'{i.address:08x}: {i.bytes.hex():8s} {i.mnemonic} {i.op_str}' for i in cs.disasm(b,a))
 (ROOT/'ui-image-readers.asm').write_text('\n'.join(asm)+'\n')
 reused=['algorithm-analysis/window_tiles.py','algorithm-analysis/settings_rectangles.py','algorithm-analysis/icon_layout.py','algorithm-analysis/confirmation_dialog.py']
 js('source-provenance.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],images=sources,raw_exe_ranges=evidence,known_rule_sources=[dict(path=n,sha256=sha(z.read(n))) for n in reused],known_before='Ninepartwindow/rectanglestyleUV/cursor/icon32 formulas and originalCPUchecks existed inr2; TIMtransferheight differences also known.',new_result='Bind26required UI crops to actualTIMpayloads and record source/frame-coordinate distinction; all8SHOPTYP1icon slots needonly32existentrows,not64requestedrows.',verification='One static extraction with hash checks,originalUVtable comparison andcropbounds; no originalCPUcalls orgameupdates.'))
 js('summary.json',dict(window_parts=9,rectangle_styles=8,selection_cursor=1,icon32_slots=8,total_source_crops=len(crops),source_images=2,missing_source_crops=0,icon32_nontransparent_slots=sum(c['category']=='icon32' and not c['fully_transparent'] for c in crops),icon32_transparent_slots=[c['metadata']['slot'] for c in crops if c['category']=='icon32' and c['fully_transparent']],shoptyp1_icon_rows_required=32,shoptyp1_requested_height=binding[6]['height_pixels'],original_cpu_calls=0,gameplay_updates=0,android_code_changed=False))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
