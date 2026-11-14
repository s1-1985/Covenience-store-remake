#!/usr/bin/env python3
"""Original five advertising records, flags, payment and popularity data contracts."""
import argparse,hashlib,json,runpy,struct
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def write(name,x):(ROOT/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);args=ap.parse_args()
    raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    helper=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'))
    rows,read=helper['iso'](raw);files={r['path']:r for r in rows}
    def payload(p):r=files[p];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    decode=runpy.run_path(str(ROOT.parent/'20261114-staff-roster-growth-data/source-reference/psmoji.py'))['decode']
    msg=payload(next(k for k in files if k.endswith('/MSG00.OBJ')))
    def message(i):
        off=struct.unpack_from('<I',msg,i*4)[0];codes=[]
        for j in range(256):
            v=struct.unpack_from('<H',msg,off+2*j)[0];codes.append(v)
            if v==0x40ff:return dict(index=i,source_offset=off,codes=codes,text=decode(codes))
        raise AssertionError('no terminator')
    def inline(a):
        codes=[]
        for j in range(256):
            v=struct.unpack('<H',at(a+2*j,2))[0];codes.append(v)
            if v==0x40ff:return dict(address=hex(a),codes=codes,text=decode(codes))
        raise AssertionError('no terminator')
    (ROOT/'source').mkdir(exist_ok=True)
    promotions=[]
    for i in range(5):
        a=0x8009fe40+i*44;b=at(a,44);cost,variant,gain,stage,hour=struct.unpack_from('<5i',b,24)
        promotions.append(dict(id=i,address=hex(a),raw_hex=b.hex(),name=b[:24].split(b'\0',1)[0].decode('shift_jis'),menu_message=message(145+i),
            cost=cost,notification_variant=variant,popularity_gain=gain,trigger_stage=stage,trigger_hour=hour,
            player_required_cash=5*cost,rival_selection_required_cash=10*cost))
    assert [(x['cost'],x['popularity_gain'],x['trigger_stage'],x['trigger_hour']) for x in promotions]==[(100000,12,2,10),(500000,20,2,7),(1000000,40,3,15),(3000000,60,1,17),(5000000,90,1,19)]
    jump=list(struct.unpack('<6I',at(0x800108b0,24)))
    assert jump==[0x80028eb8,0x80028edc,0x80028f00,0x80028f24,0x80028f48,0x80028f68]
    delta=[]
    for i,a in enumerate(jump):
        instruction=struct.unpack('<I',at(a+0x14,4))[0]
        if i==4:
            assert instruction>>26==43 # store unchanged value, no addiu
            delta.append(0)
        else:
            assert instruction>>26==9 and instruction>>21&31==4 and instruction>>16&31==3
            delta.append(struct.unpack('<h',at(a+0x14,2))[0])
    assert delta==[-15,-10,-5,-3,0,5]
    decay=[dict(rating_band=i,rating_range=[20*i,min(100,20*i+19)],daily_midnight_delta=delta[i],branch=hex(jump[i])) for i in range(6)]
    combos=[]
    for mask in range(32):
        selected=[p for p in promotions if mask>>p['id']&1]
        combos.append(dict(mask=mask,flags=[mask>>i&1 for i in range(5)],selected_ids=[p['id'] for p in selected],menu_total=sum(p['cost'] for p in selected),raw_gain_sum=sum(p['popularity_gain'] for p in selected)))
    assert combos[-1]['menu_total']==9600000 and combos[-1]['raw_gain_sum']==222
    initial=[]
    for name in ['TOWN0001','TOWN0002','TOWN0003','TOWNPS']:
        b=payload('/DAT/'+name+'.BIN');stores=[]
        for i in range(10):
            s=b[25907+i*5080:25907+(i+1)*5080]
            if s[0]:stores.append(dict(slot=i,owner_flags=struct.unpack_from('<H',s,4)[0],rating=struct.unpack_from('<i',s,0xc68)[0],popularity=struct.unpack_from('<i',s,0xc6c)[0]))
        initial.append(dict(map=name,source_sha256=sha(b),stores=stores))
    write('advertising-data.json',dict(schema_version=1,source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,
        table_address='0x8009fe40',record_bytes=44,count=5,fields={'0':'Shift-JIS name24','24':'i32 cost','28':'i32 notification variant','32':'i32 popularity gain','36':'i32 stage','40':'i32 hour'},
        promotions=promotions,menu_combinations=combos,popularity_daily_delta=decay,initial_map_stores=initial,
        canonical_fields={'store+C68':'評価; MSG310, source UI renders trunc(value/20)','store+C6C':'人気; MSG311 aligned with numeric MSG369 fed fromC6C'},
        known_before='Prior guide/video-derived definitions held these five numeric rows. This work reads the original records and ties them to original menu, payments, persistent flags, company scope and decay implementation.'))
    write('ui-label-evidence.json',dict(messages=[message(i) for i in [145,146,147,148,149,203,204,205,310,311,369]],
        inline_notifications=[inline(a) for a in [0x80098d6c,0x80098d8c,0x80098da0,0x80098dc4]],
        popularity_evidence='8004dc50 loadsC6C into800cd938;8004dc8c drawsMSG369 at dy80;8004dcc8 drawsMSG311 at the same dy80. Label and numeric column differ in x.',
        decoding='Source16-bit words decoded with prior by-eye font transcription, no new OCR. Master names are source Shift-JIS.'))
    write('android-advertising-bridge.json',dict(schema_version=1,
        state=dict(player_flags='Five bytes800e3688..368c',rival_flags='Five bytes800e368d..3691',initialization='8001aee8..1aefc clears10 bytes together'),
        menu='80069bbc copies five player bytes to local buffer. Confirm input800 writes all5 back; cancel40 returns without writeback. Toggle20 changes local0/1 only. No cash debit or current-date rejection in these commit/toggle branches.',
        clock='275f8 returns unless minute0. Each promotion tests current stage and hour against its record. Month itself is not a record field.',
        recurring='Success does not clear player flag. It remains enabled for later matching months until menu disables it or insufficient-cash branch clears it. Enabling after its monthly time is not an immediate catch-up trigger.',
        player='At trigger require signed cash0>=5*cost. Success accumulates gain for owner0, charges cost once via1cbc4(store0,cost), queues kind4/variant/master28/sound100. Failure clears that player flag, no gain/debit, and queues cancellation sound31.',
        scope='Loop valid store-order entries. For each store add the gain accumulator selected by owner high bit toC6C, regardless of open/closed schedule state. Charge once per method/company, not per beneficiary store.',
        ledger='1cbc4 adds cost to company ledger800d8f68+16*side and subtracts it from company cash800cd9f8+4*side. The5x amount is a gate, not the debit.',
        rival='At stage1/hour0/minute0 consume rand()%4 and compare against signed control byte800cd8a8. If allowed, scan methods4..0 and set only the first whose10*cost<=rival cash; clear all other rival flags. At its trigger add owner1 gain, find first active rival in physical slots0..9, debit cost once and queue sound101, then break. No extra cash-adequacy check is present in that trigger path.',
        popularity='At minute0 add company gain. If hour0, add delta indexed by trunc(current ratingC68/20). Then floor popularity to current ratingC68, and cap100. Monthly rating changes earlier in the same routine are already applied.',
        ui_correction='C6C was left unnamed in the preceding incident/security reports; original UI identifies it as popularity人気. Keep it distinct from evaluationC68.',
        not_claimed=['Raw gain sum222 from all5 is not an immediate222-point effective gain; time, decay and cap apply.',
            'No per-day rival probability or natural advertising run newly measured.','No guide-only one-shot scheduling assumption overrides original persistent flags.']))
    write('source-derived-examples.json',dict(scope='Source arithmetic examples, not runtime observations.',
        direct_mail=[dict(cash_before=c,allowed=c>=500000,charge=100000 if c>=500000 else 0,cash_after=c-100000 if c>=500000 else c,flag_after=1 if c>=500000 else 0) for c in [499999,500000]],
        company_scope=dict(stores_before=[20,70],gain=12,after_gain_before_rating_floor_and_cap=[32,82],company_charge=100000,not_per_store_charge=200000),
        late_selection=dict(stage=1,hour=20,selected_method=4,next_matching_stage=1,next_matching_hour=19,note='On following monthly cycle, provided flag persists and cash gate passes; no immediate catch-up.'),
        popularity_update=[dict(before=p,rating=r,hour=h,gain=g,delta=delta[r//20] if h==0 else 0,after=min(100,max(r,p+g+(delta[r//20] if h==0 else 0)))) for p,r,h,g in [(95,40,0,0),(50,60,0,0),(5,60,1,0),(95,60,10,12)]]))
    spans=[('advertising_and_popularity',0x800275f8,0x80029020),('advertising_menu',0x80069bbc,0x8006a304),
        ('popularity_ui',0x8004dbdc,0x8004dcd4),('company_payment',0x8001cbc4,0x8001ccc0),('flags_initialize',0x8001aee8,0x8001af00)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];ranges=[]
    for label,a,end in spans:
        b=at(a,end-a);(ROOT/'source'/f'{label}.bin').write_bytes(b);ranges.append(dict(name=label,address=hex(a),bytes=len(b),sha256=sha(b)))
        asm.append(f'\n# {label} {a:#x}..{end:#x}');asm.extend(f'{x.address:08x}: {x.bytes.hex()} {x.mnemonic} {x.op_str}' for x in md.disasm(b,a))
    for label,a,n in [('advertising-master',0x8009fe40,5*44),('daily-delta-jump-table',0x800108b0,24),('notification-strings',0x80098d6c,0x80098df0-0x80098d6c)]:
        b=at(a,n);(ROOT/'source'/f'{label}.bin').write_bytes(b);ranges.append(dict(name=label,address=hex(a),bytes=n,sha256=sha(b)))
    (ROOT/'advertising-readers.asm').write_text('\n'.join(asm)+'\n');write('source-ranges.json',ranges)
    write('summary.json',dict(promotion_types=5,menu_combinations=32,initial_stores=11,canonical_popularity_field='store+C6C',
        cost_values=[p['cost'] for p in promotions],gains=[p['popularity_gain'] for p in promotions],daily_midnight_delta=delta,original_cpu_updates=0,
        source_confirmed='Five original44-byte rows; current cash5x gate versus1x charge, persistent own flags, all-company scope, rival10x selection and original UI popularity label.',
        prior_context='Guide/video definitions already had matching cost/gain/time rows; isolated native economic paths existed. Prior reference_sim scheduler explicitly left late scheduling/payment semantics partially unresolved.',
        remaining='No new mobile implementation, UI timing measurement or natural rival advertising sequence.'))
    print(json.dumps(dict(promotions=5,costs=[p['cost'] for p in promotions],gains=[p['popularity_gain'] for p in promotions],combinations=32)))

if __name__=='__main__':main()
