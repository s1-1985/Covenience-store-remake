#!/usr/bin/env python3
"""Resume actual operating RAM and navigate original menus to native card write."""
import ast,difflib,hashlib,json,runpy,sys,types
from pathlib import Path
REPORT=Path(__file__).resolve().parent
ANALYSIS=REPORT.parent
scenario=sys.argv[2] if len(sys.argv)>2 else 'create'
assert scenario in ('create','retry','cancel')
ROOT=REPORT/scenario;ROOT.mkdir(exist_ok=True)
algo=Path(sys.argv[1]).resolve();sys.path.insert(0,str(algo))
operation='save'
assert operation in ('save','load')
from check_machine import *
from save_codec import BASE,SIZE,FIELDS,encode,valid
from caller_connection_harness import Memory
from verify_schedule_selector_frames import seq
from unicorn import UC_HOOK_CODE
import verify_opened_snapshot_play_20261028 as play
def sha(b):return hashlib.sha256(b).hexdigest()
reference=runpy.run_path(str(ANALYSIS/'20261103-native-file-recovery/native-file-analysis.py'),run_name='file_reference')
LogicalFiles,CARD_PATH=reference['LogicalFiles'],reference['PATH']
adapter=ANALYSIS/'20261104-long-continuation/native-title-card-chain.py'
classes=[n for n in ast.parse(adapter.read_text()).body if isinstance(n,ast.ClassDef)]
exec(compile(ast.Module(body=classes,type_ignores=[]),str(adapter),'exec'),globals())
from source_save_write_monitor_20261031 import policy as success_policy
class AttemptMonitor:
    """Independent selected init2-create / init5-retry / init0-write call policies."""
    def __init__(self,u,runner,payload):
        self.checks=[];self.active=None
        statuses=[2] if scenario=='create' else [5,0] if scenario=='retry' else [5]
        counts={0x80089ca4:1,0x80064e4c:1,0x80018940:2,0x800157b4:0,0x8004ea68:0,
                0x8004e494:3,0x80018a5c:0,0x8007b1f8:1,0x8007adf8:1,0x8007b8a4:0,0x80050fc8:3}
        sites={};data=EXE.read_bytes()
        for pc in range(0x800505a0,0x80050b04,4):
            word=struct.unpack_from('<I',data,pc-0x80010000+2048)[0]
            target=0x80000000|((word&0x3ffffff)<<2)
            if word>>26==3 and target in counts:sites[pc]=target
        def observe(z,pc,size,d):
            if pc==0x800505a0:
                assert self.active is None
                status=statuses[len(self.checks)];expected=success_policy(0)
                index=next(i for i,row in enumerate(expected) if row[0]==0x8007b1f8)+2
                if status==2:expected[index:index]=[[0x8007b8a4,[]],[0x80089ca4,[2]]]
                if status==5:expected=expected[:index]+[[0x800157b4,[]],[0x80050fc8,[5,64,64]]]
                self.active=[]
                def finish():
                    assert self.active==expected,('attempt policy',status,self.active,expected)
                    value=z.reg_read(UC_MIPS_REG_V0)
                    assert value==(5 if status==5 else 0)
                    self.checks.append(dict(init_status=status,result=value,calls=self.active,payload_sha256=sha(payload())))
                    self.active=None
                runner.onreturn(z.reg_read(UC_MIPS_REG_RA),finish)
            elif self.active is not None:
                target=sites[pc]
                self.active.append([target,[z.reg_read(r) for r in (UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2)[:counts[target]]]])
        self.hooks=[u.hook_add(UC_HOOK_CODE,observe,begin=pc,end=pc) for pc in (0x800505a0,*sites)]
