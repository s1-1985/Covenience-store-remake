#!/usr/bin/env python3
"""Static packed TOWN staff data, original UI labels and staff growth contracts.
No emulation, game-day continuation or synthetic candidate-sampling tests.
"""
import argparse,collections,hashlib,json,runpy,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
FIELDS=[(0,2),(2,1),(3,1),(4,1),(6,2),(8,2),(12,4),(16,4),(20,4)]+[(a,1) for a in range(24,47)]+[(47,10)]
NAMES={24:'maximum_energy',25:'current_energy',26:'education',27:'agility',28:'sociability',29:'academic_background',30:'cashier',31:'restocking',32:'customer_service',33:'cleaning',34:'security',35:'cashier_soft_limit',36:'restocking_soft_limit',37:'customer_service_soft_limit',38:'cleaning_soft_limit',39:'security_soft_limit'}
def sha(b):return hashlib.sha256(b).hexdigest()
def js(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args();raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'));files,read=lib['iso'](raw);by={r['path']:r for r in files}
    def payload(name):r=by[name];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    decode=runpy.run_path(str(ROOT/'source-reference/psmoji.py'))['decode']
    msg_path=next(name for name in by if name.endswith('/MSG00.OBJ'));msg=payload(msg_path)
    def words_until_end(data,pos):
        out=[]
        while True:
            v=struct.unpack_from('<H',data,pos)[0];out.append(v);pos+=2
            if v==0x40ff:return out
    labels=[]
    for a in [0x800b9654,0x800b96b0,0x800b9670,0x800b967c]:
        codes=words_until_end(exe,a-0x80010000+2048);labels.append(dict(address=hex(a),codes=codes,text=decode(codes)))
    assert labels[0]['text']=='体力{4002}学歴{4002}敏捷性{4002}社交性'
    assert labels[1]['text']=='体力{4002}教育{4002}レジ{4002}補充{4002}警備{4002}清掃{4002}接客'
    name_rows=[]
    for i in range(35):
        pos=struct.unpack_from('<I',msg,(150+i)*4)[0];codes=words_until_end(msg,pos);name_rows.append(dict(id=i,message_index=150+i,source_offset=pos,codes=codes,name=decode(codes)))
    js('ui-label-evidence.json',dict(source_exe_sha256=EXE_SHA,inline_labels=labels,name_source=msg_path,name_source_sha256=sha(msg),staff_names=name_rows,candidate_rows=[dict(label=l,offset=o,profile_dy=dy) for l,o,dy in [('体力',25,64),('学歴',29,80),('敏捷性',27,96),('社交性',28,112)]],transfer_rows=[dict(label=l,offset=o,profile_dy=dy) for l,o,dy in [('体力',25,48),('教育',26,64),('レジ',30,80),('補充',31,96),('警備',34,112),('清掃',33,128),('接客',32,144)]],glyph_reference='Reused prior by-eye PSMOJI0/1 transcription from repository tools/ps1/psmoji.py. This work decodes fresh source words; it does not claim new font OCR.'))
    packed_offset=0;field_map=[]
    for off,n in FIELDS:field_map.append(dict(packed_offset=packed_offset,runtime_offset=off,bytes=n));packed_offset+=n
    assert packed_offset==54
    (ROOT/'source').mkdir(exist_ok=True);profiles=None;maps=[];sources=[]
    for mapname in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
        data=payload('/DAT/'+mapname+'.BIN');pool=data[24017:24017+35*54];assert len(pool)==1890
        (ROOT/'source'/f'{mapname}-staff-packed.bin').write_bytes(pool);sources.append(dict(file='/DAT/'+mapname+'.BIN',file_sha256=sha(data),staff_offset=24017,bytes=len(pool),staff_sha256=sha(pool)))
        personal=[];states=[]
        for i in range(35):
            rec=bytearray(60);packed=pool[i*54:(i+1)*54]
            for f in field_map:rec[f['runtime_offset']:f['runtime_offset']+f['bytes']]=packed[f['packed_offset']:f['packed_offset']+f['bytes']]
            assert b''.join(rec[f['runtime_offset']:f['runtime_offset']+f['bytes']] for f in field_map)==packed
            sb=lambda off:struct.unpack_from('<b',rec,off)[0];owner=struct.unpack_from('<H',rec)[0];nameidx=sb(2);assert nameidx==i
            personal.append(dict(id=i,name=name_rows[nameidx]['name'],name_index=nameidx,age=sb(3),sex_code=sb(4),portrait=struct.unpack_from('<h',rec,8)[0],wage_base=struct.unpack_from('<i',rec,12)[0],initial_attributes={NAMES[k]:sb(k) for k in NAMES}))
            states.append(dict(id=i,owner_flags=owner,hire_pool_eligible=owner==0,initial_body_appearance=struct.unpack_from('<h',rec,6)[0],raw_word16=struct.unpack_from('<i',rec,16)[0],employment_experience_counter=struct.unpack_from('<i',rec,20)[0],task=sb(40),position=[sb(j) for j in (41,42,43)],goal=[sb(j) for j in (44,45,46)],route=list(rec[47:57])))
        if profiles is None:profiles=personal
        else:assert personal==profiles
        stores=[]
        for i in range(10):
            b=data[25907+i*5080:25907+(i+1)*5080]
            if b[0]:stores.append(dict(physical_slot=i,flags=struct.unpack_from('<H',b,4)[0],staff_ids=list(struct.unpack_from('<3h',b,0xdd8)),annual_wage_rate=struct.unpack_from('<i',b,0x12dc)[0]))
        referenced={j for s in stores for j in s['staff_ids'] if j!=-1}
        for s in stores:
            for sid in s['staff_ids']:
                if sid!=-1:assert states[sid]['owner_flags']==s['flags']
        maps.append(dict(map=mapname,free_count=sum(s['hire_pool_eligible'] for s in states),free_staff_ids=[s['id'] for s in states if s['hire_pool_eligible']],nonfree_without_active_store_reference=[s['id'] for s in states if s['owner_flags']!=0 and s['id'] not in referenced],active_stores=stores,staff_states=states))
    assert [m['free_count'] for m in maps]==[29,26,32,23]
    assert maps[3]['nonfree_without_active_store_reference']==[27]
    js('staff-roster-data.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,sources=sources,packed_schema=dict(staff_count_per_map=35,packed_record_bytes=54,runtime_record_bytes=60,field_map=field_map,unwritten_padding=[5,10,11,57,58,59],padding_note='Canonical decode here uses zero scratch bytes for padding; original loader does not write these holes. They are not source-defined fields.'),shared_initial_profiles=profiles,maps=maps,scope='35 shared initial profiles, with140 map-specific states. Skills/age/wage are mutable during gameplay; do not share one mutable prototype between sessions.'))
    roles=list(at(0x800cd758,6));assert roles==[42,43,38,40,39,41] and roles==list(at(0x800cd6f4,6));offsets=[list(struct.unpack('<2i',at(0x800997c8+i*8,8))) for i in range(3)]
    js('android-staff-roster-bridge.json',dict(schema_version=1,fields={str(k):v for k,v in NAMES.items()},ui_name_correction={'0x1d':'学歴; earlier reports used inferred name指導力 for this same byte. Manager academic value really is used in growth/advice rolls.','0x20':'接客; this current skill is also used in replenishment target threshold.','0x1a':'教育, also the hard limit for current cashier/security growth.'},candidates='Scan35 records, eligible only if u16 owner_flags==0. Choose up to10 with rejection sampling over the original free-list length; used entries become-1 and repeated draws consume RNG.',required_manager='Staffing commit refuses an empty first slot. Transfer final validation checks first slots; native writes are not a generic transactional rollback.',roles=[dict(slot=i,male=roles[2*i],female=roles[2*i+1],rest_offset=offsets[i]) for i in range(3)],hiring_commit='New assignment sets owner flags, role/sex body appearance, state0 and coordinates-1 before native rest placement; increments experience counter+20. Original unassigned look is not the hired role sprite.',growth=dict(manager_input='academic background+0x1d of store slot0 employee',rare='Draw rand()%16 once at function entry. Zero permits crossing soft limits for this call, but never the hard limit.',per_attribute='Always draw roll before comparing current<hard and(current<soft or rare); increment by1 if roll1..100<=manager academic value and both bounds permit.',modes={'1':[{'skill':30,'hard':26,'soft':35},{'skill':32,'hard':28,'soft':37}],'2':[{'skill':31,'hard':27,'soft':36},{'skill':34,'hard':26,'soft':39},{'skill':33,'hard':28,'soft':38,'extra_condition':'cleanliness summary>=100'}],'4':[{'skill':33,'hard':28,'soft':38},{'skill':34,'hard':26,'soft':39}]},minus1='Reduce cashier30,restocking31,cleaning33,security34 by1 only when>=2; customer_service32 is not reduced by this mode.'),energy=dict(active='If energy>0, one rand()&3==0 decrements it. Exhaustion clears non-rest-travel goals and sets flag0x1000; rest-travel state3 can keep its goal.',room48='Below maximum, one rand()&1==0 recovers1.',room49='Below maximum, recovers1 without RNG.',resume='Once full, resting slot is eligible to choose work only when (clock//2)%3==slot. These are update rules, not measured seconds.'),annual=dict(gate='Finance close at stage1/month1 and minute0/hour0',age='All35 records age by1 if signed age<127, including unassigned records. Age>=80 rolls rand()%5==0 for basic-trait boost; age127 guarantees it.',boost='Set maximum energy24,education26,agility27,sociability28,academic29 to100. Does not directly set current energy or five current work skills to100.',wage='Per active store assigned staff: wage=trunc((store+12dc+100)*wage/100). Free records outside assignments do not receive that per-store multiplication.'),wage_display='Transfer profile displays wage_base*scheduled_hours; actual payroll separately applies130% to slot0 before hours. Do not conflate UI amount with charged manager amount.'))
    js('summary.json',dict(person_profiles=35,map_staff_states=140,free_by_map={m['map']:m['free_count'] for m in maps},initial_age_range=[min(p['age'] for p in profiles),max(p['age'] for p in profiles)],initial_wage_range=[min(p['wage_base'] for p in profiles),max(p['wage_base'] for p in profiles)],source_label_corrections={'29':'学歴','32':'接客','26':'教育'},new_work='Full54-byte staff records to60-byte runtime fields; shared35 named personal profiles plus140 ownership/role states; source UI labels resolve academic/customer-service fields and connect to growth/rest/payroll.',known_before='Isolated candidate, growth, rest and commit algorithms were reconstructed earlier.',unresolved='Purpose of TOWNPS ownerFFFF for staff27; raw word16 remains unlabeled.',original_cpu_updates=0))
    spans=[('town_loader',0x8001a0b8,0x8001b0a4),('candidate_pool',0x8006f8bc,0x8006fae0),('hire_shell',0x8006fae0,0x8006fd68),('candidate_profile',0x800703e4,0x80070f48),('hire_commit',0x80070f48,0x80071384),('transfer_label_panel',0x80072f20,0x80073100),('transfer_profile_left',0x80073100,0x80074150),('growth',0x8003aa58,0x8003b278),('rest_entry',0x8003dda8,0x8003e130),('rest_energy',0x80036e10,0x80036f30),('active_energy',0x800370ec,0x800371a8),('finance_close',0x80029334,0x8002a8e0)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];manifest=[]
    for name,a,end in spans:
        b=at(a,end-a);(ROOT/'source'/f'{name}.bin').write_bytes(b);manifest.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)));asm.append(f'\n# {name} {a:#x}..{end:#x}');asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(b,a))
    (ROOT/'source/inline-ui-labels.bin').write_bytes(at(0x800b9654,0x800b96da-0x800b9654));manifest.append(dict(name='inline_ui_labels',address='0x800b9654',bytes=0x86,sha256=sha(at(0x800b9654,0x86))))
    table=at(0x800cd750,14);(ROOT/'source/display-hours-and-role-table.bin').write_bytes(table);manifest.append(dict(name='display_hours_and_roles',address='0x800cd750',bytes=len(table),sha256=sha(table)))
    (ROOT/'staff-readers.asm').write_text('\n'.join(asm)+'\n');js('source-ranges.json',manifest)
    js('source-derived-examples.json',dict(scope='Source arithmetic examples, not gameplay observations.',soft_limit=dict(initial_profile=0,cashier_hard_limit=80,cashier_soft_limit=52,at51='Can grow to52 when academic roll passes.',at52='Needs shared rare flag and academic roll to grow to53.',at80='Cannot grow beyond hard limit even with rare flag.'),wage=dict(profile=0,base=280,hours=24,profile_display=6720,manager_hourly=364,manager_payroll=8736,after3_percent_annual_raise_base=288,unassigned_record='No per-store annual wage multiplication while unassigned.')))
    print(json.dumps(dict(profiles=35,states=140,free_by_map={m['map']:m['free_count'] for m in maps}),ensure_ascii=False))
if __name__=='__main__':main()
