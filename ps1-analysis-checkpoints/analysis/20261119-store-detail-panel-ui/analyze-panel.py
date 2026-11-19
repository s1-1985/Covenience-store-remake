#!/usr/bin/env python3
"""Original store-detail reader; capture visual calls, keep metric callees native."""
import argparse,hashlib,importlib.util,json,runpy,struct,zipfile
from pathlib import Path
from unicorn import UC_HOOK_CODE
from unicorn.mips_const import *
ROOT=Path(__file__).resolve().parent;HELPER=ROOT.parent/'20261117-festival-customer-state-data/analyze-festival-state.py'
spec=importlib.util.spec_from_file_location('machine_helper',HELPER);P=importlib.util.module_from_spec(spec);spec.loader.exec_module(P)
def sha(b):return hashlib.sha256(b).hexdigest()
def save(n,d):(ROOT/n).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def rd(u,a,n):return bytes(u.mem_read(a&0x1fffffff,n))
def word(u,a):return struct.unpack('<I',rd(u,a,4))[0]
def signed16(v):v&=65535;return v-65536 if v>=32768 else v

def main(archive):
 z=zipfile.ZipFile(archive);exe=z.read('algorithm-analysis/source/SLPS_007.82');town=z.read('algorithm-analysis/source/TOWN0001.BIN');msg=z.read('algorithm-analysis/source/MSG00.OBJ');assert sha(exe)==P.EXE_SHA
 base,_=P.fixture(exe,town);cases=[]
 visuals={0x80018940:'draw_group',0x80017b18:'panel_frame',0x800157b4:'restore_display',0x8004e494:'message',0x800419e0:'icon_group_setup',0x80043a80:'permit_icon'}
 inputs=[(19,1,0,[0,0,0]),(20,2,2,[1,1,1]),(99,0x8001,6,[1,0,1]),(100,0x8002,3,[0,1,0])]
 for rating,flags,schedule,permits in inputs:
  u=P.machine(exe,base);s=P.S+2*5080;assert rd(u,s,1)!=b"\0"
  u.mem_write(s+4,struct.pack('<H',flags));P.put(u,s+0xc68,rating);P.put(u,s+0xc6c,73);P.put(u,s+0xc78,schedule);u.mem_write(s+0xc74,bytes(permits))
  P.put(u,s+0xd48,987654);P.put(u,s+0xd5c,1234567)
  before=rd(u,s,5080);draws=[];metrics=[]
  def code(uc,pc,n,c):
   if pc in [0x8002287c,0x800224e0,0x800221d0]:metrics.append({'entry':hex(pc),'store_arg':hex(uc.reg_read(UC_MIPS_REG_A0))})
   if pc in visuals:
    args=[uc.reg_read(r) for r in [UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3]]
    d={'kind':visuals[pc],'pc':hex(pc),'args':args}
    if pc==0x8004e494:
     d={'kind':'message','x':signed16(args[0]),'y':signed16(args[1]),'message':args[2],'numeric_slot_u32':word(uc,0xcd938),'money_slot_u32':word(uc,0xe4000),'star_repeat_i16':signed16(word(uc,0xcd8e4)>>16)}
    elif pc==0x80043a80:d={'kind':'permit_icon','x':signed16(args[0]),'y':signed16(args[1]),'icon':args[2]}
    draws.append(d);uc.reg_write(UC_MIPS_REG_PC,uc.reg_read(UC_MIPS_REG_RA))
  h=u.hook_add(UC_HOOK_CODE,code)
  x,y=184,8
  for r,v in [(UC_MIPS_REG_A0,x),(UC_MIPS_REG_A1,y),(UC_MIPS_REG_A2,s+0x80000000)]:u.reg_write(r,v)
  P.call(u,0x8004d8c8);u.hook_del(h)
  texts=[a for a in draws if a['kind']=='message'];icons=[a for a in draws if a['kind']=='permit_icon']
  assert rd(u,s,5080)==before
  star=next(a for a in texts if a['message']==310);assert star['star_repeat_i16']==rating//20 and (star['x'],star['y'])==(x+16,y+112)
  money=next(a for a in texts if a['message']==302);assert money['money_slot_u32']==1234567 and money['money_slot_u32']!=word(u,s+0xd48)
  assert any(a['message']==303+schedule for a in texts)
  assert icons==[{'kind':'permit_icon','x':x+60+16*j,'y':y+32,'icon':j+1} for j,v in enumerate(permits) if v]
  assert texts[0]['message']==(384 if not flags&0x8000 else 362+rd(u,0xcd948,1)[0])
  assert any(a['message']==(12 if flags&127==1 else 366) and a['y']==y+32 for a in texts)
  assert [m['entry'] for m in metrics]==['0x8002287c','0x800224e0','0x800221d0']
  values=[a['numeric_slot_u32'] for a in texts if a['message']==369]
  assert len(values)==4 and values[0]==73
  cases.append({'input':{'rating':rating,'flags':flags,'schedule':schedule,'permits':permits,'current_month_sales':987654,'previous_month_sales':1234567,'popularity':73,'origin':[x,y]},'captured_visual_calls':draws,'native_metric_entries':metrics,'display_values':{'stars':star['star_repeat_i16'],'money':money['money_slot_u32'],'popularity_clean_security_service':values},'store_record_unchanged':True})
 save('original-cases.json',{'leaf':'0x8004d8c8..0x8004dfac','cases':cases,'original_top_level_entries':{'existing_bootstrap':3,'detail_reader':4,'total':7},'nested_native_metric_calls':12,'visual_callee_intercepts':{hex(a):n for a,n in visuals.items()},'gameplay_callee_replacements':0,'operating_updates':0,'scope':'Four controlled display inputs; native metric calculations are not newly verified formulas. Visual/text calls captured, not actual GPU/glyph/audio rendering or complete menu/input execution.'})
 dec=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode'];labels=[]
 ids=sorted({a['message'] for c in cases for a in c['captured_visual_calls'] if a['kind']=='message'}|set(range(303,310)))
 for mid in ids:
  off=struct.unpack_from('<I',msg,mid*4)[0];cs=[]
  while True:
   c=struct.unpack_from('<H',msg,off+2*len(cs))[0];cs.append(c)
   if c==0x40ff:break
   assert len(cs)<200
  labels.append({'message_id':mid,'source_offset':off,'codes':cs,'decoded_template':dec(cs),'sha256':sha(msg[off:off+len(cs)*2])})
 save('message-templates.json',{'source':'MSG00.OBJ','source_sha256':sha(msg),'rows':labels,'note':'Control tokens preserved as {40xx}; raw control words and glyphs retained, not guessed plain text.'})
 rules={'reader':'0x8004d8c8','origin':'signed16 x,y arguments; all positions below are relative logical coordinates','header':{'own_company_message':384,'rival_company_message':'362+signed byte CD948','company_xy':[16,16],'store_number':'flags4 low7 bits; serial1 -> MSG12 本店, otherwise MSG366 with numeric slot','store_xy':[16,32]},'money':{'field':'store+D5C previous-month revenue','message':302,'xy':[16,48],'not':'store+D48 current month or company cash'},'hours':{'field':'store+C78','message':'303+schedule0..6','xy':[16,80]},'rating':{'field':'signed32 store+C68','star_repeat':'trunc(value/20), written to signed16 CD8E6','message':310,'xy':[16,112],'scope':'Normal0..100 gives0..5. Reader has no separate explicit clamp; no malformed-value display claim.'},'numeric_rows':[{'label':'人気','label_message':311,'value':'store+C6C','y':128},{'label':'清掃','label_message':312,'value':'native2287C(store)','y':144},{'label':'警備','label_message':313,'value':'native224E0(store)','y':160},{'label':'サービス','label_message':314,'value':'native221D0(store)','y':176}],'numeric_row_x':{'label':16,'value':80},'numeric_message':369,'permits':[{'field':'C74','icon':1,'label':'たばこ','xy':[60,32]},{'field':'C75','icon':2,'label':'酒類','xy':[76,32]},{'field':'C76','icon':3,'label':'薬品','xy':[92,32]}],'permit_rule':'Each signed byte !=0 shows its own fixed icon; no compacting gaps or treating all three as one boolean.','known_reused':['source finance monthly history','cleaning/security/service metrics','permit fields and icon identities','company/store flags and source text decoder'],'apk_updated':False}
 save('panel-rules.json',rules)
 spans=[('panel_reader',0x8004d8c8,0x8004dfac),('permit_icon_renderer',0x80043a80,0x80043cd0)]
 save('source-provenance.json',{'exe_sha256':sha(exe),'town_sha256':sha(town),'msg_sha256':sha(msg),'archive_sha256':sha(archive.read_bytes()),'helper_sha256':sha(HELPER.read_bytes()),'ranges':[{'name':n,'start':hex(a),'end_exclusive':hex(b),'sha256':sha(exe[a-0x80010000+2048:b-0x80010000+2048])} for n,a,b in spans],'reuse_audit_scope':'Small prior reports/models and r2 source-reference; no exhaustive large snapshot-log audit.','paused_issues_touched':False})
 print(json.dumps({'detail_calls':4,'stars':[c['display_values']['stars'] for c in cases],'metric_values':[c['display_values']['popularity_clean_security_service'] for c in cases],'store_mutations':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);main(ap.parse_args().archive)
