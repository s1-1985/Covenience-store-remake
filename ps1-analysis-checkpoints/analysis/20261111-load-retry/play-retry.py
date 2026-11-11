#!/usr/bin/env python3
"""Resume actual operating RAM and navigate original menus to native card write."""
import ast,difflib,hashlib,json,runpy,sys,types,shutil,zlib
from pathlib import Path
REPORT=Path(__file__).resolve().parent
variant=sys.argv[2] if len(sys.argv)>2 else "repeat-corrupt"
assert variant in ("repeat-corrupt","replace-with-valid")
accepted=variant=="replace-with-valid"
layout="fragmented"
assert layout in ("contiguous","fragmented")
ROOT=REPORT/variant
ROOT.mkdir(exist_ok=True)
sys.path.insert(0,str(REPORT.parent/"20261105-card-image"))
from raw_card import RawCard,CardFiles
algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
operation='load'
assert operation in ('save','load')
from check_machine import *
from save_codec import BASE,SIZE,FIELDS,encode,valid
from caller_connection_harness import Memory
from verify_schedule_selector_frames import seq
from unicorn import UC_HOOK_CODE
import verify_opened_snapshot_play_20261028 as play
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
reference=runpy.run_path(str(REPORT.parent/'20261103-native-file-recovery/native-file-analysis.py'),run_name='file_reference')
LogicalFiles,CARD_PATH=reference['LogicalFiles'],reference['PATH']
BaseLogicalFiles=LogicalFiles
class LogicalFiles(BaseLogicalFiles):
    def __init__(self,cpu,files):
        order=(list(range(1,16)) if layout=='contiguous' else [15,1,14,2,13,3,12,4,11,5,10,6,9,7,8])
        self.raw_card=RawCard((ROOT/'operating-menu-save.mcr').read_bytes() if operation=='load' else None,allocation_order=order)
        if operation=='save':
            for path,data in files.items():self.raw_card.create(path,bytes(data))
        for path,data in files.items():
            assert self.raw_card.read(path,0,len(data),trace=False)==bytes(data)
        super().__init__(cpu,files)
        self.files=CardFiles(self.raw_card)

