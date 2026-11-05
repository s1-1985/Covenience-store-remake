"""Small original appearance and audio-ID tables; no executable runtime."""
import argparse,json,struct
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('exe',type=Path);a=p.parse_args();raw=a.exe.read_bytes()
def at(addr,n):return raw[addr-0x80010000+0x800:addr-0x80010000+0x800+n]
data=dict(source='SLPS_007.82 / 2c00ba53',groups=[struct.unpack('<h',at(0x800A09D0+i*24,2))[0]for i in range(144)],appearances=list(at(0x800A1B44,176)),roles=list(at(0x800CD758,6)),sound_flags=list(struct.unpack('<16i',at(0x8009947C,64))),music_choices=list(struct.unpack('<4i',at(0x80099864,16))))
out=Path(__file__).resolve().parents[2]/'game/data/source_actor_tables.json';out.write_text(json.dumps(data,separators=(',',':'))+'\n');print(data['roles'])
