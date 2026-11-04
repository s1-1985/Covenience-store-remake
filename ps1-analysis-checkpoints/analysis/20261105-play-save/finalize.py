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
source='TOWN0001-ci-main-08-single';output='TOWN0001-ci-main-09-single'
im,before=snapshot(source);fm,after=snapshot(output)
proof_path=algo/('opened-snapshot-'+output+'-verification-20261103.json')
proof=json.loads(proof_path.read_text());row=proof['cases'][0]
assert proof['all_passed'] and proof['iterations_verified']==60
assert row['snapshot_sha256']==im['ram_sha256']==fm['parent_snapshot_sha256']
assert fm['completed_iterations']==im['completed_iterations']+60
assert row['opening_clock']==15840 and row['steps'][-1]['clock']==15960 and not row['midnight_finance_checks']
opening=list(struct.unpack_from('<2i',before,0xcd9f8));cash=opening[:];writes=0
signed=lambda x:(x+0x80000000)%0x100000000-0x80000000
for event in row['accounting_write_trace']:
    address=int(event['address'],16)
    if address not in (0xcd9f8,0xcd9fc):continue
    side=(address-0xcd9f8)//4
    assert event['size']==4 and signed(event['before'])==cash[side]
    cash[side]=signed(event['after']);writes+=1
assert cash==list(struct.unpack_from('<2i',after,0xcd9f8))
ledger=opening[:];stores=[]
for slot in range(10):
    off=0x12b2f8+5080*slot
    assert before[off]==after[off] and before[off+4:off+6]==after[off+4:off+6]
    if not before[off]:continue
    owner=struct.unpack_from('<H',before,off+4)[0]>>15
    a=list(struct.unpack_from('<5i',before,off+0xd88));b=list(struct.unpack_from('<5i',after,off+0xd88))
    assert a[:3]==b[:3]==[0,0,0] and before[off+0xd9c:off+0xdd8]==after[off+0xd9c:off+0xdd8]
    sales,goods=b[4]-a[4],b[3]-a[3];ledger[owner]+=sales-goods
    stores.append(dict(slot=slot,owner=owner,additional_sales=sales,additional_goods=goods))
assert ledger==cash and len(row['whole_staff_loop_checks'])==len(row['customer_loop_checks'])==180
result=dict(all_passed=True,updates=60,clock_before=15840,clock_after=15960,completed_iterations=fm['completed_iterations'],
    cash_before=opening,cash_after=cash,cash_from_ledgers=ledger,cash_writes=writes,stores=stores,staff_checks=180,customer_checks=180,
    source_ram_sha256=im['ram_sha256'],final_ram_sha256=fm['ram_sha256'],daily_closes=0)
(ROOT/'natural-audit.json').write_text(json.dumps(result,indent=2)+'\n')
for p in [proof_path,snaps/(output+'.json'),snaps/(output+'.ram.zlib')]:
    dst=ROOT/'evidence'/p.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
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
name='TOWN0001-menu-save-20261105-single'
for ext in ('.json','.ram.zlib'):
    p=snaps/(name+ext);dst=ROOT/'evidence'/p.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
load_path=ROOT/'play-load.json'
if load_path.exists():
    load=json.loads(load_path.read_text());assert load['all_passed'] and len(load['decode_checks'])==1
    assert load['decode_checks'][0]['payload_sha256']==sha(payload)
    lm,loaded_ram=snapshot('TOWN0001-menu-load-20261105-single')
    products=lambda ram:b''.join(ram[0x9ce14+j*88:0x9ce14+j*88+48] for j in range(27))
    assert products(loaded_ram)==products(before)
    assert loaded_ram[0x9c7a0:0x9c7a0+1616]==before[0x9c7a0:0x9c7a0+1616]
    tables=dict(all_passed=True,loaded_ram_sha256=sha(loaded_ram),products27x12_sha256=sha(products(loaded_ram)),
        appearance101x4_sha256=sha(loaded_ram[0x9c7a0:0x9c7a0+1616]),
        scope='All native post-load product/appearance references match the certified single-conversion entry snapshot.')
    (ROOT/'loaded-runtime-tables.json').write_text(json.dumps(tables,indent=2)+'\n')
    for ext in ('.json','.ram.zlib'):
        p=snaps/('TOWN0001-menu-load-20261105-single'+ext);dst=ROOT/'evidence'/p.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
print(json.dumps(dict(all_passed=True,natural_clock=15960,menu_saved_clock=decoded['saved_clock'],decoded_regions=len(FIELDS))))
