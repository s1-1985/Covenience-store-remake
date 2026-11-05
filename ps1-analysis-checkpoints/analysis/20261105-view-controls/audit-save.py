#!/usr/bin/env python3
"""Reconcile the new natural segment and independently read/decode the UI-written file."""
import hashlib,json,runpy,shutil,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
from save_codec import BASE,SIZE,FIELDS,valid
def sha(b):return hashlib.sha256(b).hexdigest()
snaps=algo/'source/opened-snapshots-20261028'
def snapshot(name):
    meta=json.loads((snaps/(name+'.json')).read_text());ram=zlib.decompress((snaps/(name+'.ram.zlib')).read_bytes())
    assert sha(ram)==meta['ram_sha256'];return meta,ram
im,before=snapshot('TOWN0001-view-own-20261105-single')
ref=runpy.run_path(str(ROOT.parent/'20261103-native-file-recovery/native-file-analysis.py'),run_name='file_reference')
exe=(algo/'source/SLPS_007.82').read_bytes();cpu=ref['Cpu'](exe)
card=(ROOT/'operating-menu-save.card-file.bin').read_bytes();payload=card[512:512+SIZE]
assert len(card)==114688 and valid(payload)
env=ref['LogicalFiles'](cpu,{ref['PATH']:card});calls=[]
for mode in (0,1):
    value=cpu.run(0x8007ab2c,[mode],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
    assert value==0;calls.append(dict(function='7AB2C',mode=mode,instructions=cpu.steps))
assert cpu.read(BASE,114176)==card[512:]
assert cpu.run(0x8005188c,[],limit=3000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)==0
for off,address,size in FIELDS:cpu.write(address,b'\xcc'*size)
decode_return=cpu.run(0x8006bc40,[],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
assert all(cpu.read(address,size)==payload[off:off+size] for off,address,size in FIELDS)
reads=[r for r in env.io if r['op']=='read'];assert len(reads)==892
assert [r['file_offset'] for r in reads]==list(range(512,114688,128)) and not env.fds
decoded=dict(all_passed=True,input_card_sha256=sha(card),payload_sha256=sha(payload),decoded_regions=len(FIELDS),
    saved_clock=struct.unpack_from('<I',payload,0x30)[0],saved_cash=list(struct.unpack_from('<2i',payload,0x3c)),
    original_calls=calls,decode_return=decode_return,file_reads=len(reads),source_executable_sha256=sha(exe),
    limits=['Exact file written from original operating menus; separate strict-MIPS native read/checksum/decode diagnostic.',
            'Decode destinations deliberately corrupted only in this diagnostic; natural operating state remains untouched.',
            'Logical BIOS file/event boundaries, not physical card communication.'])
(ROOT/'read-decode.json').write_text(json.dumps(decoded,indent=2)+'\n')
(ROOT/'read-decode-io.json').write_text(json.dumps(env.io,separators=(',',':'))+'\n')
menu=json.loads((ROOT/'play-save.json').read_text());assert menu['all_passed']
assert decoded['payload_sha256']==menu['encoders'][0]['payload_sha256']
name='TOWN0001-menu-from-own-save-20261105-single'
for ext in ('.json','.ram.zlib'):
    p=snaps/(name+ext);dst=ROOT/'evidence'/p.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
load_path=ROOT/'play-load.json'
if load_path.exists():
    load=json.loads(load_path.read_text());assert load['all_passed'] and len(load['decode_checks'])==1
    assert load['decode_checks'][0]['payload_sha256']==sha(payload)
    lm,loaded_ram=snapshot('TOWN0001-menu-from-own-load-20261105-single')
    products=lambda ram:b''.join(ram[0x9ce14+j*88:0x9ce14+j*88+48] for j in range(27))
    assert products(loaded_ram)==products(before)
    assert loaded_ram[0x9c7a0:0x9c7a0+1616]==before[0x9c7a0:0x9c7a0+1616]
    tables=dict(all_passed=True,loaded_ram_sha256=sha(loaded_ram),products27x12_sha256=sha(products(loaded_ram)),
        appearance101x4_sha256=sha(loaded_ram[0x9c7a0:0x9c7a0+1616]),
        scope='All native post-load product/appearance references match the certified single-conversion entry snapshot.')
    (ROOT/'loaded-runtime-tables.json').write_text(json.dumps(tables,indent=2)+'\n')
    for ext in ('.json','.ram.zlib'):
        p=snaps/('TOWN0001-menu-from-own-load-20261105-single'+ext);dst=ROOT/'evidence'/p.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
print(json.dumps(dict(all_passed=True,source_clock=struct.unpack_from('<I',before,0xcd93c)[0],menu_saved_clock=decoded['saved_clock'],decoded_regions=len(FIELDS))))
