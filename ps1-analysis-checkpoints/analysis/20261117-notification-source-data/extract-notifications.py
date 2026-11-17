#!/usr/bin/env python3
"""Static notification routes/callsites and project completion icon source join.
No source CPU execution, generated input trials or gameplay continuation.
"""
import argparse,collections,hashlib,json,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent;EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sint(v):return v if v<0x80000000 else v-0x100000000
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args();arch=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==arch['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN)
 entries=list(struct.unpack('<8I',raw(0x800109c0,32)));assert entries==[0x8004000c,0x8004015c,0x8004028c,0x800402e0,0x8004041c,0x8004057c,0x800406dc,0x800406ec]
 routes=[dict(kind=0,entry=None,source='no image switch branch',parameter='notused by imagebranch'),dict(kind=1,entry=hex(entries[0]),source='SHOPTYP1.TIM',image_id=6,reader='0x80067494',parameter='code&7 icon slot; see previous UIcropmap'),dict(kind=2,entry=hex(entries[1]),source='BUILDIN1.TIM',image_id=17,reader='0x8006B620',parameter='building notification icon index,not building kind'),dict(kind=3,entry=hex(entries[2]),source='KAO01/02.TIM orKYOU placeholder',reader='0x800675DC',parameter='portraitcode; see previous portraitcropmap'),dict(kind=4,entry=hex(entries[3]),source='PS_CM1.TIM',image_id=16,reader='0x8006A304',parameter='helperUVrow96+parameter*32; broaderparameterreachability notinventoried'),dict(kind=5,entry=hex(entries[4]),source='PS_CM1.TIM',image_id=16,reader='0x80041630',raw_template='0x80010998',parameter='rawtemplate only; exact resultingcrop notassigned inthiswork'),dict(kind=6,entry=hex(entries[5]),source='PS_CM1.TIM',image_id=16,reader='0x80041630',raw_template='0x80010974',parameter='rawtemplate only; exact resultingcrop notassigned inthiswork'),dict(kind=7,entry=hex(entries[6]),source='no image branch; active timer zeroed'),dict(kind=8,entry=hex(entries[7]),source='no image branch; active timer zeroed')]
 js('notification-image-routes.json',dict(switch_table='0x800109C0',kind_global='0x800E3BE4',parameter_global='0x800E3BE8',rows=routes,important='Kind selects image path; queue mode+2 independentlyselects text/report presentation. Kind7/8 timerzero isnotproofactiveflagcleared.',modes=[dict(mode=1,content='currenttextarea800E3AA0;kind<7 copiesqueued120bytebody,kind>=7 skipscopy',text_x_offset_rule='kind0:+32;kind3:+72;others:+56',text_y_offset=16),dict(mode=2,content='monthlyreport renderer8006C048 at0,64'),dict(mode=3,content='annualreport renderer8006C8B0 at16,48')],known_before='Basic queue and displaycontrol alreadydecoded inr2 event_queue.py/notification_display.py; this work records source routes and icon binding.'))
 # Conservative local constant propagation. Reset at each earlier control transfer.
 # Values inherited from predecessors, loads and function returns remain unknown.
 def constargs(a):
  seq=list(cs.disasm(raw(a-256,264),a-256));before=[i for i in seq if i.address<a];start=0
  for j,i in enumerate(before):
   if i.mnemonic.startswith('b') or i.mnemonic in ['j','jal','jalr','jr']:start=min(j+2,len(before))
  r={'$zero':0};last={};stack=None
  for i in before[start:]+[i for i in seq if i.address==a+4]:
   p=[x.strip() for x in i.op_str.split(',')];m=i.mnemonic;value=None;dest=p[0] if p else None
   def rv(s):return r.get(s)
   def imm(s):return int(s,0)
   if m=='nop':continue
   if m=='sw':
    if len(p)==2 and p[1] in ['0x10($sp)','16($sp)']:stack=dict(value=sint(rv(p[0])) if rv(p[0]) is not None else None,writer=hex(i.address),instruction=m+' '+i.op_str)
    continue
   if m in ['sb','sh','swl','swr','mtc1','mult','multu','div','divu']:continue
   if m=='move':value=rv(p[1])
   elif m=='lui':value=imm(p[1])<<16
   elif m in ['addiu','addi','ori','andi','xori']:
    v=rv(p[1]);k=imm(p[2]);value=None if v is None else v+k if m in ['addiu','addi'] else v|k if m=='ori' else v&k if m=='andi' else v^k
   elif m in ['addu','or','and','xor','subu']:
    x,y=rv(p[1]),rv(p[2]);value=None if x is None or y is None else x+y if m=='addu' else x|y if m=='or' else x&y if m=='and' else x^y if m=='xor' else x-y
   elif m in ['sll','srl']:
    v=rv(p[1]);value=None if v is None else v<<imm(p[2]) if m=='sll' else (v&0xffffffff)>>imm(p[2])
   if dest and dest.startswith('$') and dest!='$zero':r[dest]=None if value is None else value&0xffffffff;last[dest]=dict(writer=hex(i.address),instruction=m+' '+i.op_str)
  return dict(block_start=hex(before[start].address) if start<len(before) else hex(a),arguments={name:dict(value=sint(r[reg]) if r.get(reg) is not None else None,**last.get(reg,{})) for name,reg in [('image_kind','$a0'),('image_parameter','$a1'),('sound_request','$a2'),('queue_mode','$a3')]},variant_stack_argument=stack)
 sites=[];windows=bytearray()
 for a in range(0x80011c00,0x80098000,4):
  if struct.unpack('<I',raw(a,4))[0]!=0x0c00fb36:continue
  sites.append(dict(call=hex(a),**constargs(a)));windows.extend(raw(a-256,264))
 assert len(sites)==34
 js('notification-reservation-sites.json',dict(callee='0x8003ECD8',rows=sites,scope='DirectJALonly. Withinlastcontrol-transfer-freeblock, immediate arithmetic/copies are propagated. Loads/callreturns/predecessor values areunknown(null). No paths/indirectcalls or exactruntimevalues inferred.',raw_windows='source/enqueue-call-windows.bin',window_bytes=264,window_start_relative_to_call=-256))
 (ROOT/'source/enqueue-call-windows.bin').write_bytes(windows)
 # FullBUILDIN1 icon sheet. Normalprojectuses are a separate subset,notall32.
 binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'][17];blob=z.read('algorithm-analysis/source/BUILDIN1.TIM');assert sha(blob)==binding['source_sha256'] and struct.unpack_from('<II',blob)==(16,9)
 n,px,py,pw,ph=struct.unpack_from('<I4H',blob,8);assert(pw,ph)==(256,1);pal=blob[20:8+n];words=struct.unpack('<256H',pal);p=8+n;plen,px,py,pw,ph=struct.unpack_from('<I4H',blob,p);pixels=blob[p+12:p+plen];assert p+plen==len(blob) and (pw*2,ph)==(256,128)
 rgba=[tuple(((v>>s)&31)*255//31 for s in (0,5,10))+(0 if v==0 else 255,) for v in words];im=Image.new('RGBA',(256,128));im.putdata([rgba[v] for v in pixels]);icons=[];pictures={}
 for i in range(32):
  u=(i%8)*32;v=(i//8*32-128)&255;dx,dy,dw,dh=binding['destination_pixel_rect_words'];sx=13*64*2+u-dx*2;sy=v-dy;assert 0<=sx<=224 and 0<=sy<=96
  idx=b''.join(pixels[(sy+y)*256+sx:(sy+y)*256+sx+32] for y in range(32));color=b''.join(struct.pack('<H',words[n]) for n in idx)
  icons.append(dict(icon=i,source_image_id=17,draw_record_kind=13,uv=[u,v],source_rect=[sx,sy,32,32],clut_xy=binding['destination_clut_rect_words'][:2],indices_sha256=sha(idx),raw_color_words_sha256=sha(color),fully_transparent=all(words[n]==0 for n in idx),inside_original_pixels=True));pictures[i]=im.crop((sx,sy,sx+32,sy+32))
 js('building-notification-crops.json',dict(source_file='BUILDIN1.TIM',file_sha256=sha(blob),palette_sha256=sha(pal),source_pixels=[256,128],rows=icons,scope='Geometric0..31iconslot coverage; doesnotestablish every slotisusedbynormalplay.'))
 master=json.loads((ROOT.parent/'20261115-town-project-data/project-master.json').read_text())['rows'];links=[]
 for row in master:
  kind=row['kind'];name=row['name'];b=raw(0x8009d738+kind*56,56);icon=struct.unpack_from('<h',b,52)[0];assert icon==row['notification_event'] and 0<=icon<32
  links.append(dict(project_selection=row['selection'],building_kind=kind,name=name,notification_image_kind=2,notification_image_parameter=icon,source_image_id=17,source_rect=icons[icon]['source_rect'],existing_name_message_index=row['completion_name_message'],icon_fully_transparent=icons[icon]['fully_transparent']))
 js('project-notification-image-links.json',dict(rows=links,source_reader='80029284..800292A4 loadsbuildingmaster+52 intoV0;800292DC..800292EC passeskind2,paramV0 toreservation',important='Buildingkind,projectselection andnotification iconindex aredifferent. Three schools shareicon8; gym/pool shareicon18. Do notforceuniquegraphics for eachbuildingname.'))
 fontpath=Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc');font=ImageFont.truetype(str(fontpath),14) if fontpath.exists() else ImageFont.load_default()
 atlas=Image.new('RGB',(6*180,3*120),(38,40,44));draw=ImageDraw.Draw(atlas)
 for j,row in enumerate(links):
  x=j%6*180+5;y=j//6*120+24;draw.text((x,y-22),row['name'],font=font,fill='white');art=pictures[row['notification_image_parameter']].resize((64,64),Image.Resampling.NEAREST);atlas.paste(art,(x,y),art);draw.text((x,y+71),f"kind {row['building_kind']} / icon {row['notification_image_parameter']}",fill='#cccccc')
 atlas.save(ROOT/'project-notification-icons-preview.png')
 spans=[('image_switch_table',0x800109c0,0x800109e0),('raw_fixed_templates',0x80010974,0x800109bc),('notification_display',0x8003ff00,0x8004095c),('building_icon_reader',0x8006b620,0x8006b780),('completion_icon_parameter',0x80029284,0x800292f4)]
 ev=[];asm=[]
 for name,a,e in spans:
  b=raw(a,e-a);fn='source/'+name+'.bin';(ROOT/fn).write_bytes(b);ev.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(b)))
  if name not in ['image_switch_table','raw_fixed_templates']:asm.append('# '+name);asm.extend(f'{i.address:08x}: {i.bytes.hex():8s} {i.mnemonic} {i.op_str}' for i in cs.disasm(b,a))
 (ROOT/'notification-readers.asm').write_text('\n'.join(asm)+'\n')
 js('source-provenance.json',dict(exe_sha256=EXE_SHA,archive_sha256=arch['sha256'],building_icon_tim_sha256=sha(blob),raw_exe_ranges=ev,reservation_windows_sha256=sha(windows),known_rule_sources=[dict(path=name,sha256=sha(z.read(name))) for name in ['algorithm-analysis/event_queue.py','algorithm-analysis/notification_display.py']],known_before='Notificationqueue/display modes and basiciconhelper alreadydecoded;18projects andnotification_event fields alreadyexported. Newworkjoins34directcalls,8imageroutes and18projects to15actualBUILDIN1icon pixels.',verification='Static hashes, switch/argument decoding, knownfield comparison andcropbounds. No sourceCPUcalls/gameplayupdates.'))
 js('summary.json',dict(direct_reservation_calls=len(sites),calls_with_local_constant_kind=sum(s['arguments']['image_kind']['value'] is not None for s in sites),calls_with_local_constant_mode=sum(s['arguments']['queue_mode']['value'] is not None for s in sites),image_switch_branches=8,building_icon_slots=32,building_icon_nontransparent_slots=sum(not i['fully_transparent'] for i in icons),projects=18,distinct_project_notification_icons=len({r['notification_image_parameter'] for r in links}),project_icons_transparent=sum(r['icon_fully_transparent'] for r in links),missing_project_crops=0,original_cpu_calls=0,gameplay_updates=0,android_code_changed=False))
 print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
