#!/usr/bin/env python3
"""Static binding of known permit dialog rules to original text and image data."""
import argparse,hashlib,json,runpy,struct,zipfile
from pathlib import Path
from PIL import Image,ImageDraw
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 manifest=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text());assert sha(args.archive.read_bytes())==manifest['sha256'];z=zipfile.ZipFile(args.archive)
 exe=z.read('algorithm-analysis/source/SLPS_007.82');assert sha(exe)==EXE_SHA
 def raw(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
 def imm(a):return struct.unpack('<I',raw(a,4))[0]&65535
 for n in ['source']: (ROOT/n).mkdir(exist_ok=True)
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
 msg=z.read('algorithm-analysis/source/MSG00.OBJ');messages=[];packed=bytearray()
 def stream(b,p):
  codes=[]
  for i in range(100):
   c=struct.unpack_from('<H',b,p+2*i)[0];codes.append(c)
   if c==0x40ff:return codes,b[p:p+2*len(codes)]
  raise AssertionError('no terminator')
 for mid in [16,17,18,24,25,26,272,273,274]:
  off=struct.unpack_from('<I',msg,mid*4)[0];codes,b=stream(msg,off)
  messages.append(dict(id=mid,source_offset=off,packed_offset=len(packed),bytes=len(b),codes=codes,transcription=dec(codes),sha256=sha(b)));packed.extend(b)
 (ROOT/'source/dialog-messages.bin').write_bytes(packed)
 codes,b=stream(exe,0x80099858-0x80010000+2048);assert dec(codes)=='申請済み';(ROOT/'source/already-applied-string.bin').write_bytes(b)
 put('dialog-text-source.json',dict(source='/DAT/MSG00.OBJ',source_sha256=sha(msg),messages=messages,raw_status_string=dict(address='0x80099858',codes=codes,transcription=dec(codes),sha256=sha(b)),policy='Transcriptions reuse original font mapping; commands/arguments retained. Button glyph inmessage18 is not assigned a new Unicode meaning.'))
 fees=[]
 for i,a in enumerate([0x80042634,0x80042644,0x80042654]):
  value=(imm(a)<<16)|imm(a+4);fees.append(value)
 assert fees==list(struct.unpack('<3i',raw(0x800b92d0,12)))==[3000000,7000000,10000000]
 (ROOT/'source/display-fee-literals.bin').write_bytes(raw(0x80042634,48))
 rows=[]
 for i in range(3):rows.append(dict(type=i,product=[8,2,22][i],store_byte_offset=0xc74+i,label_message=24+i,label_screen_xy=[72,80+16*i],applied_string_screen_xy=[128,80+16*i],cost_message=272+i,cost_value_slot=i,cost=fees[i],cost_screen_xy=[128,80+16*i],unavailable_message=17,unavailable_screen_xy=[120,80+16*i],unavailable_mask_bit=1<<i))
 states=[]
 for owned in range(8):
  flags=[(owned>>i)&1 for i in range(3)]
  for unavailable in range(8):
   lines=[dict(type=i,status='already_applied' if flags[i]!=0 else 'unavailable' if unavailable&(1<<i) else 'fee',screen_xy=rows[i]['applied_string_screen_xy'] if flags[i]!=0 else rows[i]['unavailable_screen_xy'] if unavailable&(1<<i) else rows[i]['cost_screen_xy']) for i in range(3)]
   states.append(dict(owned_flags=flags,unavailable_mask=unavailable,lines=lines,acknowledgement_only=(unavailable&7)==7 or flags==[1,1,1]))
 put('dialog-state-source.json',dict(rows=rows,states=states,scope='64static0/1input combinations; not64executions or natural reachability proof.',rule='Existing nonzero flag displays original申請済み before testing unavailable bit. Otherwisebit1 showsmessage17,bit0 showsfee.',fee_source='UI writes three immediateconstants into0x800E4000/4/8. These equal the existingfee table0x800B92D0 in this EXE; do not mistake slots for existing funds.',ack_rule='Parent422A4 takes acknowledgement loop when low3unavailablebits==7 OR all3storebytes equal exactly1. Nonzero status label and exact1 all-owned branch are distinct raw tests.'))
 binding=json.loads((ROOT.parent/'20261117-texture-runtime-binding-data/texture-bindings.json').read_text())['rows'][8]
 blob=z.read('algorithm-analysis/source/KYOU.TIM');assert sha(blob)==binding['source_sha256'] and struct.unpack_from('<II',blob)==(16,9)
 clen,cx,cy,cw,ch=struct.unpack_from('<I4H',blob,8);pal=struct.unpack_from('<256H',blob,20);p=8+clen;plen,px,py,pw,ph=struct.unpack_from('<I4H',blob,p);pix=blob[p+12:p+plen];assert (pw*2,ph)==(256,240)
 rgba=[tuple(((w>>s)&31)*255//31 for s in [0,5,10])+(0 if w==0 else 255,) for w in pal];im=Image.new('RGBA',(256,240));im.putdata([rgba[n] for n in pix])
 # UV immediates are read from actual producer instructions, not guessed from images.
 defs=[('checkbox_nonzero',0x80043974,48,'0x800438CC'),('checkbox_zero',0x800439f8,48,'0x800438CC'),('row_symbol_1',0x80043b5c,16,'0x80043A80'),('row_symbol_2',0x80043be0,16,'0x80043A80'),('row_symbol_3',0x80043c64,16,'0x80043A80')]
 crops=[];atlas=Image.new('RGB',(5*126,100),(38,40,44));draw=ImageDraw.Draw(atlas)
 for i,(name,a,v,reader) in enumerate(defs):
  u=imm(a);assert 0<=u<=240 and v+16<=ph;indices=b''.join(pix[(v+y)*256+u:(v+y)*256+u+16] for y in range(16));colors=b''.join(struct.pack('<H',pal[n]) for n in indices)
  crops.append(dict(key=name,draw_kind=7,uv=[u,v],source_rect=[u,v,16,16],clut_xy=[0,492],reader=reader,immediate_address=hex(a),indices_sha256=sha(indices),raw_color_words_sha256=sha(colors)))
  tile=im.crop((u,v,u+16,v+16)).resize((48,48),Image.Resampling.NEAREST);atlas.paste(tile,(i*126+8,26),tile);draw.text((i*126+4,5),name,fill='white');draw.text((i*126+8,80),f'{u},{v}',fill='#bbbbbb')
 assert [x['uv'] for x in crops]==[[160,48],[176,48],[128,16],[144,16],[160,16]]
 atlas.save(ROOT/'permit-control-source-preview.png');put('control-image-source.json',dict(source_file='KYOU.TIM',source_sha256=sha(blob),source_size_pixels=[256,240],rows=crops,policy='Raw original pixels only. No assumed RGB for unwritten template bytes; no claim of GPU compositing or semantic meaning of row symbols.'))
 spans=[('permit_dialog',0x800422a4,0x80042c7c),('checkbox_call_sites',0x80042e70,0x8004301c),('unavailable_text',0x800437f0,0x800438cc),('checkbox_helper',0x800438cc,0x80043a80),('row_symbol_helper',0x80043a80,0x80043cf4)]
 cs=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);evidence=[];asm=[]
 for name,a,e in spans:
  b=raw(a,e-a);fn='source/'+name+'.bin';(ROOT/fn).write_bytes(b);evidence.append(dict(file=fn,start=hex(a),end_exclusive=hex(e),sha256=sha(b)));asm.append('# '+name);asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in cs.disasm(b,a))
 (ROOT/'permit-ui-readers.asm').write_text('\n'.join(asm)+'\n')
 put('android-permit-dialog-bridge.json',dict(status='analysis_only',android_code_changed=False,acquisition_rules='../20261114-permit-siting-data/android-permit-siting-bridge.json',product_menu='../20261117-product-menu-source-data/android-product-menu-bridge.json',text='dialog-text-source.json',states='dialog-state-source.json',images='control-image-source.json',window=dict(screen_xy=[32,48],size_cells=[16,7],size_pixels=[256,112]),prompt=dict(message=16,screen_xy=[80,64]),footer=dict(message=18,screen_xy=[96,128]),row_symbols=dict(selector=[1,2,3],screen_xy=[[48,80],[48,96],[48,112]],semantic_names_unassigned=True),checkbox_value_rule='Nonzero ->UV160,48; zero->176,48. Do notinfer checkedmeaning from the copiedinput exclusionmask alone.',limitations=['No original CPUcalls or full screen composition.','Only five controlcrops, not full UI inventory.','Checkbox interactions/confirmation/transaction rules reuse earlier acquisition analysis; no new gameplay rule claim.']))
 put('source-provenance.json',dict(archive_sha256=manifest['sha256'],exe_sha256=EXE_SHA,exe_ranges=evidence,known_before='Permitfees/acquisition/siting/transaction semantics recovered20261114. Current addition: UI rawtext/status priority,fee message slots andfivecontrol image bindings.',original_cpu_calls=0))
 put('summary.json',dict(messages=9,raw_exe_status_strings=1,control_image_crops=5,static_dialog_state_rows=64,original_cpu_calls=0,operating_updates=0,android_code_changed=False));print((ROOT/'summary.json').read_text())
if __name__=='__main__':main()