bridges=[];monitors=[];encoders=[];reached=[];hooks=[];load_monitors=[];decode_checks=[];initial_transfers=[]
original_runner=play.BackgroundCategoryRunner
card=(ANALYSIS/'20261104-long-continuation/TOWN0001-ci-main-08-single.card-file.bin').read_bytes()
def runner_factory(u,*args,**kwargs):
    r=original_runner(u,*args,**kwargs);m=Memory(u);expected=[None];enc=[];trace=[]
    files={} if scenario=='create' else {CARD_PATH:card}
    responses={'info':[1,1,1,0]} if scenario=='retry' else {'info':[1]} if scenario=='cancel' else None
    bridge=NativeCardBridge(u,r,files,responses);bridge.cpu.allow_ram_mirror=True
    transfers=[];initial_transfers.append(transfers);read=bridge.cpu.read
    def capture_read(address,size):
        data=read(address,size);physical=address&0x1fffffff
        if physical<0x800000 and physical+size>0x200000:
            transfers.append(dict(address=address,data=data))
        return data
    bridge.cpu.read=capture_read
    monitor=AttemptMonitor(u,r,lambda:expected[0])
    bridges.append(bridge);monitors.append(monitor);encoders.append(enc);reached.append(trace)
    decoded=[];decode_checks.append(decoded)
    if operation=='load':
        from load_read_control_20261030 import LoadReadMonitor
        from load_confirmation_20261029 import LoadConfirmationMonitor
        load_monitors.append((LoadReadMonitor(u,r,0,0,True),LoadConfirmationMonitor(u,r)))
    def observe(z,a,n,d):
        trace.append(dict(function=hex(a),caller=hex(z.reg_read(UC_MIPS_REG_RA)),clock=m.word(0x800cd93c),active=m.word(0x801398b4),processed=m.word(0x800cd884)))
        if a==0x8006b81c:
            expected[0]=bytes(encode(bytearray(m.read(BASE,SIZE)),m.read))
            def finish():
                assert m.read(BASE,SIZE)==expected[0] and valid(expected[0])
                enc.append(dict(payload_sha256=sha(expected[0]),clock=m.word(0x800cd93c),cash=m.word(0x800cd9f8)))
            r.onreturn(z.reg_read(UC_MIPS_REG_RA),finish)
        if a==0x8006bc40:
            payload=m.read(BASE,SIZE);assert payload==card[512:512+SIZE] and valid(payload)
            def finish_decode():
                assert all(m.read(address,size)==payload[offset:offset+size] for offset,address,size in FIELDS)
                decoded.append(dict(payload_sha256=sha(payload),regions=len(FIELDS)))
            r.onreturn(z.reg_read(UC_MIPS_REG_RA),finish_decode)
    for a in (0x8005fe54,0x80062484,0x8006b81c,0x8004eeb8,0x8004efd0,0x800501fc,0x800505a0,0x80051174,0x80051524,0x8006bc40):hooks.append((u,u.hook_add(UC_HOOK_CODE,observe,begin=a,end=a)))
    return r
play.BackgroundCategoryRunner=runner_factory
plans={0x8004e578:[seq([0x4000]*4+[32])+[0]*150,seq([64])+[0]*150],
       0x8004efd0:[seq([0x1000,0x1000,32])+[0]*150]+([seq([0x800])+[0]*150] if scenario=='cancel' else []),
       0x800501fc:[seq(([32,32,64] if scenario=='retry' else [32,64]))+[0]*150],
       0x80051174:[seq([32,64])+[0]*150],
       0x80051524:[[0]*12+seq([64])+[0]*200],
       0x800505a0:([[0]*12+seq([64])+[0]*150] if scenario=='create' else [[0]*2+seq([64])+[0]*150]+([[0]*12+seq([64])+[0]*150] if scenario=='retry' else []))}
