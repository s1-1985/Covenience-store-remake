#!/usr/bin/env python3
"""Audit natural cash, native error recovery, and independent native file decode."""
import hashlib,json,runpy,shutil,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
from save_codec import BASE,SIZE,FIELDS,valid
def sha(b):return hashlib.sha256(b).hexdigest()
snapshots=algo/'source/opened-snapshots-20261028'
def snap(name):
    m=json.loads((snapshots/(name+'.json')).read_text());b=zlib.decompress((snapshots/(name+'.ram.zlib')).read_bytes())
    assert len(b)==2097152 and sha(b)==m['ram_sha256'];return m,b
im,before=snap('TOWN0001-ci-main-09-single');fm,after=snap('TOWN0001-ci-main-10-single')
path=algo/'opened-snapshot-TOWN0001-ci-main-10-single-verification-20261103.json'
proof=json.loads(path.read_text());c=proof['cases'][0]
assert proof['all_passed'] and proof['iterations_verified']==60
assert c['snapshot_sha256']==im['ram_sha256']==fm['parent_snapshot_sha256']
assert fm['completed_iterations']==im['completed_iterations']+60
assert c['opening_clock']==15960 and c['steps'][-1]['clock']==16080 and not c['midnight_finance_checks']
opening=list(struct.unpack_from('<2i',before,0xcd9f8));cash=opening[:];count=0
signed=lambda x:(x+0x80000000)%0x100000000-0x80000000
for e in c['accounting_write_trace']:
    a=int(e['address'],16)
    if a not in (0xcd9f8,0xcd9fc):continue
    owner=(a-0xcd9f8)//4;assert e['size']==4 and signed(e['before'])==cash[owner]
    cash[owner]=signed(e['after']);count+=1
assert cash==list(struct.unpack_from('<2i',after,0xcd9f8))
ledger=opening[:];stores=[]
for slot in range(10):
    p=0x12b2f8+slot*5080;assert before[p]==after[p] and before[p+4:p+6]==after[p+4:p+6]
    if not before[p]:continue
    owner=struct.unpack_from('<H',before,p+4)[0]>>15
    a=list(struct.unpack_from('<5i',before,p+0xd88));b=list(struct.unpack_from('<5i',after,p+0xd88))
    assert a[:3]==b[:3]==[0,0,0] and before[p+0xd9c:p+0xdd8]==after[p+0xd9c:p+0xdd8]
    sales,goods=b[4]-a[4],b[3]-a[3];ledger[owner]+=sales-goods
    stores.append(dict(slot=slot,owner=owner,sales=sales,goods=goods))
assert ledger==cash and len(c['whole_staff_loop_checks'])==len(c['customer_loop_checks'])==180
natural=dict(all_passed=True,updates=60,clock_before=15960,clock_after=16080,completed_iterations=fm['completed_iterations'],
    cash_before=opening,cash_after=cash,cash_from_ledgers=ledger,cash_writes=count,stores=stores,staff_checks=180,customer_checks=180,
    source_ram_sha256=im['ram_sha256'],final_ram_sha256=fm['ram_sha256'])
