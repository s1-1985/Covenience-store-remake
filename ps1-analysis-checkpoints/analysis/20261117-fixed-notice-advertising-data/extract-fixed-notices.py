#!/usr/bin/env python3
"""Static ABI interpretation of notification5/6 and advertisement icon source join.
No original CPU execution or generated game state is used.
"""
import argparse,hashlib,json,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent;EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 previous=ROOT.parent/'20261117-notification-source-data';assert raw(0x80010974,72)==(previous/'source/raw_fixed_templates.bin').read_bytes()
 abi=[dict(template_offset=0,bytes=4,caller='A1',role='storedby41630,notreadagain'),dict(template_offset=4,bytes=4,caller='A2',role='packedXY'),dict(template_offset=8,bytes=4,caller='A3',role='packedWH'),dict(template_offset=12,bytes=2,caller='stack+0x10',role='recordkind'),dict(template_offset=14,bytes=2,caller='stack+0x12',role='U,V'),dict(template_offset=16,bytes=2,caller='stack+0x14',role='record+16CLUTcolumn'),dict(template_offset=18,bytes=2,caller='stack+0x16',role='record+18CLUTrow/reference'),dict(template_offset=20,bytes=3,caller='stack+0x18',role='RGBignoredwhenmode0')]
 decoded=[]
 for kind,address,local,call in [(5,0x80010998,0x58,0x8004056c),(6,0x80010974,0x30,0x800406cc)]:
  b=raw(address,36);x,y,w,h=struct.unpack_from('<4H',b,4);rk,u,v,col,row=struct.unpack_from('<HBBHH',b,12)
  fields=dict(flags=0x01000000,x=x,y=y,width=w,height=h,record_kind=rk,u=u,v=v,clut_column=col,clut_row_reference=row,rgb=[128,128,128],unwritten_byte23=None)
  assert w==0 and h==192
  decoded.append(dict(notification_kind=kind,template_address=hex(address),local_frame_offset=hex(local),copy_size=36,raw_hex=b.hex(),sha256=sha(b),call=hex(call),ignored_A1_word=struct.unpack_from('<I',b)[0],constructor_mode=0,derived_record_fields=fields,source_width_load='80041698:lhu fromcalleeFP+1C=entrySP+0C=A3low16',renderer_width_gate='80084848 readsrecord+8;80084850 zero->800849A4 beforepacketwrites',emits_rectangle_if_unmodified=False,natural_reachability='Not established. Previous34directreservation sites contain no constantkind5/6. Not proof ofglobalunused.'))
 js('fixed-template-argument-map.json',dict(template_layout=abi,rows=decoded,proof_scope='Static source template -> actualcallerargument offsets -> original41630 writes -> original84830 zero-width gate. Conditional onunmodifiedtemplates/record; not a naturalgame run.',important='Do not treat firstword32 aswidth, do not alignthisblob asafinished36byterecord, anddo not silentlyreplacewidth0with32/256. No intendedportrait/icon inferred fromthese misaligned-lookingbytes.'))
 # Original5-row promotion table routeskind4 parameter to6A304 andPS_CM1.
 oldpath=ROOT.parent/'20261114-advertising-popularity-data/advertising-data.json';old=json.loads(oldpath.read_text())['promotions'];promos=[]
 binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'][16];blob=z.read('algorithm-analysis/source/PS_CM1.TIM');assert sha(blob)==binding['source_sha256'] and struct.unpack_from('<II',blob)==(16,9)
 n,px,py,pw,ph=struct.unpack_from('<I4H',blob,8);assert(pw,ph)==(256,1);pal=blob[20:8+n];words=struct.unpack('<256H',pal);p=8+n;plen,px,py,pw,ph=struct.unpack_from('<I4H',blob,p);pix=blob[p+12:p+plen];assert p+plen==len(blob) and (pw*2,ph)==(256,160)
 rgba=[tuple(((w>>s)&31)*255//31 for s in (0,5,10))+(0 if w==0 else 255,) for w in words];im=Image.new('RGBA',(256,160));im.putdata([rgba[v] for v in pix]);arts=[]
 for i in range(5):
  b=raw(0x8009fe40+i*44,44);assert b.hex()==old[i]['raw_hex'];name=b[:24].split(b'\0')[0].decode('shift_jis');variant=struct.unpack_from('<i',b,28)[0];assert variant==old[i]['notification_variant'] and 0<=variant<5
  u,v=224,(96+32*variant)&255;dx,dy,dw,dh=binding['destination_pixel_rect_words'];sx=13*64*2+u-dx*2;sy=256+v-dy;assert sx==224 and 0<=sy<=128
  idx=b''.join(pix[(sy+y)*256+sx:(sy+y)*256+sx+32] for y in range(32));color=b''.join(struct.pack('<H',words[k]) for k in idx)
  promos.append(dict(promotion=i,name=name,master_address=hex(0x8009fe40+i*44),notification_kind=4,notification_parameter=variant,parameter_field_offset=28,source_image_id=16,source_image='PS_CM1.TIM',draw_record_kind=29,uv=[u,v],source_rect=[sx,sy,32,32],clut_xy=binding['destination_clut_rect_words'][:2],indices_sha256=sha(idx),raw_color_words_sha256=sha(color),inside_original_pixels=True,fully_transparent=all(words[k]==0 for k in idx)));arts.append(im.crop((sx,sy,sx+32,sy+32)))
 js('advertisement-notification-crops.json',dict(rows=promos,source_tim_sha256=sha(blob),palette_sha256=sha(pal),source_pixels=[256,160],known_before='Fivepromotionmethods/costs/variant0..4 and6A304iconformula existed. Newjoin is actualPS_CM1sourcepixels anddirectkind4callerparameterfield.',source_readers=['2795C..2798C:44byterow+28 ->A1;27980kind4;27998enqueue','27A54/27C38:twootherkind4enqueuepaths read same44byterow+28','40400..4040C:notificationparameter ->6A304','6A35C..6A37C:U224,V96+32*parameter;kind29,CLUTrow495']))
 fontpath=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');font=ImageFont.truetype(str(fontpath),14) if fontpath.exists() else ImageFont.load_default();preview=Image.new('RGB',(5*200,128),(38,40,44));d=ImageDraw.Draw(preview)
 for i,r in enumerate(promos):
  x=i*200+5;d.text((x,3),r['name'],font=font,fill='white');a=arts[i].resize((64,64),Image.Resampling.NEAREST);preview.paste(a,(x,30),a);d.text((x,102),f"kind4 / param{r['notification_parameter']}",fill='white')
 preview.save(ROOT/'advertisement-source-preview.png')
 spans=[('raw_fixed_templates',0x80010974,0x800109bc),('notification_template_copy',0x8003ff00,0x8003ff50),('fixed_kind5_call',0x80040518,0x80040574),('fixed_kind6_call',0x80040678,0x800406d4),('sprite_constructor',0x80041630,0x800419e0),('sprite_zero_size_gate',0x80084830,0x80084868),('byte_copy',0x8007e57c,0x8007e5b0),('advertisement_master',0x8009fe40,0x8009ff1c),('advertisement_parameter_reader',0x8002795c,0x800279a0),('advertisement_icon_helper',0x8006a304,0x8006a44c)]
 evidence=[];asm=[];cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
 for name,a,e in spans:
  b=raw(a,e-a);fn='source/'+name+'.bin';(ROOT/fn).write_bytes(b);evidence.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(b)))
  if name not in ['raw_fixed_templates','advertisement_master']:asm.append('# '+name);asm.extend(f'{i.address:08x}: {i.bytes.hex():8s} {i.mnemonic} {i.op_str}' for i in cs.disasm(b,a))
 (ROOT/'template-advertisement-readers.asm').write_text('\n'.join(asm)+'\n')
 js('source-provenance.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],source_image=dict(file='algorithm-analysis/source/PS_CM1.TIM',sha256=sha(blob),palette_sha256=sha(pal)),raw_exe_ranges=evidence,known_rule_sources=[dict(path=name,sha256=sha(z.read(name))) for name in ['algorithm-analysis/sprite_record.py','algorithm-analysis/render_control.py']],existing_advertising_data_sha256=sha(oldpath.read_bytes()),known_before='Spriteconstructor and zero-size renderer gate previouslydecoded/tested; fixedrawtemplates recordeduninterpretedlastturn. Fivepromotionmaster alreadyexported.',new_result='StaticactualABIjoin shows bothfixedkind5/6templates width0 andskiprectangleifunchanged. Fivekind4promotionvariants mappedtooriginalPS_CM1pixels.',verification='Static source bytes/ABIoffsets/gate/oldmasteralignment/cropbounds only; no originalCPUcalls or gameplayupdates.'))
 js('summary.json',dict(fixed_notification_templates=2,fixed_templates_derived_width_zero=2,promotion_image_bindings=5,missing_promotion_crops=0,natural_fixed_kind_reachability_confirmed=False,original_cpu_calls=0,gameplay_updates=0,android_code_changed=False))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
