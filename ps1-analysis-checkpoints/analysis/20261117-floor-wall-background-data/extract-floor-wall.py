#!/usr/bin/env python3
"""Static source join: floor/wall layout cells and KABEE CEL/BGD background.
Reuses decoded render rules; never executes PS CPU or simulates gameplay.
"""
import argparse,collections,hashlib,json,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent;EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 def string(a):return raw(a,80).split(b'\0')[0].decode('ascii')
 bindings=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'];images={};source=[]
 for image_id in [3,4,5,8]:
  row=bindings[image_id];blob=z.read('algorithm-analysis/source/'+Path(row['path']).name);assert sha(blob)==row['source_sha256'];assert struct.unpack_from('<II',blob)==(16,9)
  clen,cx,cy,cw,ch=struct.unpack_from('<I4H',blob,8);assert(cw,ch)==(256,1);palette=blob[20:8+clen];pwds=struct.unpack('<256H',palette);p=8+clen;plen,px,py,pw,ph=struct.unpack_from('<I4H',blob,p);pix=blob[p+12:p+plen];assert p+plen==len(blob) and len(pix)==pw*ph*2
  colors=[tuple(((v>>s)&31)*255//31 for s in (0,5,10))+(0 if v==0 else 255,) for v in pwds];im=Image.new('RGBA',(pw*2,ph));im.putdata([colors[n] for n in pix]);images[image_id]=dict(image=im,indices=pix,width=pw*2,height=ph,palette=palette,words=pwds,binding=row)
  source.append(dict(id=image_id,path=row['path'],sha256=sha(blob),source_pixels=[pw*2,ph],palette_sha256=sha(palette),destination_pixel_rect_words=row['destination_pixel_rect_words'],destination_clut_rect_words=row['destination_clut_rect_words']))
 def crop(image_id,x,y,w=16,h=16):
  a=images[image_id];assert 0<=x<=a['width']-w and 0<=y<=a['height']-h
  idx=b''.join(a['indices'][(y+j)*a['width']+x:(y+j)*a['width']+x+w] for j in range(h));colors=b''.join(struct.pack('<H',a['words'][n]) for n in idx)
  return dict(source_image_id=image_id,source_rect=[x,y,w,h],indices_sha256=sha(idx),raw_color_words_sha256=sha(colors),palette_sha256=sha(a['palette']),inside_original_pixels=True)
 # Floors0..35 were previously decoded; now attach every layout wall anchor to those pixels.
 floorcrops=[dict(code=i,**crop(3,(i&15)*16,(i>>4)*16)) for i in range(36)]
 floorinfo=json.loads((ROOT.parent/'20261113-floor-cleaning-data/layout-floor-counts.json').read_text())
 fixture_crops=json.loads((ROOT.parent/'20261117-interior-source-crops-data/image-source-crops.json').read_text())['rows'];fby={c['image_code']:c for c in fixture_crops}
 layouts=[];floorhist=collections.Counter();wallhist=collections.Counter();nfixtures=0;contact=Image.new('RGB',(5*244,6*248),(38,40,44));draw=ImageDraw.Draw(contact)
 for k in range(30):
  b=raw(0x800a2074+k*3108,3108);w,h=struct.unpack_from('<2i',b);assert w%2==h%2==0 and 0<w<=28 and 0<h<=26
  floor=[[b[12+y*14+x] for x in range(w//2)] for y in range(h//2)];hist=collections.Counter(v for line in floor for v in line);floorhist.update(hist)
  sample=Image.new('RGBA',(w*8,h*8));wall=[];fixtures=[];anchors=collections.Counter()
  for y,line in enumerate(floor):
   for x,c in enumerate(line):
    if c<36:sample.paste(images[3]['image'].crop(((c&15)*16,(c>>4)*16,(c&15)*16+16,(c>>4)*16+16)),(x*16,y*16))
  for y in range(h):
   for x in range(w):
    word=struct.unpack_from('<I',b,196+y*112+x*4)[0];code=word&1023;kind=(word>>12)&1023
    if word&0x80000000:
     anchors[kind]+=1
     if kind==53:
      fc=floor[y//2][x//2];assert 20<=code<=27 and fc==code and x%2==y%2==0
      wall.append([x,y,code]);wallhist[code]+=1
    if not code or word&3072 or not 60<=code<360:continue
    row=fby[code];assert row['fixture_reference'];x0,y0,ww,hh=row['source_rect'];observed=crop(row['source_image_id'],x0,y0);assert observed['indices_sha256']==row['indices_sha256'];assert x*8+16<=w*8 and y*8+16<=h*8
    art=images[row['source_image_id']]['image'].crop((x0,y0,x0+16,y0+16));sample.alpha_composite(art,(x*8,y*8));fixtures.append([x,y,code])
  nfixtures+=len(fixtures);ox=k%5*244+8;oy=k//5*248+24;draw.text((ox,oy-17),f'layout{k:02d} {w}x{h} / wall {len(wall)}',fill='white');contact.paste(sample,(ox,oy),sample)
  layouts.append(dict(layout=k,address=hex(0x800a2074+k*3108),source_sha256=sha(b),size_half_cells=[w,h],source_canvas_pixels=[w*8,h*8],floor_grid=floor,floor_histogram=dict(sorted(hist.items())),wall_anchor_columns=['half_x','half_y','floor_and_low_image_code'],wall_anchors=wall,wall_count=len(wall),anchor_kind_histogram=dict(sorted(anchors.items())),fixture_draw_columns=['half_x','half_y','image_code'],fixture_draw_cells=fixtures))
 contact.save(ROOT/'thirty-layout-source-preview.png')
 js('layout-floor-wall-map.json',dict(rows=layouts,floor_source_image_id=3,floor_draw_limit_exclusive=36,wall_kind=53,wall_result='All1060kind53anchors have lowimagecode20..27 equal to floorcode at(x//2,y//2); allanchorevenx/y. These codes are below60, so equipment-only drawpath omits them. Visible wall comes from floorplane.',fixture_draw_rule='Nonzero low10bits; skipword&0xC00; render60<=code<360 at x8/y8 with16x16 frame. Stock repaint and actors not generated.',preview_scope='Raw template floor plus fixture art; no originalCPU, no stocked products, characters, UI, lighting or GPU blend equivalence.'))
 js('floor-source-crops.json',dict(rows=floorcrops,known_before='36floor/edge sourcecells and0/5/10clean materials were already extracted. Added usage binding to all30layouts and explicit kind53wall/floor pairing.',histogram_30_layouts=dict(sorted(floorhist.items())),wall_image_histogram=dict(sorted(wallhist.items()))))
 # KABEE is a separate scene background. Use declared dimensions, not padded slots.
 cel=z.read('algorithm-analysis/source/KABEE.CEL');bgd=z.read('algorithm-analysis/source/KABEE.BGD');magic,count,cols,rows=struct.unpack_from('<IHBB',cel);assert(magic,count,cols,rows)==(0xc0000322,16,4,4);assert len(cel)==168 and cel[8+count*8:]==bytes(32)
 assert struct.unpack_from('<I',bgd)[0]==0xc0000023;bw,bh,tw,th=bgd[4:8];assert(bw,bh,tw,th)==(20,16,16,16);codes=list(struct.unpack_from('<320H',bgd,8));assert max(codes)<count and bgd[648:]==bytes(640)
 b=images[8]['binding'];dx,dy,dw,dh=b['destination_pixel_rect_words'];clx,cly,cw,ch=b['destination_clut_rect_words'];ct=[];arts=[]
 for i in range(count):
  u,v,clut,unused,tp=struct.unpack_from('<BBHHH',cel,8+i*8);assert unused==0 and (tp>>7)&3==1 and ((clut&63)*16,clut>>6)==(clx,cly)
  sx=(tp&15)*64*2+u-dx*2;sy=((tp>>4)&1)*256+v-dy;ct.append(dict(tile=i,uv=[u,v],clut_word=clut,tpage_word=tp,**crop(8,sx,sy)));arts.append(images[8]['image'].crop((sx,sy,sx+16,sy+16)))
 bg=Image.new('RGBA',(bw*tw,bh*th))
 for i,c in enumerate(codes):bg.paste(arts[c],(i%bw*tw,i//bw*th))
 bg.save(ROOT/'kabee-background-source-preview.png')
 celpointer=struct.unpack('<I',raw(0x800986c4+4,4))[0];bgdpointer=struct.unpack('<I',raw(0x800986cc,4))[0];assert string(celpointer)=='\\DAT\\KABEE.CEL;1' and string(bgdpointer)=='\\DAT\\KABEE.BGD;1'
 js('kabee-background-source-map.json',dict(cel=dict(sha256=sha(cel),declared_count=count,grid=[cols,rows],physical_slots=20,padded_zero_slots=4,source_name_pointer=hex(celpointer)),bgd=dict(sha256=sha(bgd),grid=[bw,bh],tile_pixels=[tw,th],declared_cells=len(codes),physical_cells=(len(bgd)-8)//2,padded_zero_cells=320,image_codes=codes,histogram=dict(sorted(collections.Counter(codes).items())),source_name_pointer=hex(bgdpointer),source_name_table='0x800986CC'),crop_rows=ct,source_image='KYOU.TIM',original_source_image_pixels=[images[8]['width'],images[8]['height']],source_crop_union=[0,72,64,64],composed_pixels=[320,256],background_type1_viewport=[320,240],static_call_links=['80012730:A0=1,A1=6;12738load=>KABEE.CEL at801FD000','80012740:A0=0,A1=5;12748load=>KABEE.BGD at801ED600','80057C58:A0=801ED604,A1=801FD008,A2=1;57C6C=>19460'],scope='Original file/path/static call binding and raw composition. Not a store wall material or a whole57BD4 scene execution.'))
 (ROOT/'source/KABEE.CEL').write_bytes(cel);(ROOT/'source/KABEE.BGD').write_bytes(bgd)
 spans=[('floor_reader',0x800561cc,0x8005643c),('resource_preload',0x80012730,0x80012780),('bgd_cel_loaders',0x800150dc,0x800152a4),('scene_background_link',0x80057bd4,0x80057c74),('resource_name_pointers',0x800986c4,0x800986d0)]
 ev=[];asm=[];cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
 for n,a,e in spans:
  bb=raw(a,e-a);fn='source/'+n+'.bin';(ROOT/fn).write_bytes(bb);ev.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(bb)))
  if n!='resource_name_pointers':asm.extend(f'{i.address:08x}: {i.bytes.hex():8s} {i.mnemonic} {i.op_str}' for i in cs.disasm(bb,a))
 (ROOT/'floor-background-readers.asm').write_text('\n'.join(asm)+'\n')
 js('source-provenance.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],source_images=source,raw_exe_ranges=ev,layout_table=dict(address='0x800A2074',stride=3108,count=30,sha256=sha(raw(0x800a2074,3108*30)),floor_offset=12,grid_offset=196),existing_floor_data_sha256=sha((ROOT.parent/'20261113-floor-cleaning-data/layout-floor-counts.json').read_bytes()),existing_fixture_crops_sha256=sha((ROOT.parent/'20261117-interior-source-crops-data/image-source-crops.json').read_bytes()),known_before='Floor36crops/30layoutfloorcounts, kind53wallidentity and basicrenderpaths existed. KABEE sourcefiles and CELparser also existed. New work joins all1060wallanchors to floorpixels,30template composites, and16KABEEcrops/320BGDcells toKYOU actualpixels/load paths.',verification='Single static extraction with source hashes, referenced crop consistency and bounds. No sourceCPUcall or extra gameplaytests.'))
 js('summary.json',dict(layouts=30,template_floor_cells=sum(floorhist.values()),wall_anchors=sum(wallhist.values()),wall_floor_pairs_matching=sum(wallhist.values()),wall_image_codes=sorted(wallhist),fixture_draw_cells=nfixtures,floor_crops_reused=36,kabee_source_crops=16,kabee_background_cells=320,kabee_cel_zero_padding_slots=4,kabee_bgd_zero_padding_cells=320,missing_source_crops=0,original_cpu_calls=0,gameplay_updates=0,android_code_changed=False))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
