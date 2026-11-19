#!/usr/bin/env python3
"""Ordinary admission sound audit; no festival/unresolved-path execution."""
import hashlib,importlib.util,json,struct,sys,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('helper',ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py');P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
S=P.S+2*5080;FLAGS=0xcd790
entries=[]
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def out(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def block(u,start,end,frame=None,args=()):
 f=P.SP if frame is None else frame
 for r,v in [(UC_MIPS_REG_SP,f),(UC_MIPS_REG_FP,f),(UC_MIPS_REG_RA,P.STOP)]:u.reg_write(r,v)
 for r,v in zip((UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3),args):u.reg_write(r,v)
 def stop(uc,pc,n,c):uc.emu_stop()
 h=u.hook_add(UC_HOOK_CODE,stop,begin=end,end=end)
 u.emu_start(start,P.STOP,count=3000000);u.hook_del(h);assert u.reg_read(UC_MIPS_REG_PC)==end
 entries.append(dict(start=hex(start),stop=hex(end)))
def main(archive,asmfile,androidroot):
 z=zipfile.ZipFile(archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWN0001.BIN');assert hashlib.sha256(exe).hexdigest()==P.EXE_SHA
 baseline,initial=P.fixture(exe,town);u=P.machine(exe,baseline)
 for slot in [1,2]:P.put(u,P.S+5080*slot+0xc78,0)
 P.put(u,0xcd93c,44640);P.call(u,0x80023c20);P.put(u,0xd6270,2);P.call(u,0x8002619c)
 assert P.get(u,0xcda00)==0 and rd(u,S+0xf04,32)==bytes(32)
 P.put(u,0xcd8ec,2);u.mem_write(0x1398bc,b'\1');f=P.SP-0x40;P.put(u,f+0x24,S+0x80000000);P.put(u,f+0x18,0)
 block(u,0x80023670,0x800238ac,f)
 u.mem_write(FLAGS,b'\0\0');P.put(u,0xd6270,0);writes=[];dispatch=[]
 def memory(uc,access,a,n,v,c):
  a&=0x1fffffff
  if a<FLAGS+2 and a+n>FLAGS:writes.append(dict(pc=hex(uc.reg_read(UC_MIPS_REG_PC)),value=v&65535))
 def audio(uc,pc,n,c):
  if pc==0x80064e4c:dispatch.append(uc.reg_read(UC_MIPS_REG_A0));raise AssertionError('unexpected direct audio request')
 h=u.hook_add(UC_HOOK_MEM_WRITE,memory);c=u.hook_add(UC_HOOK_CODE,audio)
 block(u,0x800319ac,0x80032814,args=[S+0x80000000]);b=rd(u,S+0xf04,32)
 assert (b[0],struct.unpack_from('<h',b,2)[0],b[30])==(1,60,2)
 steps=[]
 for seed in range(4):
  if rd(u,S+0xf04,1)[0]!=1:break
  P.put(u,0xd6270,seed);f=P.SP-0x58;P.put(u,f+0x58,S+0x80000000);P.put(u,f+0x54,P.STOP);P.put(u,f+0x50,P.SP)
  block(u,0x80032814,P.STOP,f);steps.append(dict(seed=seed,state=rd(u,S+0xf04,1)[0],flags=struct.unpack('<H',rd(u,FLAGS,2))[0]))
 u.hook_del(h);u.hook_del(c)
 assert steps[-1]['state']==2 and writes==[] and dispatch==[]
 normal=dict(profile=60,quantity=2,steps=steps,sound_flag_writes=writes,direct_audio_requests=dispatch,scope='Native ordinary spawn and pending-entry loop, flag0; calendar/schedules/RNG specified, no natural UI/playthrough.')
 # Isolate existing parking-capacity admission guard; preserve original comparison/flag writer.
 raw=lambda a,b:exe[a-0x80010000+2048:b-0x80010000+2048]
 eligible=[i for i in range(144) if struct.unpack('<b',raw(0x800a09d0+24*i+12,0x800a09d0+24*i+13))[0]==3]
 assert eligible;profile=eligible[0];caps=[]
 for capacity in [1,2]:
  u=P.machine(exe);P.put(u,0xcd8ec,2);P.put(u,0xcecec+2*2948,0x80160000);P.put(u,0x160010,capacity);P.put(u,0x160014,0)
  u.mem_write(S+0x12e3,b'\0');u.mem_write(S+0xde4+profile*2,struct.pack('<h',2));f=P.SP
  P.put(u,f+0x58,S+0x80000000);P.put(u,f+0x1c,profile);P.put(u,f+0x2c,2)
  block(u,0x80031c28,0x80031e3c,f)
  flags=struct.unpack('<H',rd(u,FLAGS,2))[0];assert flags==(64 if capacity==1 else 0)
  assert rd(u,S+0x12e3,1)[0]==(1 if capacity==1 else 0)
  caps.append(dict(profile=profile,type_byte=3,capacity=capacity,present=0,incoming=2,remaining_attempt_quantity=P.get(u,f+0x2c),sound_flags=flags,lost_counter=rd(u,S+0x12e3,1)[0],remaining_profile_demand=struct.unpack('<h',rd(u,S+0xde4+profile*2,2))[0]))
 # Original selected-store main audio dispatch for parking failure bit6; source playback captured.
 u=P.machine(exe);u.mem_write(FLAGS,b'\x40\0');u.mem_write(0xcd834,b'\1');P.put(u,0xce61c,2);f=P.SP;P.put(u,f+0x14,0);P.put(u,f+0x28,2);requests=[]
 def capture(uc,pc,n,c):
  if pc==0x80064e4c:requests.append(uc.reg_read(UC_MIPS_REG_A0));uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
 h=u.hook_add(UC_HOOK_CODE,capture);block(u,0x80023a14,0x80023bbc,f);u.hook_del(h)
 assert requests==[11] and rd(u,FLAGS,2)==b'\0\0'
 out('original-cases.json',dict(normal_admission=normal,parking_capacity_cases=caps,main_dispatch=dict(input_flags=64,requests=requests,final_flags=0),entry_log=entries,top_level_entries=len(entries),preparation_entries=0,prior_successful_output_pass_entries=6,setup_original_calls=['5C858','1A0B8','23C20','23C20','2619C'],ordinary_full_operating_updates=0,fixture_external_resource_substitution=True,visual_audio_playback=False))
 spans={'spawn':(0x800319ac,0x80032814),'entry_dispatch':(0x800329bc,0x80032abc),'entry_search':(0x800331b4,0x800340fc),'audio_dispatch':(0x80023a14,0x80023bbc),'flag_table':(0x8009947c,0x800994bc)}
 out('source-provenance.json',dict(exe_sha256=P.EXE_SHA,town_sha256=hashlib.sha256(town).hexdigest(),ranges={k:dict(start=hex(a),end_exclusive=hex(b),sha256=hashlib.sha256(raw(a,b)).hexdigest()) for k,(a,b) in spans.items()},sound_flag_table=list(struct.unpack('<16i',raw(0x8009947c,0x800994bc)))))
 lines=Path(asmfile).read_text().splitlines(); excerpts=[(0x80031c28,0x80031e3c),(0x800329bc,0x80032abc),(0x800331b4,0x80033238),(0x80023a14,0x80023bbc)];(ROOT/'admission-sound-readers.asm').write_text('\n'.join(x for x in lines if any(a<=int(x[:8],16)<b for a,b in excerpts) or (0x800331b4<=int(x[:8],16)<0x800340fc and 'jal ' in x))+'\n')
 a=Path(androidroot);config=json.loads((a/'game/data/vertical_slice.json').read_text());synth=(a/'game/scripts/audio/sound_synth.gd').read_text()
 assert config['sound']['event_sfx']['customer_entered']=='door_chime' and '"E6", 0.42' in synth
 out('android-sound-audit.json',dict(commit='22ba479999c4e025727806454b9858364ca145cc',event='customer_entered',alias='door_chime',source_id=None,legacy_synth=dict(notes=['E6','C6'],seconds=[0.42,0.9],octave_overtones=['E7','C7']),path=['main.gd::_play_event_sounds','SoundManager.play_sfx','SoundSynth.sfx_samples'],evidence='Explicit REMAKE_BALANCED_DEFAULT legacy synthesis; not recovered source door audio.',files={str(p):hashlib.sha256((a/p).read_bytes()).hexdigest() for p in ['game/data/vertical_slice.json','game/scripts/main.gd','game/scripts/audio/sound_manager.gd','game/scripts/audio/sound_synth.gd']},app_changed=False))
 print(json.dumps(dict(entries=len(entries),normal_flags=0,parking_failure_request=requests,normal_steps=steps)))
if __name__=='__main__':main(*sys.argv[1:])
