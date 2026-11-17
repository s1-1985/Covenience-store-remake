#!/usr/bin/env python3
"""Static join: original CEL -> TIM crop -> building range / four packed towns.
No CPU execution, gameplay continuation, or natural screen claim.
"""
import argparse,collections,hashlib,json,struct,zipfile,zlib
from pathlib import Path
from PIL import Image,ImageDraw
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
SPECIAL={4:(True,0),5:(False,10),6:(True,32),7:(False,42),16:(True,64),17:(False,74),18:(True,96),19:(False,106)}
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 cel=z.read('disc-analysis/files/DAT/TOWN_PR1.CEL');tim=z.read('algorithm-analysis/source/TOWN_PR1.TIM')
 prior_cel=next(x for x in json.loads(z.read('algorithm-analysis/cel-source-tables.json')) if x['file']=='TOWN_PR1.CEL')
 assert sha(cel)==prior_cel['sha256']
 magic,count,cols,rows=struct.unpack_from('<IHBB',cel);assert (magic,count,cols,rows)==(0xc0000322,640,32,20)
 assert (len(cel)-8)//8==800 and cel[8+count*8:]==bytes(160*8)
 # Original TIM:8-bit indices; preserve raw BGR555/STP separately from preview colors.
 assert struct.unpack_from('<II',tim)==(16,9)
 clen,cx,cy,cw,ch=struct.unpack_from('<I4H',tim,8);assert (cw,ch)==(256,1)
 palette=tim[20:8+clen];pwords=struct.unpack('<256H',palette);p=8+clen
 plen,px,py,pw,ph=struct.unpack_from('<I4H',tim,p);indices=tim[p+12:p+plen];assert p+plen==len(tim) and len(indices)==pw*ph*2
 binding=next(x for x in json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'] if x['id']==0)
 assert sha(tim)==binding['source_sha256'];dx,dy,dw,dh=binding['destination_pixel_rect_words'];clx,cly,clw,clh=binding['destination_clut_rect_words'];assert (pw,ph)==(dw,dh)==(128,160)
 rgba=[tuple(((w>>s)&31)*255//31 for s in (0,5,10))+(0 if w==0 else 255,) for w in pwords]
 im=Image.new('RGBA',(pw*2,ph));im.putdata([rgba[v] for v in indices]);im.save(ROOT/'town-source-preview.png')
 cells=[];tiles=[]
 for i in range(count):
  u,v,c,unused,t=struct.unpack_from('<BBHHH',cel,8+i*8)
  assert unused==0 and (t>>7)&3==1 #8-bit page
  vx=(t&15)*64*2+u;vy=((t>>4)&1)*256+v
  sx=vx-dx*2;sy=vy-dy
  assert 0<=sx<=pw*2-8 and 0<=sy<=ph-8
  assert ((c&63)*16,c>>6)==(clx,cly)
  crop=b''.join(indices[(sy+y)*pw*2+sx:(sy+y)*pw*2+sx+8] for y in range(8))
  words=b''.join(struct.pack('<H',pwords[n]) for n in crop)
  tiles.append(im.crop((sx,sy,sx+8,sy+8)))
  cells.append([i,u,v,c,t,sx,sy,sha(crop),sha(words)])
 js('cel-to-source.json',dict(columns=['image_code','u','v','clut_word','tpage_word','source_x','source_y','index64_sha256','raw_color128_sha256'],rows=cells,source_image_id=0,source_image_path=binding['path'],source_tile_pixels=[8,8],declared_count=count,physical_slots=800,zero_padding_slots=160,all_declared_crops_inside_original_payload=True,palette_sha256=sha(palette),raw_word_policy='Raw15-bit BGR +STPbit retained via sourceTIM; PNG is reference preview, not GPU blend output.'))
 # Full contiguous82-row master, including9 store descriptors,4 earlier vacant types,
 #59 ordinary environmental definitions and10 extension labels. These counts are not82 distinct buildings.
 base=0x8009d738;buildings=[]
 for i in range(82):
  b=raw(base+i*56,56);name=b[:24].split(b'\0',1)[0].decode('shift_jis');w,h,lo,hi=struct.unpack_from('<4i',b,24)
  assert w*h==hi-lo+1 and 0<=lo<=hi<count
  crops=[dict(code=k,offset=[(k-lo)%w*8,(k-lo)//w*8],source_rect=[cells[k][5],cells[k][6],8,8]) for k in range(lo,hi+1)]
  buildings.append(dict(master_index=i,address=hex(base+i*56),name=name,footprint=[w,h],tile_range=[lo,hi],preview_pixels=[w*8,h*8],category=struct.unpack_from('<h',b,40)[0],source_image_id=0,crops=crops,extension_named_entry=name.startswith('拡張'),unused_named_entry=name=='(未使用)'))
 old=json.loads(z.read('algorithm-analysis/town-building-tables.json'))['buildings'];assert len(old)==72
 for b,o in zip(buildings,old):assert b['name']==o['name'] and b['tile_range']==[o['lower'],o['upper']] and raw(base+b['master_index']*56,56).hex()==o['raw_hex']
 later=json.loads((ROOT.parent/'20261113-customer-data/customer-data.json').read_text())['buildings'];assert len(later)==69
 for b,o in zip(buildings[13:],later):assert b['name']==o['name'] and b['tile_range']==o['tile_range']
 js('building-source-crops.json',dict(schema='Source master indices begin0x8009D738; customer-data69row indices begin13 rows later. Do not confuse these indices with tile codes or gameplay kinds.',rows=buildings))
 atlas=Image.new('RGB',(8*150,11*146),(30,32,36));ad=ImageDraw.Draw(atlas)
 for b in buildings:
  i=b['master_index'];x=(i%8)*150;y=(i//8)*146
  ad.text((x+4,y+3),f"#{i} tiles {b['tile_range'][0]}..{b['tile_range'][1]}",fill='white')
  sample=Image.new('RGBA',tuple(b['preview_pixels']))
  for c in b['crops']:sample.paste(tiles[c['code']],tuple(c['offset']))
  sample=sample.resize((sample.width*2,sample.height*2),Image.Resampling.NEAREST);atlas.paste(sample,(x+4,y+24),sample)
 atlas.save(ROOT/'building-crops-preview.png')
 lookup=list(struct.unpack('<10H',raw(0x8001009c,20)));assert lookup==list(range(524,534))
 js('store-sign-crops.json',dict(known_rule_source='r2 algorithm-analysis/town_tile_image.py; static source80019870',identifier='First containing active store: low7bits ofstore+4. Tens orunits select lookup; tens>=10 uses originaltile. No matching store retains stack half inoriginal code, not fabricated as0 here.',lookup=lookup,variants=[dict(source_tile=k,digit='tens' if tens else 'units',offset=off,image_codes=[v+off for v in lookup]) for k,(tens,off) in SPECIAL.items()],all_80_variant_crops_inside_source=True))
 worlds=[];resolved=bytearray();canvas=Image.new('RGB',(1000,860),(30,32,36));draw=ImageDraw.Draw(canvas)
 for wi,name in enumerate(['TOWN0001','TOWN0002','TOWN0003','TOWNPS']):
  b=z.read('algorithm-analysis/source/'+name+'.BIN');assert len(b)==76707
  stores=[]
  for j in range(10):
   rec=b[25907+j*5080:25907+(j+1)*5080]
   if rec[0]:stores.append(dict(slot=j,identifier=struct.unpack_from('<H',rec,4)[0]&127,rect=list(struct.unpack_from('<4i',rec,8))))
  codes=[];replacements=[];hist=collections.Counter()
  mapim=Image.new('RGBA',(480,400))
  for j in range(3000):
   tile=struct.unpack_from('<h',b,17+j*8)[0];x=j%60;y=j//60;code=tile
   if tile in SPECIAL:
    match=next((s for s in stores if s['rect'][0]<=x<=s['rect'][2] and s['rect'][1]<=y<=s['rect'][3]),None)
    assert match is not None,(name,x,y,tile,'unresolved retained stack input')
    tens,offset=SPECIAL[tile];digit=match['identifier']//10 if tens else match['identifier']%10
    code=lookup[digit]+offset if not tens or digit<10 else tile
    replacements.append(dict(x=x,y=y,tile=tile,image_code=code,store_slot=match['slot'],identifier=match['identifier']))
   assert 0<=code<count
   codes.append(code);hist[code]+=1;mapim.paste(tiles[code],(x*8,y*8))
  resolved.extend(struct.pack('<3000H',*codes));xx=(wi%2)*500+10;yy=(wi//2)*430+24;draw.text((xx,yy-19),name,fill='white');canvas.paste(mapim,(xx,yy),mapim)
  worlds.append(dict(name=name,source_sha256=sha(b),cells=3000,original_tile_range=[min(struct.unpack_from('<h',b,17+k*8)[0] for k in range(3000)),max(struct.unpack_from('<h',b,17+k*8)[0] for k in range(3000))],resolved_image_range=[min(codes),max(codes)],histogram=dict(sorted(hist.items())),stores=stores,store_sign_substitutions=replacements,unresolved_cells=0,invalid_source_crops=0,resolved_u16_sha256=sha(struct.pack('<3000H',*codes))))
 canvas.save(ROOT/'four-town-source-preview.png');compressed=zlib.compress(bytes(resolved),9);(ROOT/'resolved-town-images.u16.zlib').write_bytes(compressed)
 js('four-town-source-map.json',dict(order=[w['name'] for w in worlds],decoded_dtype='little-endian u16',cells_per_map=3000,grid=[60,50],decoded_bytes=len(resolved),decoded_sha256=sha(resolved),compressed_sha256=sha(compressed),rows=worlds))
 spans=[('building_master',base,base+82*56),('store_sign_lookup',0x8001009c,0x800100b0),('town_map_and_sign_reader',0x800196c8,0x80019ea0)]
 evidence=[];assembly=[];cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
 for n,a,e in spans:
  bb=raw(a,e-a);fn='source/'+n+'.bin';(ROOT/fn).write_bytes(bb);evidence.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(bb)))
  if n=='town_map_and_sign_reader':assembly.extend(f'{i.address:08x}: {i.bytes.hex():8s} {i.mnemonic} {i.op_str}' for i in cs.disasm(bb,a))
 (ROOT/'town-image-reader.asm').write_text('\n'.join(assembly)+'\n');(ROOT/'source/TOWN_PR1.CEL').write_bytes(cel)
 js('source-provenance.json',dict(archive_sha256=arch['sha256'],exe_sha256=EXE_SHA,cel_sha256=sha(cel),tim_sha256=sha(tim),raw_exe_ranges=evidence,inputs_in_existing_archive=['algorithm-analysis/source/SLPS_007.82','algorithm-analysis/source/TOWN_PR1.TIM','algorithm-analysis/source/TOWN0001.BIN','algorithm-analysis/source/TOWN0002.BIN','algorithm-analysis/source/TOWN0003.BIN','algorithm-analysis/source/TOWNPS.BIN'],known_before='CEL640 declared/800physical/160zero; existing72/69 building row exports; store digit mapping and full-map original renderer already decoded. New join is all640 crops,82-row source master and4maps to originalTIM pixel payload, including80 digit variants.',verification_scope='One static extraction, source hashes, table overlap cross-checks and crop/range bounds. No original CPU execution or additional game updates.'))
 js('summary.json',dict(cel_source_crops=640,padded_slots_not_exported=160,building_master_rows=82,building_master_note='Includes9store descriptors,4vacant definitions,59environment definitions and10extension labels; not82distinct buildings.',store_sign_variant_crops=80,initial_maps=4,initial_map_cells=12000,initial_sign_replacements=sum(len(w['store_sign_substitutions']) for w in worlds),all_crops_inside_source=True,unresolved_initial_map_cells=0,original_cpu_calls=0,gameplay_updates=0,scope='Source-data visual reconstruction only; no screen-layer/fog/lighting/UI/semitransparency/GPU equivalence claim.'))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
