#!/usr/bin/env python3
"""Link original TIM load requests, rectangle selection and upload payloads.
GPU LoadImage boundary is captured, not rendered. No game-day continuation.
"""
import argparse,hashlib,json,struct,zipfile,itertools
from pathlib import Path
from unicorn import Uc,UC_ARCH_MIPS,UC_MODE_MIPS32,UC_MODE_LITTLE_ENDIAN,UC_HOOK_CODE
from unicorn.mips_const import UC_MIPS_REG_SP,UC_MIPS_REG_FP,UC_MIPS_REG_RA,UC_MIPS_REG_PC,UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3
ROOT=Path(__file__).resolve().parent;EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd';STOP=0x80001000;SP=0x801f0000
TIM_TYPES={0:0x80187e00,7:0x801f1600,8:0x8015ea00,9:0x80182e00}
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def constant(word,reg):
 op=word>>26;rs=(word>>21)&31;rt=(word>>16)&31;rd=(word>>11)&31
 if op==9 and rs==0 and rt==reg:return struct.unpack('<h',struct.pack('<H',word&65535))[0]
 if op==0 and (word&63) in (0x21,0x25) and rs==rt==0 and rd==reg:return 0
 return None
def overlap(a,b):
 x=max(a[0],b[0]);y=max(a[1],b[1]);r=min(a[0]+a[2],b[0]+b[2]);d=min(a[1]+a[3],b[1]+b[3]);return [x,y,r-x,d-y] if x<r and y<d else None
def tim(b):
 magic,flags=struct.unpack_from('<2I',b);assert magic==16;pos=8;clut=None
 if flags&8:
  n=struct.unpack_from('<I',b,pos)[0];clut=dict(rect=list(struct.unpack_from('<4H',b,pos+4)),offset=pos+12,bytes=n-12);pos+=n
 n=struct.unpack_from('<I',b,pos)[0];pix=dict(rect=list(struct.unpack_from('<4H',b,pos+4)),offset=pos+12,bytes=n-12)
 assert pos+n==len(b)
 return flags,pix,clut
def machine(exe):
 u=Uc(UC_ARCH_MIPS,UC_MODE_MIPS32|UC_MODE_LITTLE_ENDIAN);u.mem_map(0,0x200000);u.mem_write(0x10000,exe[2048:]);return u
def call(u,entry):
 for r,v in [(UC_MIPS_REG_SP,SP),(UC_MIPS_REG_FP,SP),(UC_MIPS_REG_RA,STOP)]:u.reg_write(r,v)
 u.emu_start(entry,STOP,count=10000);assert u.reg_read(UC_MIPS_REG_PC)==STOP

