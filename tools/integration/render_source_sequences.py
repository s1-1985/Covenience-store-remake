"""Offline source SEQ/SEP + VAB sample rendering (TinySoundFont 0.3.7).

Source melodies, notes, sample IDs and controllers are retained. This is NOT
SPU emulation. REMAKE_BALANCED_DEFAULT: SoundFont envelopes approximate SPU
ADSR; interpolation, dry mixing, fine tuning and libsnd NRPN/reverb differ.
Keep those rendering differences visible until a reference PCM comparison.
Formats: Sony Sound Artist Tool, Sound20.pdf; extracted original byte tables.
https://psx.arthus.net/sdk/Psy-Q/DOCS/Devrefs/Sound20.pdf
Only generated Ogg and provenance JSON ship, not SF2, MIDI or the renderer.
"""
from pathlib import Path
import argparse, collections, hashlib, json, math, struct, subprocess, tempfile, wave
import numpy as np
from tinysoundfont import Synth

ROOT = Path(__file__).resolve().parents[2]
RATE = 44100

def chunk(tag, data):
    return tag + struct.pack('<I', len(data)) + data + b'\0'*(len(data)&1)

def name(s):
    return s.encode()[:20].ljust(20,b'\0')

def gen(op, value):
    return struct.pack('<HH',op,value&65535)

def timecents(seconds):
    return max(-12000,min(8000,round(1200*math.log2(max(seconds,0.000001)))))

def envelope_seconds(rate, start, target, exponential=False):
    level=start; elapsed=0; increasing=target>start
    cycles=1<<max(0,(rate>>2)-11)
    step=((7-(rate&3)) if increasing else (-8+(rate&3)))<<max(0,11-(rate>>2))
    for _ in range(100000):
        if (increasing and level>=target) or (not increasing and level<=target): break
        delay=cycles* (4 if increasing and exponential and level>0x6000 else 1)
        change=step if increasing or not exponential else min(-1,(step*level)>>15)
        level=max(0,min(32767,level+change));elapsed+=delay
        if elapsed>RATE*100:break
    return elapsed/RATE