adapter=REPORT.parent/'20261104-long-continuation/native-title-card-chain.py'
classes=[n for n in ast.parse(adapter.read_text()).body if isinstance(n,ast.ClassDef)]
exec(compile(ast.Module(body=classes,type_ignores=[]),str(adapter),'exec'),globals())
monitor_path=algo/'source_save_write_monitor_20261031.py';source=monitor_path.read_text()
old='    m.byteset(0x800cd820,status);z.reg_write(UC_MIPS_REG_V0,0);z.reg_write(UC_MIPS_REG_PC,z.reg_read(UC_MIPS_REG_RA));return'
assert source.count(old)==1
patched=source.replace(old,'    return # Original card routines execute; no completion or payload injection.')
patched=patched.replace('expected=payload();assert m.read(BASE,SIZE)==expected', 'expected=payload();assert (a==0x8007b1f8 and arg==1) or m.read(BASE,SIZE)==expected')
(ROOT/'save-monitor.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),patched.splitlines(True),fromfile=monitor_path.name,tofile='observed_save_monitor.py')))
module=types.ModuleType('observed_save_monitor');exec(compile(patched,str(monitor_path),'exec'),module.__dict__)
bridges=[];monitors=[];encoders=[];reached=[];hooks=[];load_monitors=[];decode_checks=[]
original_runner=play.BackgroundCategoryRunner
origin=REPORT.parent/'20261105-card-image'
image=(origin/'mutated-payload-bit-flip.mcr').read_bytes()
valid_image=(origin/'fragmented-0.mcr').read_bytes()
initial_card=RawCard(image).read(CARD_PATH,0,114688,trace=False)
(ROOT/'operating-menu-save.mcr').write_bytes(image)
card=RawCard(valid_image if accepted else image).read(CARD_PATH,0,114688,trace=False)
(ROOT/'operating-menu-save.card-file.bin').write_bytes(card)
assert valid(card[512:512+SIZE])==accepted
protected=[];policies=[]
def runner_factory(u,*args,**kwargs):
    r=original_runner(u,*args,**kwargs);m=Memory(u);expected=[None];enc=[];trace=[]
    bridge=NativeCardBridge(u,r,{CARD_PATH:initial_card});bridge.cpu.allow_ram_mirror=True
    monitor=module.SourceSaveWriteMonitor(u,r,lambda:expected[0])
    bridges.append(bridge);monitors.append(monitor);encoders.append(enc);reached.append(trace)
    decoded=[];decode_checks.append(decoded)
    fields=[];protected.append(fields)
    if operation=='load':
        from load_read_control_20261030 import LoadReadMonitor
        from load_confirmation_20261029 import LoadConfirmationMonitor
        load_monitors.append((RetryLoadReadMonitor(u,r,0,0,[False,accepted]),LoadConfirmationMonitor(u,r)))
    def observe(z,a,n,d):
        trace.append(dict(function=hex(a),caller=hex(z.reg_read(UC_MIPS_REG_RA)),clock=m.word(0x800cd93c),active=m.word(0x801398b4),processed=m.word(0x800cd884)))
        if a==0x80051524:
            attempt=len(fields)
            if accepted and attempt==1:
                assert not bridge.env.fds
                bridge.env.raw_card=RawCard(valid_image)
                bridge.env.files=CardFiles(bridge.env.raw_card)
            before=[m.read(address,size) for _,address,size in FIELDS]
            def finish_attempt():
                after=[m.read(address,size) for _,address,size in FIELDS]
                changed=[hex(address) for (_,address,_),old,new in zip(FIELDS,before,after) if old!=new]
                assert not changed,changed
                fields.append(dict(regions=len(FIELDS),unchanged=True,return_value=z.reg_read(UC_MIPS_REG_V0)))
            r.onreturn(z.reg_read(UC_MIPS_REG_RA),finish_attempt)
        if a==0x8006b81c:
            expected[0]=bytes(encode(bytearray(m.read(BASE,SIZE)),m.read))
            def finish():
                assert m.read(BASE,SIZE)==expected[0] and valid(expected[0])
                enc.append(dict(payload_sha256=sha(expected[0]),clock=m.word(0x800cd93c),cash=m.word(0x800cd9f8)))
            r.onreturn(z.reg_read(UC_MIPS_REG_RA),finish)
        if a==0x8006bc40:
            payload=m.read(BASE,SIZE);assert payload==card[512:512+SIZE] and valid(payload) and accepted
            def finish_decode():
                assert all(m.read(address,size)==payload[offset:offset+size] for offset,address,size in FIELDS)
                decoded.append(dict(payload_sha256=sha(payload),regions=len(FIELDS)))
            r.onreturn(z.reg_read(UC_MIPS_REG_RA),finish_decode)
    for a in (0x8005fe54,0x80062484,0x8006b81c,0x8004eeb8,0x8004efd0,0x800501fc,0x800505a0,0x80051174,0x80051524,0x8006bc40):hooks.append((u,u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)))
    return r
play.BackgroundCategoryRunner=runner_factory
# Check monitor accepts per-attempt expected validity; original game code is unchanged.
import load_read_control_20261030 as load_reference
monitor_source=Path(load_reference.__file__).read_text()
monitor_patched=monitor_source.replace('expected,result=policy(status,read_status,checksum_valid)',
    'validity=checksum_valid[min(len(self.checks),len(checksum_valid)-1)] if isinstance(checksum_valid,list) else checksum_valid;expected,result=policy(status,read_status,validity)').replace('read_status=read_status,checksum_valid=checksum_valid,','read_status=read_status,checksum_valid=validity,')
assert monitor_patched!=monitor_source
(ROOT/'load-monitor.patch').write_text(''.join(difflib.unified_diff(monitor_source.splitlines(True),monitor_patched.splitlines(True),fromfile='load_read_control_20261030.py',tofile='retry_load_monitor.py')))
retry_module=types.ModuleType('retry_load_monitor');exec(compile(monitor_patched,'retry_load_monitor.py','exec'),retry_module.__dict__)
RetryLoadReadMonitor=retry_module.LoadReadMonitor
plans={0x8004e578:[seq([0x4000]*4+[32])+[0]*150,seq([64])+[0]*150],
       0x8004efd0:[seq(([0x1000,0x1000,32] if operation=='save' else [0x1000,32]))+[0]*150,seq([0x800])+[0]*150],
       0x800501fc:[seq([32,64])+[0]*150],
       0x80051174:[seq([32,32,64])+[0]*150],
       0x80051524:[[0]*12+seq([64])+[0]*200 for _ in range(2)],
       0x800505a0:[[0]*12+seq([64])+[0]*150]}