(ROOT/'natural-audit.json').write_text(json.dumps(natural,indent=2)+'\n')
ref=runpy.run_path(str(ROOT.parent/'20261103-native-file-recovery/native-file-analysis.py'),run_name='file_reference')
exe=(algo/'source/SLPS_007.82').read_bytes();rows=[]
for scenario in ('create','retry'):
    folder=ROOT/scenario;d=json.loads((folder/'play-save.json').read_text());assert d['all_passed']
    statuses=[row['init_status'] for row in d['save_policy']];assert statuses==([2] if scenario=='create' else [5,0])
    functions=d['card']['native_calls'];assert [row['status'] for row in functions]==([2,0,0] if scenario=='create' else [5,0,0,0])
    if scenario=='retry':
        first=functions[0]
        assert all(row['pc']!='0x8007e51c' for row in d['card']['bios_calls'][first['bios_before']:first['bios_after']])
    card=(folder/'operating-menu-save.card-file.bin').read_bytes();payload=card[512:512+SIZE]
    assert len(card)==114688 and valid(payload) and sha(payload)==d['encoders'][0]['payload_sha256']
    temporary_return_address=None
    if scenario=='create':
        initial_a=(folder/'initial-native-0.bin').read_bytes();initial_b=(folder/'initial-reference-0.bin').read_bytes()
        trace=json.loads((folder/'menu-save-reach-trace.json').read_text())['reached']
        # Original 5FE54 saves RA at entry SP-4; both parents share entry SP.
        entry_sp=im['registers']['31'];source_address=int(d['card']['ram_mirror_reads'][0]['address'],16)
        offset=(entry_sp-4)-source_address
        assert offset==34116
        assert initial_a[offset:offset+4]==struct.pack('<I',int(trace[0][0]['caller'],16))
        assert initial_b[offset:offset+4]==struct.pack('<I',int(trace[1][0]['caller'],16))
        assert [i for i,(a,b) in enumerate(zip(initial_a,initial_b)) if a!=b]==[offset,offset+1,offset+2]
        temporary_return_address=dict(file_offset=offset,native=trace[0][0]['caller'],reference=trace[1][0]['caller'],
            overwritten_by_final_body=True,final_entire_file_equal=True)
    cpu=ref['Cpu'](exe);env=ref['LogicalFiles'](cpu,{ref['PATH']:card})
    for mode in (0,1):assert cpu.run(0x8007ab2c,[mode],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)==0
    assert cpu.read(BASE,114176)==card[512:]
    assert cpu.run(0x8005188c,[],limit=3000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)==0
    for off,a,n in FIELDS:cpu.write(a,b'\xcc'*n)
    decode_return=cpu.run(0x8006bc40,[],limit=1000000,stack_pointer=0x801d0000,global_pointer=0x800cd6c4)
    assert all(cpu.read(a,n)==payload[off:off+n] for off,a,n in FIELDS) and not env.fds
    reads=[r for r in env.io if r['op']=='read'];assert len(reads)==892
    assert [r['file_offset'] for r in reads]==list(range(512,114688,128))
    row=dict(scenario=scenario,all_passed=True,attempt_statuses=statuses,attempt_results=[r['result'] for r in d['save_policy']],
        card_sha256=sha(card),payload_sha256=sha(payload),saved_clock=struct.unpack_from('<I',payload,0x30)[0],
        saved_cash=list(struct.unpack_from('<2i',payload,0x3c)),decoded_regions=len(FIELDS),reads=892,decode_return=decode_return,
        initial_transfer_differences=d.get('initial_transfer_comparison',[]),temporary_return_address=temporary_return_address)
    rows.append(row);(folder/'read-decode-io.json').write_text(json.dumps(env.io,separators=(',',':'))+'\n')
    name='TOWN0001-menu-'+scenario+'-recovery-20261105-single'
    for ext in ('.json','.ram.zlib'):
        src=snapshots/(name+ext);dst=ROOT/'evidence'/src.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
for src in (path,snapshots/'TOWN0001-ci-main-10-single.json',snapshots/'TOWN0001-ci-main-10-single.ram.zlib'):
    dst=ROOT/'evidence'/src.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
cancel_path=ROOT/'cancel/play-save.json'
if cancel_path.exists():
    d=json.loads(cancel_path.read_text());assert d['all_passed']
    assert [r['init_status'] for r in d['save_policy']]==[5]
    assert len(d['card']['native_calls'])==1 and d['card']['native_calls'][0]['status']==5
    assert not any(r['op']=='write' for r in d['card']['io'])
    baseline=(ROOT.parent/'20261104-long-continuation/TOWN0001-ci-main-08-single.card-file.bin').read_bytes()
    assert (ROOT/'cancel/operating-menu-save.card-file.bin').read_bytes()==baseline
    rows.append(dict(scenario='cancel',all_passed=True,attempt_statuses=[5],attempt_results=[5],
        writes=0,unchanged_card_sha256=sha(baseline),scope='User acknowledges error, cancels save and exits settings; original existing file remains byte-identical.'))
    for ext in ('.json','.ram.zlib'):
        src=snapshots/('TOWN0001-menu-cancel-recovery-20261105-single'+ext);dst=ROOT/'evidence'/src.relative_to(algo);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
out=dict(all_passed=True,total=len(rows),cases=rows,limits=['Existing BIOS/file/event adapters, not physical card communication.',
    'Init5 is reached by controlled BIOS info responses [1,1,1,0]; original game code derives error and retries after raw UI input.',
    'Read/checksum/decode is a separate strict-MIPS diagnostic of actual UI-written files; original fields are corrupted only in that diagnostic.',
    'All three menu cases start from the same main09 state; none replaces natural main10.'])
(ROOT/'recovery-audit.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(all_passed=True,cases=len(rows),decoded_file_cases=2,decoded_regions_per_file=len(FIELDS),natural_clock=16080)))