try:
    result=play.compare('TOWN0001-ci-main-09-single',4,actions={0:128},native_music=True,
        input_plans=plans,finance_monitor=True,event_monitor=True,refill_monitor=True,
        customer_monitor=True,whole_town_monitor=True,staff_loop_monitor=True,
        progress_snapshot='TOWN0001-menu-'+scenario+'-recovery-20261105-single',progress_file=str(ROOT/('menu-'+operation+'-progress.json')))
    # The independent parent invokes its native child through its sentinel RA.
    # Assert the exact two wrapper callers, then require every nested call equal.
    assert reached[0][0]['caller']=='0x8005d06c' and reached[1][0]['caller']=='0x80001000'
    assert reached[0][1:]==reached[1][1:]
    assert {k:v for k,v in reached[0][0].items() if k!='caller'}=={k:v for k,v in reached[1][0].items() if k!='caller'}
    assert encoders[0]==encoders[1]
    assert len(encoders[0])==1 and len(monitors[0].checks)==(2 if scenario=='retry' else 1)
    proofs=[b.proof() for b in bridges]
    assert {k:v for k,v in proofs[0].items() if k!='ram_mirror_reads'}=={k:v for k,v in proofs[1].items() if k!='ram_mirror_reads'}
    initial_comparison=[]
    assert len(initial_transfers[0])==len(initial_transfers[1])
    for index,(a,b) in enumerate(zip(initial_transfers[0],initial_transfers[1])):
        assert a['address']==b['address'] and len(a['data'])==len(b['data'])==114688
        assert a['data'][:512]==b['data'][:512]
        assert sha(a['data'])==proofs[0]['ram_mirror_reads'][index]['sha256']
        assert sha(b['data'])==proofs[1]['ram_mirror_reads'][index]['sha256']
        assert {k:v for k,v in proofs[0]['ram_mirror_reads'][index].items() if k!='sha256'}=={k:v for k,v in proofs[1]['ram_mirror_reads'][index].items() if k!='sha256'}
        differences=[dict(file_offset=i,native=x,reference=y) for i,(x,y) in enumerate(zip(a['data'],b['data'])) if x!=y]
        assert all(d['file_offset']>=512 for d in differences)
        (ROOT/('initial-native-'+str(index)+'.bin')).write_bytes(a['data'])
        (ROOT/('initial-reference-'+str(index)+'.bin')).write_bytes(b['data'])
        initial_comparison.append(dict(header512_equal=True,differences=differences,
            native_sha256=sha(a['data']),reference_sha256=sha(b['data']),
            scope='Temporary initial file fill differs only in body bytes later fully overwritten by the 892 checked writes. Final entire file and all I/O are compared without normalization.'))
    assert monitors[0].checks==monitors[1].checks
    saved=bytes(bridges[0].env.files[CARD_PATH])
    if scenario=='cancel':assert saved==card
    elif operation=='save':assert sha(saved[512:512+SIZE])==encoders[0][0]['payload_sha256']
    else:
        assert saved==card and decode_checks[0]==decode_checks[1] and len(decode_checks[0])==1
        assert load_monitors[0][0].checks==load_monitors[1][0].checks
        assert load_monitors[0][1].checks==load_monitors[1][1].checks
    assert not bridges[0].env.fds
    transfers=[r for r in bridges[0].env.io if r['op']==('write' if operation=='save' else 'read') and r['requested']==128]
    assert len(transfers)==(0 if scenario=='cancel' else 892)
    if scenario!='cancel':assert [r['file_offset'] for r in transfers]==list(range(512,114688,128))
    assert saved==bytes(bridges[1].env.files[CARD_PATH])
    if scenario!='cancel':assert sha(saved[512:])==bridges[0].native_calls[-1]['body_sha256']
    if operation=='save':(ROOT/'operating-menu-save.card-file.bin').write_bytes(saved)
    out=dict(all_passed=True,scenario=scenario,operation=operation,iterations=4,encoders=encoders[0],decode_checks=decode_checks[0],native_path=reached[0],card=proofs[0],
             save_policy=monitors[0].checks,play=result,initial_transfer_comparison=initial_comparison,source_adapter_sha256=sha(adapter.read_bytes()),
             limits=['Original play CPU checkpoint plus supplied raw-controller streams at SDK frame boundaries.',
                     'No direct menu selection return, save-UI entry jump, encoded payload injection or card status completion.',
                     'Existing paired parent and reached models share native child routines and Unicorn.',
                     'Card BIOS/file/event and prior GPU/SPU/IRQ adapters remain modeled; no physical card claim.',
                     'This menu branch preserves its own clock/RNG/UI history and does not replace natural main-09.'])
    if operation=='load':out['load_policy']=load_monitors[0][0].checks
    (ROOT/('play-'+operation+'.json')).write_text(json.dumps(out,separators=(',',':'))+'\n')
    print('original play -> raw menu navigation -> native card '+scenario+' -> play passed',flush=True)
finally:
    (ROOT/('menu-'+operation+'-reach-trace.json')).write_text(json.dumps(dict(reached=reached,encoders=encoders,bridges=[b.proof() for b in bridges]),separators=(',',':'))+'\n')
