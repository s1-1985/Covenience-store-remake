#!/usr/bin/env python3
"""Bounded original settings application and sound dispatch, not UI/audio replay."""
import hashlib,importlib.util,json,struct,sys
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helper',ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def out(n,x):(ROOT/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main(path):
 exe=Path(path).read_bytes();assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 tracks=list(struct.unpack('<4i',raw(0x80099864,0x80099874)))
 cases=[]
 for packed in (0,0x103,0x202):
  u=P.machine(exe);u.mem_write(0xcd898,struct.pack('<H',packed));calls=[]
  for r,v in ((UC_MIPS_REG_SP,P.SP),(UC_MIPS_REG_FP,P.SP)):u.reg_write(r,v)
  def hook(uc,pc,n,c):
   if pc==0x80062690:uc.emu_stop()
   elif pc==0x80065100:
    calls.append([uc.reg_read(UC_MIPS_REG_A0),uc.reg_read(UC_MIPS_REG_A1)]);uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x800625c4,P.STOP,count=10000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x80062690
  observed=[u.mem_read(a,1)[0] for a in (0xcd834,0xcd835,0xcd8a9)]
  expected=[1-(packed&1),1-((packed>>1)&1),(packed>>8)+1]
  assert observed==expected and calls==[[tracks[expected[2]],0]]
  cases.append(dict(packed=hex(packed),se_enabled=observed[0],monthly_report_enabled=observed[1],music_selector=observed[2],music_request=calls))
 dispatch=[]
 for se,ident in ((1,1),(0,1),(0,28)):
  u=P.machine(exe);u.mem_write(0xcd834,bytes([se]));P.put(u,0xcd990,0xffffffff);u.reg_write(UC_MIPS_REG_A0,ident);calls=[]
  targets={0x8008ea7c,0x80064550,0x80018a5c,0x80064740}
  def hook(uc,pc,n,c):
   if pc in targets:
    calls.append(dict(callee=hex(pc),a0=uc.reg_read(UC_MIPS_REG_A0),a1=uc.reg_read(UC_MIPS_REG_A1)))
    uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);P.call(u,0x80064e4c);u.hook_del(h)
  assert [x['callee'] for x in calls]==(['0x8008ea7c'] if se else [] if ident==1 else ['0x80064550','0x80018a5c','0x80064740'])
  dispatch.append(dict(se_enabled=se,sound_request=ident,intercepted_calls=calls))
 ranges={'settings_ui':(0x8004eeb8,0x8004f5c8),'settings_apply':(0x800625c4,0x80062698),'sound_defaults':(0x80064d58,0x80064da4),'sound_dispatch':(0x80064e4c,0x80065000),'music_table':(0x80099864,0x80099874),'save_settings':(0x8006b8c0,0x8006b910),'load_settings':(0x8006bce4,0x8006bd34),'monthly_notice_gate':(0x80029e44,0x80029e78)}
 out('original-cases.json',dict(settings_application=cases,sound_dispatch=dispatch,original_entries=6,gameplay_updates=0,actual_audio=False))
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in ranges.items()}))
 out('runtime-rules.json',dict(packed_address='0x800CD898',se=dict(disable_mask=1,runtime='0x800CD834',save_body_offset='0x36'),monthly_report=dict(disable_mask=2,runtime='0x800CD835',save_body_offset='0x38'),bgm=dict(ui_values=[1,2,3],packed_values=[0,256,512],runtime='0x800CD8A9',save_body_offset='0x35',table='0x80099864',table_i32=tracks,selected_requests=tracks[1:4]),known_reused=['save_codec.py byte positions','sound backend and existing sample decoding'],new_scope='settings UI representation -> runtime switch -> playback dispatch / existing save fields',android_updated=False))
 # Keep focused disassembly, no bulk logs or copyrighted executable copy.
 asm=Path(sys.argv[2]).read_text().splitlines()
 (ROOT/'settings-readers.asm').write_text('\n'.join(line.rstrip() for line in asm if any(a<=int(line[:8],16)<b for a,b in ranges.values()) and line[:8].isalnum())+'\n')
 print('6 bounded original entries passed; no playback or gameplay execution')
if __name__=='__main__':main(sys.argv[1])