def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256']
 z=zipfile.ZipFile(args.archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 raw=lambda a,n:exe[a-0x80010000+2048:a-0x80010000+2048+n]
 word=lambda a:struct.unpack('<I',raw(a,4))[0]
 def name(a):return raw(a,300).split(b'\0')[0].decode('ascii').replace('\\','/').removesuffix(';1')
 calls=[]
 for a in range(0x80011c00,0x80098000,4):
  if word(a)!=0x0c00503a:continue # JAL800140E8
  index=constant(word(a-8),4);kind=constant(word(a-4),5)
  calls.append(dict(address=hex(a),index=index,resource_type=kind,argument_words=[hex(word(a-8)),hex(word(a-4))],delay_word=hex(word(a+4)),image_request=kind in TIM_TYPES))
 assert calls and all(c['index'] is not None for c in calls if c['image_request'])
 used=sorted({c['index'] for c in calls if c['image_request']});assert used==list(range(29))+[30,31]
 # No literal function pointer to this entry is present in original EXE; not a general indirect-call proof.
 literal=[hex(a) for a in range(0x80010000,0x80010000+len(exe)-2048,4) if word(a)==0x800140e8]
 rows=[];execution=[]
 for index in range(34):
  path=name(word(0x8009863c+4*index));b=z.read('algorithm-analysis/source/'+Path(path).name) if index<32 else (ROOT.parent/'20261113-disc-data-extraction/source'/Path(path).name).read_bytes();flags,pix,clut=tim(b)
  r=dict(id=index,path=path,source_sha256=sha(b),flags=flags,index_bits=4 if flags&7==0 else 8 if flags&7==1 else None,source_pixel_rect=pix['rect'],source_clut_rect=clut['rect'] if clut else None,source_file_bytes=len(b),direct_request_addresses=[c['address'] for c in calls if c['image_request'] and c['index']==index],directly_requested=index in used)
  if index>=32:
   r['binding_status']='Filename only; no dedicated rectangle in32-entry banks and no direct image request in scan.';rows.append(r);continue
  pixel_rect=list(struct.unpack('<4H',raw(0x800983d0+8*index,8)));palette_rect=list(struct.unpack('<4H',raw(0x800984d0+8*index,8)));assert clut
  r.update(destination_pixel_rect_words=pixel_rect,destination_clut_rect_words=palette_rect,decoded_width_pixels=pixel_rect[2]*(4 if r['index_bits']==4 else 2),height_pixels=pixel_rect[3],binding_status='Direct request and rectangle' if index in used else 'Rectangle and filename; no direct request in scan.')
  assert pix['rect'][2]==pixel_rect[2] and clut['rect'][2:]==palette_rect[2:]
  requested=pixel_rect[2]*pixel_rect[3]*2
  r.update(source_pixel_bytes=pix['bytes'],requested_pixel_bytes=requested,valid_pixel_bytes=min(requested,pix['bytes']),request_beyond_pixel_bytes=max(0,requested-pix['bytes']),source_pixel_bytes_not_requested=max(0,pix['bytes']-requested),valid_height_pixels=min(pixel_rect[3],pix['rect'][3]))
  # Native rectangle selector and native TIM parser/upload wrapper. Only GPU boundary returns early.
  u=machine(exe)
  for reg,v in [(UC_MIPS_REG_A0,index),(UC_MIPS_REG_A1,0x801d0000),(UC_MIPS_REG_A2,0x801d0008)]:u.reg_write(reg,v)
  call(u,0x80013f7c);selected=bytes(u.mem_read(0x1d0000,16));assert list(struct.unpack('<8H',selected))==pixel_rect+palette_rect
  u.mem_write(0x180000,b'\xa5'*0x22000);u.mem_write(0x180000,b);uploads=[]
  def gpu(uc,a,size,ctx):
   if a!=0x80080ca0:return
   rect=list(struct.unpack('<4h',uc.mem_read(uc.reg_read(UC_MIPS_REG_A0)&0x1fffffff,8)));ptr=uc.reg_read(UC_MIPS_REG_A1)&0x1fffffff;n=rect[2]*rect[3]*2
   uploads.append(dict(destination_rect_words=rect,source_file_offset=ptr-0x180000,bytes=n,sha256=sha(bytes(uc.mem_read(ptr,n)))))
   uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  u.hook_add(UC_HOOK_CODE,gpu)
  packed=struct.unpack('<4I',selected)
  for reg,v in [(UC_MIPS_REG_A0,0x80180000),(UC_MIPS_REG_A1,packed[0]),(UC_MIPS_REG_A2,packed[1]),(UC_MIPS_REG_A3,packed[2])]:u.reg_write(reg,v)
  u.mem_write((SP+16)&0x1fffffff,struct.pack('<I',packed[3]));call(u,0x80013eac)
  assert len(uploads)==2
  for actual,expected,rect in zip(uploads,[pix,clut],[pixel_rect,palette_rect]):
   assert actual['destination_rect_words']==rect and actual['source_file_offset']==expected['offset']
   n=actual['bytes'];valid=min(n,expected['bytes']);observed=bytes(u.mem_read(0x180000+expected['offset'],n))
   assert observed[:valid]==b[expected['offset']:expected['offset']+valid]
   if n>valid:assert observed[valid:]==b'\xa5'*(n-valid)
   actual.update(valid_file_bytes=valid,request_beyond_file_payload=max(0,n-expected['bytes']),omitted_file_payload=max(0,expected['bytes']-n),valid_prefix_sha256=sha(observed[:valid]),synthetic_tail_byte=165 if n>valid else None)
  r['native_uploads']=uploads;rows.append(r);execution.append(dict(id=index,uploads=uploads,pixel_source_position_ignored=pix['rect'][:2]!=pixel_rect[:2],clut_source_position_ignored=clut['rect'][:2]!=palette_rect[:2],directly_requested=index in used))
 pixel_collisions=[];palette_collisions=[]
 for a,b in itertools.combinations(rows[:32],2):
  for key,target in [('destination_pixel_rect_words',pixel_collisions),('destination_clut_rect_words',palette_collisions)]:
   rect=overlap(a[key],b[key])
   if rect:target.append(dict(images=[a['id'],b['id']],overlap_rect_words=rect))
 prior_bytes=z.read('algorithm-analysis/tim-source-transfer-manifest.json');prior=json.loads(prior_bytes)
 assert len(prior)==32
 for old,current in zip(prior,rows[:32]):
  assert old['id']==current['id'] and old['sha256']==current['source_sha256']
  assert old['source_pixel_rectangle']==current['source_pixel_rect'] and old['destination_pixel_rectangle']==current['destination_pixel_rect_words']
  assert old['source_pixel_word_bytes']==current['source_pixel_bytes'] and old['requested_pixel_word_bytes']==current['requested_pixel_bytes']
 js('prior-evidence-crosscheck.json',dict(archive_path='algorithm-analysis/tim-source-transfer-manifest.json',sha256=sha(prior_bytes),matched_rows=32,known_before='All32 source/destination rectangles,14 dimension differences and source/requested byte counts were already in the archived manifest; old GPU-port manifest also exists. These are reused facts, not new decoding.',new_binding='55 direct loader JAL sites,39 TIM requests referencing31 IDs; all34 filename entries,32 rectangle rows and48 pixel/49 CLUT overlap pairs joined into one bounded binding inventory.'))
 icons=[];base=rows[7];b=z.read('algorithm-analysis/source/CASE_T00.TIM');flags,pix,clut=tim(b);bitmap=b[pix['offset']:pix['offset']+pix['bytes']];palette=b[clut['offset']:clut['offset']+clut['bytes']];stride=pix['rect'][2]*2
 assert flags==9 and stride==256
 for fixture in range(53):
  icon=word(0x80099f0c+fixture*196+80);x=(icon%8)*32;y=(icon//8)*32
  assert x+32<=stride and y+32<=pix['rect'][3]
  indices=b''.join(bitmap[(y+dy)*stride+x:(y+dy)*stride+x+32] for dy in range(32))
  icons.append(dict(fixture_kind=fixture,icon_index=icon,source_image_id=7,source_rect_pixels=[x,y,32,32],indices_sha256=sha(indices),palette_sha256=sha(palette),clut_destination=base['destination_clut_rect_words'][:2],source_rows_complete=True,uses_past_source_height=False))
 js('fixture-icon-source-coverage.json',dict(rows=icons,scope='53 descriptor icon rectangles against original CASE_T00 pixels. Not proof all UI/fixture sprites use only valid source rows.',known_before='Descriptor icon IDs and CASE_T01 difference at icon54 were previously extracted. New join checks those53 icons against confirmed upload/source boundary.'))
 js('texture-bindings.json',dict(schema_version=1,rows=rows));js('load-callsites.json',dict(scan_start='0x80011c00',scan_end_exclusive='0x80098000',calls=calls,literal_loader_function_pointers=literal,limits='Direct JAL sites and immediate arguments only. No claim of whole-program reachability or absence of computed indirect calls/data mutation.'))
 js('native-upload-results.json',execution);js('vram-overlaps.json',dict(pixel=pixel_collisions,clut=palette_collisions,scope='Potential overlaps from alternative images; not proof all pairs coexist in a single screen.'))
 spans=[('rectangle_and_upload_helpers',0x80013eac,0x800140e8),('tim_loader_variants',0x800140e8,0x800149b8),('tim_parser',0x800855dc,0x800856c0),('rectangle_banks',0x800983d0,0x800985d0),('filename_bank',0x8009863c,0x800986c4)]
 for n,a,e in spans:(ROOT/'source'/f'{n}.bin').write_bytes(raw(a,e-a))
 ranges=[dict(file='source/'+n+'.bin',file_offset=0,start=hex(a),end_exclusive=hex(e),sha256=sha(raw(a,e-a))) for n,a,e in spans]
 windows=bytearray()
 for c in calls:
  a=int(c['address'],16);b=raw(a-8,16);ranges.append(dict(file='source/load-call-windows.bin',file_offset=len(windows),start=hex(a-8),end_exclusive=hex(a+8),sha256=sha(b)));windows.extend(b)
 (ROOT/'source/load-call-windows.bin').write_bytes(windows)
 js('source-ranges.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],ranges=ranges))
 js('summary.json',dict(direct_loader_calls=len(calls),direct_image_calls=sum(c['image_request'] for c in calls),unique_direct_images=len(used),rectangle_bound_images=32,filename_entries=34,no_direct_request_ids=[29,32,33],native_upload_cases=32,native_gpu_calls_captured=64,gpu_calls_replaced=64,gameplay_updates=0,pixel_overlapping_pairs=len(pixel_collisions),clut_overlapping_pairs=len(palette_collisions),different_pixel_header_position_count=sum(x['pixel_source_position_ignored'] for x in execution),different_clut_header_position_count=sum(x['clut_source_position_ignored'] for x in execution),different_pixel_height_count=sum(r['source_pixel_rect'][3]!=r['height_pixels'] for r in rows[:32]),extends_source_count=sum(r['request_beyond_pixel_bytes']>0 for r in rows[:32]),crops_source_count=sum(r['source_pixel_bytes_not_requested']>0 for r in rows[:32])))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
