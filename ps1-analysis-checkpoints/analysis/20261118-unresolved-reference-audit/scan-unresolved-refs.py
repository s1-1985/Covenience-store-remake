#!/usr/bin/env python3
"""Three static searches: staff field refs, FFFF/clock leads, product26 branches.
Candidate indexes, not proof of whole-program nonuse. Standard Python only.
"""
import argparse,hashlib,json,struct,zipfile
from collections import deque,Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MEM={32:'lb',33:'lh',35:'lw',36:'lbu',37:'lhu',40:'sb',41:'sh',43:'sw'}
LOAD={32,33,35,36,37};WIDTH={32:1,33:2,35:4,36:1,37:2,40:1,41:2,43:4}
def sha(b):return hashlib.sha256(b).hexdigest()
def put(n,v):(ROOT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def main():
 ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);args=ap.parse_args()
 expected=json.loads((ROOT.parent.parent/'archives/20261103-r2/manifest.json').read_text())['sha256'];assert sha(args.archive.read_bytes())==expected
 with zipfile.ZipFile(args.archive) as z:exe=z.read('algorithm-analysis/source/SLPS_007.82')
 assert sha(exe)=='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
 base,length=struct.unpack_from('<II',exe,0x18);data=exe[2048:2048+length];words=struct.unpack('<'+'I'*(len(data)//4),data[:len(data)//4*4])
 def d(i):
  w=words[i];return dict(pc=base+i*4,w=w,op=w>>26,rs=w>>21&31,rt=w>>16&31,rd=w>>11&31,fn=w&63,imm=w&65535,si=struct.unpack('<h',struct.pack('<H',w&65535))[0])
 def near(i,n=5):return dict(start=hex(base+max(0,i-n)*4),words=[hex(w) for w in words[max(0,i-n):i+n+1]])
 lo=0x80143ff8;hi=lo+35*60;refs=[]
 # Same canonical address inventory used for project master, now targeting
 # the full staff range rather than lexical '+16' or a few native calls.
 for i in range(len(words)):
  x=d(i)
  if x['op'] not in {9,13,*MEM}:continue
  for j in range(i-1,max(-1,i-9),-1):
   y=d(j)
   if y['op']==15 and y['rt']==x['rs']:
    target=((y['imm']<<16)|x['imm']) if x['op']==13 else ((y['imm']<<16)+x['si'])&0xffffffff
    if lo<=target<hi:refs.append(dict(pc=hex(x['pc']),index=i,word=hex(x['w']),target=hex(target),target_record=(target-lo)//60,target_field=(target-lo)%60,operation=MEM.get(x['op'],{9:'addiu',13:'ori'}.get(x['op'])),register=x['rt'],lui_pc=hex(y['pc']),context=near(i)))
    break
 # Bounded linear pointer following with compiler frame spill/reload support.
 # At non-copy indexed adds, retain base-relative displacement only as a lead.
 # Stop before every control transfer; no CFG or interprocedural claim.
 uses={};escapes=[]
 for seed in refs:
  if seed['operation'] not in ['addiu','ori']:continue
  tags={seed['register']:(seed['target_field'],False)};slots={}
  for i in range(seed['index']+1,min(len(words),seed['index']+129)):
   x=d(i);op=x['op'];rs=x['rs'];rt=x['rt'];rd=x['rd'];fn=x['fn']
   if op in [1,2,3,4,5,6,7] or op==0 and fn in [8,9]:
    if op==3:escapes.append(dict(seed=seed['pc'],pc=hex(x['pc']),kind='call_boundary',target=hex((x['pc']&0xf0000000)|((x['w']&0x3ffffff)<<2)),tagged_arguments={str(r):dict(field_mod60=tags[r][0]%60,opaque_index_add=tags[r][1]) for r in [4,5,6,7] if r in tags}))
    break
   if op in MEM:
    if rs in tags:
     off,indexed=tags[rs];field=(off+x['si'])%60
     key=hex(x['pc']);uses[key]=dict(pc=key,word=hex(x['w']),operation=MEM[op],field_mod60=field,width=WIDTH[op],opaque_index_add=indexed,seed=seed['pc'])
    if rs in [29,30]:
     if op==43:
      if rt in tags:slots[(rs,x['si'])]=tags[rt]
      else:slots.pop((rs,x['si']),None)
     elif op in [40,41]:slots.pop((rs,x['si']),None)
    old=slots.get((rs,x['si'])) if op==35 and rs in [29,30] else None
    if op in LOAD:
     tags.pop(rt,None)
     if old is not None:tags[rt]=old
   elif op in [8,9]:
    old=tags.get(rs);tags.pop(rt,None)
    if old is not None:tags[rt]=(old[0]+x['si'],old[1])
   elif op==0:
    val=None
    if fn in [33,37]:
     if rs in tags and rt==0:val=tags[rs]
     elif rt in tags and rs==0:val=tags[rt]
     elif fn==33 and (rs in tags)!=(rt in tags):
      a=tags.get(rs,tags.get(rt));val=(a[0],True)
    if fn not in [16,17,18,19,24,25,26,27]:tags.pop(rd,None)
    if val is not None:tags[rd]=val
   else:tags.pop(rt,None)
   tags.pop(0,None)
   if not tags and not slots:break
 direct=[dict(pc=r['pc'],operation=r['operation'],field_mod60=r['target_field'],target=r['target'],kind='canonical_memory_operand') for r in refs if r['operation'] in MEM.values()]
 word16=[u for u in uses.values() if u['field_mod60']<20 and u['field_mod60']+u['width']>16]
 # Literal leads only: no presumption that a literal -1 is a staff flag.
 literals={hex(a):[hex(base+i) for i in range(0,len(data)-3,4) if struct.unpack_from('<I',data,i)[0]==a] for a in [lo,lo+27*60,lo+27*60+16]}
 clock_pairs=[];special_branches=[];cash=[]
 for i in range(len(words)):
  x=d(i)
  if x['op']==15 and x['imm']==1:
   for k in range(i+1,min(i+9,len(words))):
    y=d(k)
    if y['op'] in [9,13] and y['rs']==x['rt'] and y['imm']==0xe00:
     clock_pairs.append(dict(pc=hex(y['pc']),context=near(k),scope='69120 constant candidate; register clobber/data not excluded'))
  if x['op'] in [9,13] and x['rs']==0 and x['imm'] in [0xffff,0x1a]:
   for k in range(i+1,min(i+5,len(words))):
    y=d(k)
    if y['op'] in [4,5] and x['rt'] in [y['rs'],y['rt']]:
     row=dict(constant_pc=hex(x['pc']),branch_pc=hex(y['pc']),constant=x['si'] if x['op']==9 else x['imm'],branch_target=hex(y['pc']+4+(y['si']<<2)),context=near(i))
     if x['imm']==0x1a:cash.append(row)
     elif any(int(r['pc'],16)<=x['pc']<int(r['pc'],16)+128 for r in refs):special_branches.append(row)
     break
 # Preserve all matches; domain classification is an explicit manual layer.
 put('staff-reference-index.json',dict(canonical_references=[{k:v for k,v in r.items() if k not in ['index','context']} for r in refs],direct_memory_references=direct,bounded_pointer_accesses=sorted(uses.values(),key=lambda x:x['pc']),bounded_word16_candidates=word16,pointer_call_boundaries=escapes,near_staff_minus1_comparisons=special_branches,literal_references=literals,limitations=['LUI/low within8instructions; includes data and does not prove code reachability.','Pointer propagation <=128straight instructions; stops at control transfer. Opaque index adds are leads, not verified stride60.','Caller arguments, pointer aliases, loops and noncanonical or other loaded code not covered.']))
 put('clock-cash-reference-index.json',dict(clock69120_candidates=clock_pairs,nearby_literal26_branches=cash,limitations=['Immediate26 canbe a row count or a different enum; manual domain classification required.','No proof of absent computed comparisons, indirect events or other modules.']))
 put('source-provenance.json',dict(exe_sha256=sha(exe),archive_sha256=expected,scan_payload_start=hex(base),scan_payload_bytes=len(data),original_cpu_calls=0,original_operating_updates=0))
 print(json.dumps(dict(staff_refs=len(refs),direct=len(direct),bounded_uses=len(uses),word16=word16,minus1=len(special_branches),clock69120=len(clock_pairs),literal26=len(cash))))
if __name__=='__main__':main()
