"""Offline original XA -> Ogg assets; no original CPU or disc at runtime.

Table 800B8CB8, SOUND.XA LBA1513, length in 32-sector units:
analysis 2c00ba53 cd_audio_start.py / cd_audio_control.py.
Row130 points beyond audio metadata and is deliberately never rendered.
FFmpeg's psxstr demuxer reports EOF as I/O error on a bounded stream;
accept only successful decode with the exact sector-derived PCM frame count.
"""
from pathlib import Path
import argparse, hashlib, json, struct, subprocess, tempfile, wave

DISC_SHA = '8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1'
ROOT = Path(__file__).resolve().parents[2]

def main():
    p = argparse.ArgumentParser()
    p.add_argument('analysis', type=Path)
    p.add_argument('disc', type=Path)
    args = p.parse_args()
    exe = (args.analysis / 'source/SLPS_007.82').read_bytes()
    disc = args.disc.read_bytes()
    assert hashlib.sha256(disc).hexdigest() == DISC_SHA, 'wrong source disc'
    address = 0x800b8cb8 - 0x80010000 + 0x800
    table = [struct.unpack_from('<III', exe, address+i*12) for i in range(131)]
    out = ROOT / 'game/assets/audio/source'
    out.mkdir(parents=True, exist_ok=True)
    tracks = []
    with tempfile.TemporaryDirectory(prefix='conveni-xa-') as temporary:
        tmp = Path(temporary)
        for i, (offset, channel, length) in enumerate(table[:130]):
            start = 1513 + offset
            sectors = [disc[n*2352:(n+1)*2352] for n in range(start, start+length*32)]
            sectors = [s for s in sectors if len(s)==2352 and s[17]==channel and s[18]&4]
            assert len(sectors) == length, (i, len(sectors), length)
            coding = sectors[0][19]
            assert all(s[19]==coding and s[16:20]==s[20:24] for s in sectors)
            assert coding & 0x30 == 0, 'only recovered 4-bit XA supported'
            channels = 2 if coding & 1 else 1
            rate = 18900 if coding & 4 else 37800
            expected_frames = length * 4032 // channels
            (tmp/'input.str').write_bytes(b''.join(sectors))
            result = subprocess.run(['ffmpeg','-v','error','-f','psxstr','-i',str(tmp/'input.str'),'-vn','-y',str(tmp/'decoded.wav')], capture_output=True)
            assert result.returncode==0, (i, result.stderr.decode())
            with wave.open(str(tmp/'decoded.wav')) as w:
                assert (w.getnchannels(), w.getframerate(), w.getnframes()) == (channels, rate, expected_frames), (i,w.getparams())
                pcm_hash = hashlib.sha256(w.readframes(w.getnframes())).hexdigest()
            name = f'xa_{i:03d}.ogg'
            subprocess.run(['ffmpeg','-v','error','-i',str(tmp/'decoded.wav'),'-c:a','libvorbis','-q:a','4','-y',str(out/name)],check=True)
            tracks.append(dict(id=i, dispatcher_id=i+28, offset=offset, channel=channel, sector_units=length,
                channels=channels, rate=rate, frames=expected_frames, duration=expected_frames/rate,
                pcm_sha256=pcm_hash, file=name, sha256=hashlib.sha256((out/name).read_bytes()).hexdigest()))
            print('XA',i,expected_frames,flush=True)
    data = dict(source_disc_sha256=DISC_SHA, source_exe_sha256=hashlib.sha256(exe).hexdigest(),
        table_address='800B8CB8', base_lba=1513, excluded_row130=list(table[130]), xa=tracks,
        event_tones=list(struct.unpack_from('<16i',exe,0x8009947c-0x80010000+0x800)),
        bgm_settings=list(struct.unpack_from('<4i',exe,0x80099864-0x80010000+0x800)),
        evidence_note='CONFIRMED_BINARY: original XA sectors selected by original offset/channel/length table; FFmpeg ADPCM decoded to exact PCM frame count and encoded as Ogg Vorbis. Row130 is not an audio asset. No disc, EXE, BIOS or CPU interpreter at runtime. Vorbis is a lossy distribution encoding, not physical SPU/CD equivalence.')
    (ROOT/'game/data/source_audio.json').write_text(json.dumps(data,indent=2)+'\n')

if __name__=='__main__':
    main()
