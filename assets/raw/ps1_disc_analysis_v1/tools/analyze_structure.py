from pathlib import Path
import struct,json,collections,hashlib,csv
BASE=Path(__file__).resolve().parents[1]
import argparse
parser=argparse.ArgumentParser();parser.add_argument('--bin',type=Path,default=BASE.parent/'upload/SLPS_00782.BIN');args=parser.parse_args()
raw=args.bin.read_bytes();count=len(raw)//2352
sub=collections.Counter();bad_sync=[];bad_duplicate=[]
for i in range(count):
 s=raw[i*2352:(i+1)*2352]
 if s[:12]!=bytes.fromhex('00ffffffffffffffffffff00'):bad_sync.append(i)
 if s[16:20]!=s[20:24]:bad_duplicate.append(i)
 sub[f'mode{s[15]}-form{2 if s[18]&32 else 1}']+=1
summary=dict(input_size=len(raw),sector_size=2352,sector_count=count,sha256=hashlib.sha256(raw).hexdigest(),sector_types=dict(sub),invalid_sync_sectors=bad_sync,subheader_mismatches=bad_duplicate,edc_ecc_checked=False,zero_padding_file='3MIN.BIN',zero_padding_length=31455687,zero_padding_verified=not any((BASE/'files/3MIN.BIN').read_bytes()))
(BASE/'disc-summary.json').write_text(json.dumps(summary,indent=2))
audio=[]
for p in sorted((BASE/'files').rglob('*.VH')):
 b=p.read_bytes();vb=p.with_suffix('.VB').read_bytes();programs,tones,vags=struct.unpack_from('<3H',b,18);sizes=struct.unpack_from('<256H',b,len(b)-512);active=[dict(index=i,length_units8=s,length_bytes=s*8) for i,s in enumerate(sizes) if s]
 audio.append(dict(bank=str(p.relative_to(BASE/'files')),program_field=programs,tone_field=tones,sample_field=vags,header_size=len(b),body_size=len(vb),header_program_layout_matches=len(b)==0x820+programs*512+512,sample_size_sum=sum(sizes)*8,sample_size_sum_matches_body=sum(sizes)*8==len(vb),samples=active))
seq=[]
for p in sorted((BASE/'files').rglob('*.SEQ')):
 b=p.read_bytes();tempo=int.from_bytes(b[10:13],'big');seq.append(dict(file=str(p.relative_to(BASE/'files')),ppqn=int.from_bytes(b[8:10],'big'),initial_tempo_microseconds=tempo,initial_bpm=60000000/tempo))
(BASE/'audio-index.json').write_text(json.dumps(dict(banks=audio,sequences=seq),indent=2))
rows=json.load(open(BASE/'inventory.json'))
with (BASE/'inventory.csv').open('w',newline='') as f:
 w=csv.writer(f);w.writerow(['path','LBA','ISO_size','extraction','sha256_extracted'])
 for r in rows:w.writerow([r['path'],r['lba'],r['size'],r['extraction'],r['sha256']])
print(summary);print('VAB validation',[(r['bank'],r['sample_field'],r['sample_size_sum_matches_body']) for r in audio])