try:
    result=play.compare('TOWN0001-ci-main-20-single',4,actions={0:128},native_music=True,
        input_plans=plans,finance_monitor=True,event_monitor=True,refill_monitor=True,
        customer_monitor=True,whole_town_monitor=True,staff_loop_monitor=True,
        progress_snapshot='TOWN0001-retry-'+variant+'-20261111-single',progress_file=str(ROOT/('menu-'+operation+'-progress.json')))
    # The independent parent invokes its native child through its sentinel RA.
    # Assert the exact two wrapper callers, then require every nested call equal.
    assert reached[0][0]['caller']=='0x8005d06c' and reached[1][0]['caller']=='0x80001000'
    assert reached[0][1:]==reached[1][1:]
    assert {k:v for k,v in reached[0][0].items() if k!='caller'}=={k:v for k,v in reached[1][0].items() if k!='caller'}
    assert encoders[0]==encoders[1]
    assert len(encoders[0])==1 and len(monitors[0].checks)==0
    proofs=[b.proof() for b in bridges];assert proofs[0]==proofs[1]
    assert monitors[0].checks==monitors[1].checks
    saved=bytes(bridges[0].env.files[CARD_PATH])
    if operation=='save':assert sha(saved[512:512+SIZE])==encoders[0][0]['payload_sha256']
    else:
        assert saved==card and decode_checks[0]==decode_checks[1] and len(decode_checks[0])==int(accepted)
        assert protected[0]==protected[1] and len(protected[0])==2
        assert load_monitors[0][0].checks==load_monitors[1][0].checks
        assert load_monitors[0][1].checks==load_monitors[1][1].checks
    assert not bridges[0].env.fds
    transfers=[r for r in bridges[0].env.io if r['op']==('write' if operation=='save' else 'read') and r['requested']==128]
    assert len(transfers)==1784 and [r['file_offset'] for r in transfers]==list(range(512,114688,128))*2
    images=[bytes(b.env.raw_card.image) for b in bridges]
    assert images[0]==images[1]
    raw_traces=[b.env.raw_card.transfers for b in bridges]
    assert raw_traces[0]==raw_traces[1]
    (ROOT/(operation+'-mapping.json.zlib')).write_bytes(zlib.compress(json.dumps(raw_traces[0],separators=(',',':')).encode(),9))
    if operation=='save':
        (ROOT/'operating-menu-save.card-file.bin').write_bytes(saved)
        (ROOT/'operating-menu-save.mcr').write_bytes(images[0])
    else:assert images[0]==(valid_image if accepted else image)

    out=dict(all_passed=True,operation=operation,iterations=4,encoders=encoders[0],decode_checks=decode_checks[0],native_path=reached[0],card=proofs[0],
             save_policy=monitors[0].checks,play=result,source_adapter_sha256=sha(adapter.read_bytes()),
             limits=['Original play CPU checkpoint plus supplied raw-controller streams at SDK frame boundaries.',
                     'No direct menu selection return, save-UI entry jump, encoded payload injection or card status completion.',
                     'Existing paired parent and reached models share native child routines and Unicorn.',
                     'Card BIOS/file/event and prior GPU/SPU/IRQ adapters remain modeled; no physical card claim.',
                     'This controlled retry branch is not added to natural main-20. Replacement, when requested, occurs at the modeled card boundary before the second attempt.',
                     'Physical block mapping is the bounded raw_card.py model; no real BIOS/SIO execution.'])
    if operation=='load':
        out['load_policy']=load_monitors[0][0].checks
        out['confirmation_policy']=load_monitors[0][1].checks
        out['protected_live_fields']=protected[0]
        out['variant']=variant
        out['checksum_accepted']=accepted
        out['external_card_replacement']=accepted
        out['input_image_sha256']=sha(image)
        out['replacement_image_sha256']=sha(valid_image) if accepted else None
    (ROOT/('play-'+operation+'.json')).write_text(json.dumps(out,separators=(',',':'))+'\n')
    for name in ('TOWN0001-retry-'+variant+'-20261111-single.json','TOWN0001-retry-'+variant+'-20261111-single.ram.zlib'):
        source=algo/'source/opened-snapshots-20261028'/name
        if source.exists():shutil.copy2(source,ROOT/name)
    print('original play -> raw menu navigation -> native card '+operation+' -> play passed',flush=True)
finally:
    (ROOT/('menu-'+operation+'-reach-trace.json')).write_text(json.dumps(dict(reached=reached,encoders=encoders,bridges=[b.proof() for b in bridges]),separators=(',',':'))+'\n')
