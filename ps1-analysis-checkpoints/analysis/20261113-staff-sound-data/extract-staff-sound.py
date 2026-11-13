#!/usr/bin/env python3
"""Static disc -> event/SEP/VAB/sample bridge. No original CPU emulation.
Requires capstone, Pillow (sibling ISO reader), ffmpeg for optional voice previews.
"""
import argparse, hashlib, io, json, runpy, struct, subprocess, tempfile, zipfile
from pathlib import Path
from capstone import Cs,CS_ARCH_MIPS,CS_MODE_MIPS32,CS_MODE_LITTLE_ENDIAN
ROOT=Path(__file__).resolve().parent
DISC_SHA='8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
EXE_SHA='d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd'
def sha(b):return hashlib.sha256(b).hexdigest()
def js(name,data):(ROOT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
def vlq(data,pos):
    n=0
    while True:
        v=data[pos];pos+=1;n=(n<<7)|(v&127)
        if not v&128:return n,pos
def events(score):
    pos=tick=0;running=None;programs=[0]*16;out=[]
    while pos<len(score):
        dt,pos=vlq(score,pos);tick+=dt
        if score[pos]&128:status=score[pos];pos+=1;running=status if status<0xf0 else running
        else:assert running is not None;status=running
        if status==0xff:
            kind=score[pos];pos+=1;n,pos=vlq(score,pos);body=score[pos:pos+n];pos+=n
            out.append(dict(tick=tick,status=status,meta_type=kind,data=list(body)))
            if kind==0x2f:assert pos==len(score);break
        else:
            kind=status>>4;channel=status&15;assert 8<=kind<=14
            n=1 if kind in (12,13) else 2;body=score[pos:pos+n];pos+=n;assert all(v<128 for v in body)
            e=dict(tick=tick,status=status,channel=channel,data=list(body))
            if kind==12:programs[channel]=body[0]
            if kind==9 and body[1]>0:e.update(note_on=True,program=programs[channel],note=body[0],velocity=body[1])
            out.append(e)
    return out
def sep(data):
    assert data[:6]==b'pQES\0\0';pos=6;out=[]
    while pos<len(data):
        start=pos;identifier,ppqn=struct.unpack_from('>2H',data,pos);tempo=int.from_bytes(data[pos+4:pos+7],'big');rhythm=list(data[pos+7:pos+9]);size=int.from_bytes(data[pos+9:pos+13],'big');pos+=13;score=data[pos:pos+size];pos+=size
        assert len(score)==size and score.endswith(b'\xff\x2f\0')
        out.append(dict(id=identifier,offset=start,score_offset=start+13,score_bytes=size,ppqn=ppqn,tempo_us=tempo,rhythm=rhythm,events=events(score)))
    assert pos==len(data);return out
def vab(vh,vb):
    assert vh[:4]==b'pBAV'
    count,tones_count,samples_count=struct.unpack_from('<3H',vh,18)
    active=[i for i in range(128) if vh[32+i*16]>0];assert len(active)==count
    assert len(vh)==0x820+count*512+512 and struct.unpack_from('<I',vh,12)[0]==len(vh)+len(vb)
    programs=[]
    for block,p in enumerate(active):
        pr=vh[32+p*16:48+p*16];tones=[]
        for j in range(pr[0]):
            off=0x820+block*512+j*32;t=vh[off:off+32];prog,sample=struct.unpack_from('<2h',t,20);assert prog==p
            tones.append(dict(index=j,offset=off,program=p,sample=sample,priority=t[0],mode=t[1],volume=t[2],pan=t[3],center_note=t[4],shift_raw=t[5],note_min=t[6],note_max=t[7],adsr1=struct.unpack_from('<H',t,16)[0],adsr2=struct.unpack_from('<H',t,18)[0],raw_hex=t.hex()))
        programs.append(dict(id=p,tone_block_index=block,raw_program_hex=pr.hex(),tones=tones))
    assert sum(len(p['tones']) for p in programs)==tones_count
    sizes=list(struct.unpack_from('<256H',vh,0x820+count*512));assert sum(sizes)*8==len(vb)
    samples=[];off=0
    for i,n in enumerate(sizes):
        if n:
            b=vb[off:off+n*8];assert len(b)%16==0
            samples.append(dict(id=i,offset=off,bytes=len(b),blocks=len(b)//16,decoded_frames=len(b)//16*28,sha256=sha(b),end_flag_blocks=[k//16 for k in range(0,len(b),16) if b[k+1]&1],loop_start_blocks=[k//16 for k in range(0,len(b),16) if b[k+1]&4]))
        off+=n*8
    assert len(samples)==samples_count
    return dict(program_count=count,tone_count=tones_count,sample_count=samples_count,programs=programs,samples=samples)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('disc',type=Path);ap.add_argument('--voice-previews',action='store_true');args=ap.parse_args()
    raw=args.disc.read_bytes();assert sha(raw)==DISC_SHA
    lib=runpy.run_path(str(ROOT.parent/'20261113-disc-data-extraction/extract-disc-data.py'));rows,read=lib['iso'](raw);files={r['path']:r for r in rows}
    def payload(name):r=files[name];return read(r['lba'],r['bytes'])
    exe=payload('/SLPS_007.82');assert sha(exe)==EXE_SHA
    def at(a,n):return exe[a-0x80010000+2048:a-0x80010000+2048+n]
    (ROOT/'source').mkdir(exist_ok=True);sources=[];banks={};midfiles=[]
    for bank,base,seqname,offset in [('effects','CON_SE','SE',0),('voices','CON_KOE','VOS',16)]:
        inputs={ext:payload('/SE/'+name+'.'+ext) for name,ext in [(base,'VH'),(base,'VB'),(seqname,'SEP')]}
        for ext,b in inputs.items():
            name=(seqname if ext=='SEP' else base)+'.'+ext;(ROOT/'source'/name).write_bytes(b);sources.append(dict(path='/SE/'+name,sha256=sha(b),bytes=len(b)))
        data=vab(inputs['VH'],inputs['VB']);tracks=sep(inputs['SEP']);pm={p['id']:p for p in data['programs']}
        for track in tracks:
            track['dispatch_id']=offset+track['id']
            for e in track['events']:
                if e.get('note_on'):
                    e['tone_matches']=[dict(sample=t['sample'],center_note=t['center_note'],shift_raw=t['shift_raw'],tone_index=t['index']) for t in pm[e['program']]['tones'] if t['note_min']<=e['note']<=t['note_max']]
                    assert e['tone_matches']
            score=inputs['SEP'][track['score_offset']:track['score_offset']+track['score_bytes']]
            # MIDI is an editable score export, not a rendered SPU performance.
            header=b'\0\xff\x51\x03'+track['tempo_us'].to_bytes(3,'big')+b'\0\xff\x58\x04'+bytes(track['rhythm']+[24,8]);body=header+score
            midi=b'MThd'+struct.pack('>I3H',6,0,1,track['ppqn'])+b'MTrk'+struct.pack('>I',len(body))+body
            midfiles.append((f'{bank}/dispatch-{track["dispatch_id"]:02d}.mid',midi))
        data['sequences']=tracks;banks[bank]=data
    with zipfile.ZipFile(ROOT/'sequence-midi.zip','w',zipfile.ZIP_DEFLATED) as z:
        for name,b in midfiles:
            info=zipfile.ZipInfo(name,(2026,11,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    tones=list(struct.unpack('<16i',at(0x8009947c,64)));flags=[]
    contexts={4:'underfunded ordinary purchase/theft branch',7:'resting employee switches to cashier after recovery',8:'cashier finds no relevant customers and clears goal',9:'checkout service completed and cart settled',10:'immediate-payment purchase completed',11:'successful replenishment or cleaning',12:'active employee energy exhausted'}
    for bit,tone in enumerate(tones):
        identifier={0:'50',1:'49',2:'month+36',3:'extra+51'}.get(bit,str(tone))
        f=dict(bit=bit,mask=hex(1<<bit),dispatch=identifier,context=contexts.get(bit,'producer not mapped in this work'))
        if bit<4:
            f.update(bank='XA',xa_row={0:'22',1:'21',2:'month+8',3:'extra+23'}[bit])
        if bit>=4:
            bank='effects' if tone<16 else 'voices' if tone<28 else 'XA';f['bank']=bank
            if bank!='XA':f['sequence_id']=tone-(16 if bank=='voices' else 0)
            else:f['xa_row']=tone-28
        flags.append(f)
    js('audio-sequence-bank-data.json',dict(source_disc_sha256=DISC_SHA,source_exe_sha256=EXE_SHA,sources=sources,banks=banks))
    js('android-staff-sound-bridge.json',dict(schema_version=1,flag_order='ascending bit order0..15; repeated same-bit events coalesce until consumed',flag_gate='Main fragment requires enabled byte nonzero and selected store matching; dispatcher SE/voice requires enabled byte exactly1; guard6 suppresses dispatcher.',flags=flags,dispatch_domains={'0..15':'SE.SEP sequence ID, CON_SE bank','16..27':'VOS.SEP sequence ID=dispatch-16, CON_KOE bank','28+':'XA startup row=dispatch-28'},voice22=dict(sequence=6,program=6,sample=7),voice23=dict(sequence=7,program=7,sample=8),checkout10='SE sequence10 uses multiple note events/programs; do not replace its score with a single sample.',staff_states={'0':'resting','1':'cashier task including travel','2':'refill task including travel','3':'travel toward rest','4':'cleaning task including travel'},direction_vectors=[list(struct.unpack('<2i',at(0x8009941c+j*8,8))) for j in range(4)],direction_image_offsets=list(struct.unpack('<4i',at(0x8009940c,16))),route='10 bytes;0xff terminates; high2 bits direction,low6 bits remaining half-cell steps. Obstruction can trigger sidestep/replan.',actor_image_rule='appearance*4+direction_offset+640; these source expressions contain no walk-phase term.',limits='No global claim that original game has no walking animation; real-time timing and other render paths remain outside this extraction.'))
    js('summary.json',dict(effect_sequences=len(banks['effects']['sequences']),voice_sequences=len(banks['voices']['sequences']),effect_programs=banks['effects']['program_count'],effect_samples=banks['effects']['sample_count'],voice_samples=banks['voices']['sample_count'],sparse_effect_program_ids=[p['id'] for p in banks['effects']['programs']],checkout_notes=[e for e in banks['effects']['sequences'][10]['events'] if e.get('note_on')],new_work='Parse actual SEP/VAB sample links, distinguish dispatch versus XA IDs, connect staff/checkout flags to source audio sequences. Movement formula/state evidence reused and packaged.'))
    spans=[('main_audio_flags',0x80023a14,0x80023bbc),('audio_dispatch',0x80064e4c,0x80065000),('se_initialize',0x80065350,0x8006558c),('staff_move_commit',0x80037734,0x80037f44),('staff_state_update',0x80036ac0,0x80037734),('checkout_settlement',0x80035128,0x80035770)]
    md=Cs(CS_ARCH_MIPS,CS_MODE_MIPS32|CS_MODE_LITTLE_ENDIAN);asm=[];ranges=[]
    for name,a,end in spans:
        b=at(a,end-a);(ROOT/'source'/f'{name}.bin').write_bytes(b);ranges.append(dict(name=name,address=hex(a),bytes=len(b),sha256=sha(b)));asm.append(f'\n# {name} {a:#x}..{end:#x}')
        asm.extend(f'{i.address:08x}: {i.bytes.hex()} {i.mnemonic} {i.op_str}' for i in md.disasm(b,a))
    (ROOT/'staff-audio-readers.asm').write_text('\n'.join(asm)+'\n');js('source-ranges.json',ranges)
    if args.voice_previews:
        meta=[]
        with tempfile.TemporaryDirectory() as td,zipfile.ZipFile(ROOT/'voice-previews.zip','w',zipfile.ZIP_DEFLATED) as z:
            vb=payload('/SE/CON_KOE.VB');samplemap={s['id']:s for s in banks['voices']['samples']}
            for track in banks['voices']['sequences']:
                notes=[e for e in track['events'] if e.get('note_on')];assert len(notes)==1
                n=notes[0];assert n['note']==60 and n['tone_matches'][0]['center_note']==84 and n['tone_matches'][0]['shift_raw']==0
                s=samplemap[n['tone_matches'][0]['sample']];b=vb[s['offset']:s['offset']+s['bytes']]
                vag=b'VAGp'+struct.pack('>4I',0x20,0,len(b),11025)+bytes(12)+bytes(16);v=Path(td)/'sample.vag';w=Path(td)/'sample.wav';v.write_bytes(vag+b)
                subprocess.run(['ffmpeg','-v','error','-y','-i',str(v),str(w)],check=True)
                import wave
                with wave.open(str(w)) as decoded:
                    assert decoded.getnframes()==s['decoded_frames'] and decoded.getframerate()==11025 and decoded.getnchannels()==1 and decoded.getsampwidth()==2
                name=f'dispatch-{track["dispatch_id"]:02d}-sample-{s["id"]:02d}.wav';info=zipfile.ZipInfo(name,(2026,11,13,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,w.read_bytes());meta.append(dict(file=name,dispatch=track['dispatch_id'],sample=s['id'],sample_rate=11025,sha256=sha(w.read_bytes())))
        js('voice-preview-index.json',dict(files=meta,note='Decoded sample previews at note60/center84 pitch rate44100/4. Not a full SPU mix: no ADSR, gain, reverb or sequence note-off rendering. No spoken-text transcription claimed.'))
    print(json.dumps(dict(effects=16,voices=12,samples=banks['effects']['sample_count']+banks['voices']['sample_count']),ensure_ascii=False))
if __name__=='__main__':main()
