#!/usr/bin/env python3
"""Known validator results bound to original exit messages; no layout/gameplay retests."""
import hashlib,importlib.util,json,runpy,struct,sys,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helper',ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def out(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def main(exefile,asmfile,archive,androidroot):
 exe=Path(exefile).read_bytes();assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
 pointers=struct.unpack('<11I',raw(0x800b98a4,0x800b98d0))
 def text(p):
  codes=[]
  for i in range(200):
   c=struct.unpack('<H',raw(p+2*i,p+2*i+2))[0];codes.append(c)
   if c==0x40ff:break
  else:raise AssertionError('terminator')
  value=dec(codes);return dict(pointer=hex(p),codes=codes,text=value.replace('{4002}','\n'),line_break_control='0x4002',raw_sha256=hashlib.sha256(raw(p,p+2*len(codes))).hexdigest())
 conditions=['unlicensed_tobacco','unlicensed_alcohol','unlicensed_medicine','no_break_room','multiple_break_rooms','no_register','multiple_registers','no_usable_perimeter_entrance','register_sides_blocked','break_room_neighbors_blocked']
 rows=[dict(result=i,known_condition=conditions[i-1],**text(pointers[i])) for i in range(1,11)]
 cases=[]
 for reason in (0,8,9):
  u=P.machine(exe);f=P.SP;u.reg_write(UC_MIPS_REG_FP,f);u.reg_write(UC_MIPS_REG_SP,f);P.put(u,f+0x18,reason);P.put(u,f+0x1c,7);calls=[]
  def hook(uc,pc,n,c):
   if pc==0x8007620c:uc.emu_stop();return
   if pc in (0x80065080,0x80066c64):
    calls.append(dict(callee=hex(pc),a0=hex(uc.reg_read(UC_MIPS_REG_A0)) if pc==0x80066c64 else None));uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,hook);u.emu_start(0x800761b8,P.STOP,count=10000);u.hook_del(h)
  assert u.reg_read(UC_MIPS_REG_PC)==0x8007620c
  state=P.get(u,f+0x1c);assert state==(10 if reason==0 else 7)
  if reason==0:assert calls==[]
  else:assert calls==[dict(callee='0x80065080',a0=None),dict(callee='0x80066c64',a0=hex(pointers[reason]))]
  cases.append(dict(supplied_validator_result=reason,next_parent_state=state,calls=calls,validator_executed=False,dialog_executed=False))
 out('error-message-map.json',dict(rows=rows,success_result=0,index0_raw_word=hex(pointers[0]),index0_note='Not a valid message pointer; success branch bypasses table lookup.',exit_confirmation=text(0x800b98d0)))
 out('original-cases.json',dict(cases=cases,original_entries=3,operating_updates=0,actual_validator_calls=0,actual_dialog_calls=0,visual_audio_intercepts=2,scope='Only caller fragment761B8..7620C with staged result; no natural UI or layout reachability.'))
 z=zipfile.ZipFile(archive);out('reuse-audit.json',dict(known_files=[dict(path=n,sha256=hashlib.sha256(z.read(n)).hexdigest()) for n in ['algorithm-analysis/operation_validation.py','algorithm-analysis/category_parent_control.py']],known='Numeric failure rules and priority are already decoded, including post-map checks and parent state10. No new finding in validator mechanics.',new_result='Complete10 original multiline strings bound to return codes and current Android finish route; caller fragments only.'))
 a=Path(androidroot);out('android-differences.json',dict(commit='22ba479999c4e025727806454b9858364ca145cc',path='game/scripts/ps1_ui.gd',sha256=hashlib.sha256((a/'game/scripts/ps1_ui.gd').read_bytes()).hexdigest(),finish='match finish ->close_window()',close_window='clears screen/history/floor_mode, turns editing off; no788C8-equivalent check called in this UI route',required='On success continue exit confirmation; on nonzero keep editing and show original mapped reason. Reuse known validation/priority, not UI-only geometric guesses.',app_changed=False))
 ranges={'caller':(0x80076194,0x80076214),'early_validator':(0x80078bc8,0x80078c84),'message_table':(0x800b98a4,0x800b98d0),'messages':(0x800b9730,0x800b98a4)}
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in ranges.items()}))
 asm=Path(asmfile).read_text().splitlines();(ROOT/'exit-message-callers.asm').write_text('\n'.join(x.rstrip() for x in asm if any(a<=int(x[:8],16)<b for a,b in ranges.values()))+'\n')
 print('10 original messages extracted;3 caller fragments passed; validator/gameplay/dialog executions0')
if __name__=='__main__':main(*sys.argv[1:])
