#!/usr/bin/env python3
"""Static source portraits: original UI rule -> TIM crops -> four town rosters.
No original CPU execution or gameplay tests. Existing decoded UI rule is reused.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent;EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,o):(ROOT/n).write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 roster_path=ROOT.parent/'20261114-staff-roster-growth-data/staff-roster-data.json';roster=json.loads(roster_path.read_text());profiles=roster['shared_initial_profiles'];assert len(profiles)==35
 binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'];images={};sources=[]
 for image_id in [8,14,15]:
  row=binding[image_id];b=z.read('algorithm-analysis/source/'+Path(row['path']).name);assert sha(b)==row['source_sha256'] and struct.unpack_from('<II',b)==(16,9)
  n,x,y,w,h=struct.unpack_from('<I4H',b,8);assert(w,h)==(256,1);pal=b[20:8+n];words=struct.unpack('<256H',pal);p=8+n;plen,px,py,pw,ph=struct.unpack_from('<I4H',b,p);pix=b[p+12:p+plen];assert p+plen==len(b) and len(pix)==pw*ph*2
  colors=[tuple(((v>>s)&31)*255//31 for s in (0,5,10))+(0 if v==0 else 255,) for v in words];im=Image.new('RGBA',(pw*2,ph));im.putdata([colors[v] for v in pix]);images[image_id]=dict(image=im,indices=pix,width=pw*2,height=ph,palette=pal,words=words)
  sources.append(dict(image_id=image_id,path=row['path'],file_sha256=sha(b),source_size_pixels=[pw*2,ph],source_pixel_sha256=sha(pix),palette_sha256=sha(pal),destination_pixel_rect_words=row['destination_pixel_rect_words'],destination_clut_rect_words=row['destination_clut_rect_words']))
 assert images[14]['palette']==images[15]['palette']
 crops=[];pictures={}
 for code in range(-1,35):
  if code==-1:image_id,kind,x,y,clut=8,7,48,136,492
  else:
   row,col=divmod(code,5);image_id=14 if row<6 else 15;kind=21 if row<6 else 23;x=col*48;y=(row if row<6 else row-6)*40;clut=494
  im=images[image_id];assert 0<=x<=im['width']-48 and 0<=y<=im['height']-40
  idx=b''.join(im['indices'][(y+dy)*im['width']+x:(y+dy)*im['width']+x+48] for dy in range(40));colors=b''.join(struct.pack('<H',im['words'][n]) for n in idx)
  source=binding[image_id];assert source['destination_clut_rect_words'][:2]==[0,clut]
  crops.append(dict(portrait_code=code,source_image_id=image_id,source_file=Path(source['path']).name,draw_record_kind=kind,source_rect=[x,y,48,40],clut_row=clut,indices_sha256=sha(idx),raw_color_words_sha256=sha(colors),palette_sha256=sha(im['palette']),inside_original_pixels=True,classification='unselected_ui_slot' if code==-1 else 'initial_staff_portrait'))
  pictures[code]=im['image'].crop((x,y,x+48,y+40))
 js('portrait-source-crops.json',dict(rows=crops,sources=sources,regular_portrait_size=[48,40],kao_palettes_identical=True,kao_common_palette_sha256=sha(images[14]['palette']),source_rule='Signed16code dividedby5 towardzero; row<6 kind21/KAO01, otherwise subtract6once kind23/KAO02. Code-1 is separateKYOU icon. Only normal0..34 and-1 bound here.',scope='35initialstaff portraits plus unselected UI placeholder; not all mathematically accepted signed16codes or body sprites.'))
 maps=[];references=[]
 for name in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
  b=z.read('algorithm-analysis/source/'+name+'.BIN');assert len(b)==76707
  oldsource=next(s for s in roster['sources'] if s['file'].endswith(name+'.BIN'));assert sha(b)==oldsource['file_sha256']
  rows=[]
  for sid in range(35):
   rec=b[24017+sid*54:24017+(sid+1)*54];name_index=rec[2];face=struct.unpack_from('<h',rec,7)[0];body=struct.unpack_from('<h',rec,5)[0];profile=profiles[sid]
   assert profile['id']==sid and name_index==profile['name_index'] and face==profile['portrait'] and 0<=face<35
   r=dict(staff_id=sid,name=profile['name'],name_index=name_index,portrait_code=face,packed_source_offset=24017+sid*54,packed_portrait_offset=7,runtime_portrait_offset=8,initial_body_appearance=body,packed_record_sha256=sha(rec));rows.append(r);references.append(face)
  maps.append(dict(map=name,source_sha256=sha(b),rows=rows))
 assert set(references)==set(range(35))
 js('town-staff-portrait-links.json',dict(maps=maps,reference_count=len(references),unique_portrait_codes=sorted(set(references)),name_source='Existing MSG00/PSMOJI-derivedstaff-roster-data.json. Names not newly decoded here.',body_note='Bodyappearance(+6runtime) is distinct and may change onassignment; portrait(+8runtime) is used byUI. Initialbodyvalues preserved without assuming runtimeidentity.'))
 # Preserve known direct callers without inventing argument semantics for every route.
 calls=[a for a in range(0x80011c00,0x80098000,4) if struct.unpack('<I',raw(a,4))[0]==0x0c019d77]
 assert calls==[0x800402d0,0x800700f4,0x80070150,0x8007034c,0x8007039c,0x80070480]
 js('portrait-ui-source-links.json',dict(wrapper='0x800675DC',direct_call_sites=[hex(a) for a in calls],confirmed_source_readers=[dict(call='0x800700F4',portrait_load='0x800700E4',source='staff60stride base80143FF8 +8; selectedstaff list'),dict(call='0x80070480',portrait_load='0x80070470',source='staff60stride base80143FF8 +8; staff profile'),dict(call='0x80070150',source='explicit A2=-1 at70148 for empty selection')],call_scope='Static references only; no natural UI execution or exhaustive indirect-call claim.'))
 # Code35 has no known initialstaff source. Its mathematical row is pastKAO02 payload.
 js('portrait-source-boundary.json',dict(normal_ranges=[dict(codes=[0,29],source='KAO01.TIM',grid=[5,6],max_source_bottom=240,source_height=256),dict(codes=[30,34],source='KAO02.TIM',grid=[5,1],max_source_bottom=40,source_height=40)],kao02_requested_height=64,kao02_normal_portraits_need_rows=[0,39],kao02_missing_rows_not_needed_for_normal_portraits=[40,63],first_outside_normal_code=dict(code=35,computed_source='KAO02.TIM',computed_rect=[0,40,48,40],inside_source=False,initial_staff_reference=False),special_minus1=dict(source='KYOU.TIM',rect=[48,136,48,40],is_extra_staff=False),warning='Earlier r2 tests passedwrapper codes through59 ascontrolledinputs; this doesnot establish60portraits or validpixels for35..59. No extra signedcode tests added.'))
 fontpath=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');font=ImageFont.truetype(str(fontpath),14) if fontpath.exists() else ImageFont.load_default()
 atlas=Image.new('RGB',(7*164,6*116),(38,40,44));d=ImageDraw.Draw(atlas)
 for i,p in enumerate(profiles):
  x=i%7*164+6;y=i//7*116+23;d.text((x,y-21),f"{p['id']:02d} {p['name']}",font=font,fill='white');picture=pictures[p['portrait']].resize((96,80),Image.Resampling.NEAREST);atlas.paste(picture,(x,y),picture)
 x=6;y=5*116+23;d.text((x,y-21),'-1 未選択',font=font,fill='white');p=pictures[-1].resize((96,80),Image.Resampling.NEAREST);atlas.paste(p,(x,y),p);atlas.save(ROOT/'staff-portrait-source-preview.png')
 spans=[('portrait_wrapper',0x800675dc,0x80067814),('selected_staff_portraits',0x80070000,0x80070194),('profile_portrait_reader',0x80070448,0x80070488)]
 ev=[];asm=[];cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
 for n,a,e in spans:
  bb=raw(a,e-a);fn='source/'+n+'.bin';(ROOT/fn).write_bytes(bb);ev.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(bb)));asm.append('# '+n);asm.extend(f'{i.address:08x}: {i.bytes.hex():8s} {i.mnemonic} {i.op_str}' for i in cs.disasm(bb,a))
 (ROOT/'portrait-readers.asm').write_text('\n'.join(asm)+'\n')
 js('source-provenance.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],images=sources,raw_exe_ranges=ev,existing_roster=dict(path=str(roster_path.relative_to(ROOT.parent.parent)),sha256=sha(roster_path.read_bytes())),known_before=['35staffnames andprofiles, fourtownrosters/packed54toruntime60 mapping','Original675DCportrait wrapper/5columns/6row switch and specialcode-1 already decoded and CPUtested inr2','OriginalTIM dimensions/transfer differences already extracted'],new_result='Join35actual staffportrait references across140records to exactKAO01/02pixels; separateplaceholder toKYOU; demonstrate normalcropsonKAO02 neverneed nonexistentrequestedrows40..63.',verification='One static extraction: hashes, packedrosterfields, cropbounds andcommonpalette match. No sourceCPUcalls or gameupdates.'))
 js('summary.json',dict(staff_profiles=35,initial_maps=4,packed_staff_references=140,regular_portrait_source_crops=35,special_placeholder_crops=1,kao01_portraits=30,kao02_portraits=5,missing_source_crops=0,kao_palettes_identical=True,direct_wrapper_call_sites=len(calls),original_cpu_calls=0,gameplay_updates=0,android_code_changed=False))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