def bank_to_sf2(source, base, tmp):
    vh=(source/(base+'.VH')).read_bytes();vb=(source/(base+'.VB')).read_bytes()
    assert vh[:4]==b'pBAV'
    programs=struct.unpack_from('<H',vh,18)[0]
    at=0x820+programs*512
    sizes=struct.unpack_from('<256H',vh,at)
    assert sum(sizes)*8==len(vb)
    samples=[];pcm=bytearray();shdr=bytearray();offset=0
    for i,size in enumerate(sizes[1:]):
        if not size:break
        data=vb[offset:offset+size*8];offset+=size*8
        loop_start=None;loop_end=None
        for pos in range(0,len(data),16):
            flags=data[pos+1]
            if flags&4:loop_start=pos//16*28
            if flags&1:
                if flags&2:loop_end=(pos//16+1)*28
                break
        header=b'VAGp'+struct.pack('>IIII',0x20,0,len(data),RATE)+bytes(12)+name('source')[:16]
        (tmp/'sample.vag').write_bytes(header+data)
        subprocess.run(['ffmpeg','-v','error','-i',str(tmp/'sample.vag'),'-y',str(tmp/'sample.wav')],check=True)
        with wave.open(str(tmp/'sample.wav')) as w:
            assert w.getnchannels()==1 and w.getsampwidth()==2
            decoded=w.readframes(w.getnframes())
        start=len(pcm)//2;end=start+len(decoded)//2
        looping=loop_start is not None and loop_end is not None and loop_start<loop_end
        shdr+=struct.pack('<20sIIIIIBbHH',name(f'sample{i+1}'),start,end,
            start+(loop_start or 0),start+(loop_end or len(decoded)//2),RATE,60,0,0,1)
        samples.append(dict(loop=looping,frames=len(decoded)//2,adpcm_sha256=hashlib.sha256(data).hexdigest()))
        pcm+=decoded+bytes(46*2)
    shdr+=struct.pack('<20sIIIIIBbHH',name('EOS'),len(pcm)//2,len(pcm)//2,0,0,RATE,60,0,0,1)
    phdr=bytearray();pbag=bytearray();pgen=bytearray();inst=bytearray();ibag=bytearray();igen=bytearray()
    tone_groups=[];present=[];packed=0
    for program in range(128):
        attr=vh[32+program*16:48+program*16]
        if not attr[0]:continue
        tones=[]
        for t in range(attr[0]):
            raw=vh[0x820+packed*512+t*32:0x820+packed*512+(t+1)*32]
            adsr1,adsr2,pr,sample=struct.unpack_from('<4H',raw,16)
            assert pr==program and 0<sample<=len(samples),(base,program,sample)
            tones.append(dict(raw=raw.hex(),sample=sample,adsr1=adsr1,adsr2=adsr2))
        packed+=1
        ix=len(present);present.append(program)
        phdr+=struct.pack('<20sHHHIII',name(f'program{program}'),program,0,ix,0,0,0)
        pbag+=struct.pack('<HH',len(pgen)//4,0);pgen+=gen(41,ix)
        inst+=struct.pack('<20sH',name(f'program{program}'),len(ibag)//4)
        for tone in tones:
            r=bytes.fromhex(tone['raw']);sample=tone['sample']-1
            adsr1=tone['adsr1'];adsr2=tone['adsr2']
            attack=envelope_seconds((adsr1>>8)&127,0,32767,bool(adsr1&0x8000))
            sustain=min(32767,((adsr1&15)+1)*0x800)
            decay=envelope_seconds(((adsr1>>4)&15)*4,32767,sustain,True)
            release=envelope_seconds((adsr2&31)*4,32767,0,bool(adsr2&32))
            volume=max(1e-6,(vh[24]/127)*(attr[1]/127)*(r[2]/127))
            pan=max(-500,min(500,round(((attr[4]-64)+(r[3]-64))*500/63)))
            ibag+=struct.pack('<HH',len(igen)//4,0)
            igen+=gen(43,r[6]|r[7]<<8)+gen(17,pan)+gen(48,round(-200*math.log10(volume)))
            igen+=gen(34,timecents(attack))+gen(36,timecents(decay))+gen(37,round(-200*math.log10(max(1e-6,sustain/32767))))+gen(38,timecents(release))
            igen+=gen(58,r[4]+r[5]//128)+gen(52,-round((r[5]%128)*100/128))
            igen+=gen(54,1 if samples[sample]['loop'] else 0)+gen(53,sample)
        tone_groups.append(dict(program=program,attribute=attr.hex(),tones=tones))
    phdr+=struct.pack('<20sHHHIII',name('EOP'),0,0,len(pbag)//4,0,0,0)
    pbag+=struct.pack('<HH',len(pgen)//4,0);pgen+=gen(0,0)
    inst+=struct.pack('<20sH',name('EOI'),len(ibag)//4)
    ibag+=struct.pack('<HH',len(igen)//4,0);igen+=gen(0,0)
    info=b'INFO'+chunk(b'ifil',struct.pack('<HH',2,1))+chunk(b'INAM',b'Original VAB offline conversion\0')
    pdta=b'pdta'+b''.join(chunk(k,v)for k,v in [(b'phdr',phdr),(b'pbag',pbag),(b'pmod',bytes(10)),(b'pgen',pgen),(b'inst',inst),(b'ibag',ibag),(b'imod',bytes(10)),(b'igen',igen),(b'shdr',shdr)])
    sf=chunk(b'RIFF',b'sfbk'+chunk(b'LIST',info)+chunk(b'LIST',b'sdta'+chunk(b'smpl',pcm))+chunk(b'LIST',pdta))
    return sf,dict(bank=base,vh_sha256=hashlib.sha256(vh).hexdigest(),vb_sha256=hashlib.sha256(vb).hexdigest(),programs=tone_groups,samples=samples)

def sequence_rows(blob):
    assert blob[:4]==b'pQES'
    if blob[4:8]==b'\0\0\0\1':
        return [(int.from_bytes(blob[8:10],'big'),int.from_bytes(blob[10:13],'big'),blob[15:])]
    rows=[];p=6
    while p<len(blob):
        identifier=int.from_bytes(blob[p:p+2],'big');resolution=int.from_bytes(blob[p+2:p+4],'big')
        tempo=int.from_bytes(blob[p+4:p+7],'big');size=int.from_bytes(blob[p+9:p+13],'big')
        assert identifier==len(rows) and resolution>0 and size>0
        data=blob[p+13:p+13+size];assert len(data)==size
        rows.append((resolution,tempo,data));p+=13+size
    assert p==len(blob)
    return rows

def events(resolution,tempo,blob):
    p=0;status=0;seconds=0.0;result=[]
    def read():
        nonlocal p
        v=blob[p];p+=1;return v
    def vlq():
        v=0
        while True:
            x=read();v=(v<<7)|(x&127)
            if not x&128:return v
    while p<len(blob):
        delta=vlq();seconds+=delta*tempo/1000000/resolution
        if blob[p]&128:status=read()
        assert status
        if status==255:
            kind=read()
            if kind==47:
                assert read()==0
                result.append((seconds,status,[kind]));break
            if kind==81:
                tempo=(read()<<16)|(read()<<8)|read();result.append((seconds,status,[kind,tempo]));continue
            raise ValueError(('unhandled meta',kind,p))
        length=1 if status>>4 in (12,13) else 2
        args=[read()for _ in range(length)]
        assert all(x<128 for x in args),(p,status,args)
        result.append((seconds,status,args))
    assert result and result[-1][1:]==(255,[47])
    assert p==len(blob) or not any(blob[p:]),(p,len(blob))
    return result

def render(sf, rows, basename, out, tmp):
    tracks=[]
    for index,row in enumerate(rows):
        score=events(*row);synth=Synth(gain=-6,samplerate=RATE);sfid=synth.sfload(sf)
        first=next((a[0]for _,st,a in score if st>>4==12),0)
        for ch in range(16):synth.program_select(ch,sfid,0,first)
        chunks=[];cursor=0;controllers=collections.Counter()
        for seconds,status,args in score:
            sample=round(seconds*RATE)
            if sample>cursor:
                chunks.append(np.frombuffer(synth.generate_simple(sample-cursor),dtype='<f4').copy());cursor=sample
            ch=status&15;kind=status>>4
            if kind==9:
                synth.noteon(ch,args[0],args[1]) if args[1] else synth.noteoff(ch,args[0])
            elif kind==8:synth.noteoff(ch,args[0])
            elif kind==12:synth.program_change(ch,args[0])
            elif kind==11:
                controllers[args[0]]+=1
                synth.control_change(ch,args[0],args[1])
            elif kind==14:synth.pitchbend(ch,args[0]|args[1]<<7)
            elif status==255:pass
            else:raise ValueError(('unsupported event',status,args))
        # No arbitrary extra silence/tail on music loops; sound effect release
        # tails use original note-off/end-of-track timing exactly as authored.
        pcm=np.concatenate(chunks);peak=float(np.max(np.abs(pcm)))
        assert peak>0 and np.isfinite(pcm).all(),(basename,index,peak)
        scale=min(1.0,0.98/peak)
        audio=(np.clip(pcm*scale,-1,1)*32767).astype('<i2')
        with wave.open(str(tmp/'render.wav'),'wb') as w:
            w.setparams((2,2,RATE,0,'NONE','not compressed'));w.writeframes(audio.tobytes())
        filename=f'{basename}_{index:02d}.ogg'
        subprocess.run(['ffmpeg','-v','error','-i',str(tmp/'render.wav'),'-c:a','libvorbis','-q:a','4','-y',str(out/filename)],check=True)
        tracks.append(dict(id=index,file=filename,duration=cursor/RATE,frames=cursor,rate=RATE,events=len(score),controllers=dict(controllers),peak=peak,normalization=scale,sha256=hashlib.sha256((out/filename).read_bytes()).hexdigest()))
        print(filename,cursor/RATE,len(score),flush=True)
    return tracks

def main():
    p=argparse.ArgumentParser();p.add_argument('analysis',type=Path);args=p.parse_args();source=args.analysis/'source'
    out=ROOT/'game/assets/audio/source';out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((ROOT/'game/data/source_audio.json').read_text());manifest['bgm']=[];banks=[]
    with tempfile.TemporaryDirectory(prefix='conveni-seq-') as directory:
        tmp=Path(directory)
        for kind,bank,sequence in [('bgm',f'BGM{i:02d}',f'BGM{i:02d}.SEQ')for i in range(1,8)]+[('se','CON_SE','SE.SEP'),('vos','CON_KOE','VOS.SEP')]:
            sf,meta=bank_to_sf2(source,bank,tmp);banks.append(meta)
            score=(source/sequence).read_bytes();tracks=render(sf,sequence_rows(score),bank.lower(),out,tmp)
            for track in tracks:track['sequence_sha256']=hashlib.sha256(score).hexdigest()
            if kind=='bgm':
                assert len(tracks)==1;tracks[0]['id']=len(manifest[kind]);manifest[kind]+=tracks
            else:manifest[kind]=tracks
    assert [len(manifest[k])for k in ('bgm','se','vos')]==[7,16,12]
    manifest['sequence_banks']=banks
    manifest['sequence_evidence_note']='CONFIRMED_BINARY: source note events and VAB samples/programs/controllers; offline TinySoundFont 0.3.7 rendering, NumPy and FFmpeg. REMAKE_BALANCED_DEFAULT: SoundFont ADSR approximation, dry mix without SPU reverb, fine tune/pitch interpolation and libsnd NRPN are not sample-identical; not physical SPU emulation. All source tone bytes retained here for further correction.'
    (ROOT/'game/data/source_audio.json').write_text(json.dumps(manifest,indent=2)+'\n')

if __name__=='__main__':main()
