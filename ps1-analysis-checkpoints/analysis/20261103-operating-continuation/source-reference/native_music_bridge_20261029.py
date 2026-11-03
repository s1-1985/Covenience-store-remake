"""Observe native65100 with actual resources and controlled SPU/sequence APIs."""
from check_machine import *
from caller_connection_harness import Memory
from audio_resources import destination
from bgm_resource_bridge_20261029 import AudioResources,BGM_ASSETS
from music_control import change
from se_initialization import ADDRESSES,cleanup,initialize
from unicorn import UC_HOOK_CODE
SDK_ARGS={0x8008ecf4:1,0x8008d5e8:1,0x8008ef24:1,0x8008f000:2,0x8008f4a4:2,
          0x8008f564:1,0x8008b458:2,0x8008aa60:2,0x8008ea44:3,0x8008eaec:3,0x8008b000:3,0x8008eb1c:4}
DIRECT={0x8006558c:0,0x800140e8:2,0x80089ca4:1,**SDK_ARGS}
class NativeMusic:
    def __init__(self,u,resource,bank_result=31,sequence_result=32,own_wait=False):
        self.u=u;self.m=Memory(u);self.resource=resource;self.audio=AudioResources(resource)
        self.bank_result=bank_result;self.sequence_result=sequence_result;self.own_wait=own_wait
        self.checks=[];self.cleanup_checks=[];self.volume=[];self.sdk=[];self.active=None;self.cleaning=None;self.hooks=[]
        self.se_active=None;self.se_checks=[];self.se_results={8:(17,23),7:(18,24)}
        for a in dict.fromkeys((0x80065100,0x800651d8,0x80065320,0x80065350,0x800140e8,*DIRECT)):self.hooks.append(u.hook_add(UC_HOOK_CODE,self.hook,begin=a,end=a))
    def state(self):
        m=self.m
        return dict(current=m.word(0x800cd990),sequence=int.from_bytes(m.read(0x800cd7f8,2),'little'),bank=int.from_bytes(m.read(0x800cda04,2),'little'),
                    seq_data=m.word(0x800cd810),vh_data=m.word(0x800cd81c),vb_data=m.word(0x800cd814))
    def hook(self,u,a,n,d):
        regs=(UC_MIPS_REG_A0,UC_MIPS_REG_A1,UC_MIPS_REG_A2,UC_MIPS_REG_A3)
        a0=u.reg_read(UC_MIPS_REG_A0);a1=u.reg_read(UC_MIPS_REG_A1);ra=u.reg_read(UC_MIPS_REG_RA)
        if a==0x80065350:
            assert self.se_active is None
            before=[int.from_bytes(self.m.read(p,2),'little') for p in ADDRESSES];expected=list(before);before_bgm=self.m.word(0x800cd990)
            wanted=[]
            for event in initialize(expected,self.se_results):
                if event[0]=='resource':wanted.append(['resource',event[1],event[2]])
                else:wanted.append(['sdk',event[1],[v&0xffffffff for v in event[2]]])
            current=dict(before=before,expected=expected,wanted=wanted,calls=[],key=None);self.se_active=current
            def check_se():
                actual=[int.from_bytes(self.m.read(p,2),'little') for p in ADDRESSES]
                assert actual==expected and current['calls']==wanted,(actual,expected,current['calls'],wanted)
                assert self.m.word(0x800cd990)==before_bgm
                self.se_checks.append(dict(before=before,after=expected,current_BGM=before_bgm,calls=current['calls']));self.se_active=None
            self.resource.onreturn(ra,check_se);return
        if a==0x800140e8:
            if self.active is not None and 0x80065100<=ra<=0x80065328:self.active['calls'].append([a,[a0,a1]])
            if self.se_active is not None:
                assert a0 in (7,8) and a1 in (1,2,4)
                self.se_active['key']=a0;self.se_active['calls'].append(['resource',a0,a1])
            return
        if a in (0x800651d8,0x80065320):
            # The live input/CD callback adapter changes RA at the VSync SDK
            # entry. Observe the original JAL before that adapter takes over.
            assert self.active is not None and a0==0
            self.active['calls'].append([0x80089ca4,[0]]);return
        if a==0x80065100:
            assert self.active is None
            initial=self.state();expected=dict(initial)
            if a0!=0xffffffff and a0!=initial['current']:
                assert 0<=a0<=6
                for key,mode in [('seq_data',4),('vh_data',1),('vb_data',2)]:expected[key]=destination(a0,mode)
            wanted=change(expected,a0,a1,self.bank_result,self.sequence_result)
            wanted=[[x,[v&0xffffffff for v in args]] for x,args in wanted]
            current=dict(request=[a0,a1],before=initial,wanted=wanted,calls=[],expected=expected,load_start=len(self.audio.loads))
            self.active=current
            def check():
                assert current['calls']==wanted,(current['calls'],wanted)
                assert self.state()==expected,(self.state(),expected)
                self.checks.append(dict(request=current['request'],before=initial,after=expected,calls=current['calls'],
                                        resource_loads=self.audio.loads[current['load_start']:]))
                self.active=None
            self.resource.onreturn(ra,check);return
        args=[u.reg_read(r) for r in regs[:DIRECT[a]]]
        if a!=0x80089ca4 and self.active is not None and 0x80065100<=ra<=0x80065328:self.active['calls'].append([a,args])
        if a==0x8006558c:
            handles=[int.from_bytes(self.m.read(p,2),'little') for p in ADDRESSES];expected=list(handles)
            wanted=[[q,[v&0xffffffff for v in values]] for _,q,values in cleanup(expected)];trace=[];self.cleaning=trace
            def check():
                assert [int.from_bytes(self.m.read(p,2),'little') for p in ADDRESSES]==expected and trace==wanted
                self.cleanup_checks.append(dict(before=handles,after=expected,calls=trace));self.cleaning=None
            self.resource.onreturn(ra,check);return
        if a==0x800140e8:return
        if a==0x80089ca4:
            if not self.own_wait:return
            value=0
        else:
            if self.cleaning is not None and 0x8006558c<=ra<0x80065678:self.cleaning.append([a,args])
            self.sdk.append([a,args])
            if self.se_active is not None:self.se_active['calls'].append(['sdk',a,args])
            if a==0x8008eaec:self.volume.append(args)
            # Inspect the exact disk-derived data passed to each physical API.
            if a in (0x8008f000,0x8008f4a4,0x8008b458,0x8008b000):
                assert self.active or self.se_active
                mode={0x8008f000:1,0x8008f4a4:2,0x8008b458:4,0x8008b000:4}[a]
                index=self.se_active['key'] if self.se_active is not None else self.active['request'][0]
                asset=BGM_ASSETS[index,mode]
                assert a0==destination(index,mode)
                assert self.m.read(a0,len(asset['blob']))==asset['blob']
            if self.se_active is not None and a in (0x8008f000,0x8008b000):
                value=self.se_results[self.se_active['key']][0 if a==0x8008f000 else 1]
            else:value=self.bank_result if a==0x8008f000 else self.sequence_result if a==0x8008b458 else 0
        u.reg_write(UC_MIPS_REG_V0,value&0xffffffff);u.reg_write(UC_MIPS_REG_PC,ra)
    def proof(self):
        assert self.active is None and self.cleaning is None and self.se_active is None
        return dict(calls=self.checks,cleanup=self.cleanup_checks,SE_initialization=self.se_checks,SDK_requests=self.sdk,resource_loads=self.audio.loads,
                    limits=['Original65100/6558C/140E8 with independent switching/cleanup/cache/buffer checks and original21 BGM file bytes plus sector padding.',
                            'SPU bank/sequence allocation and playback APIs return controlled handles; no audio waveform or physical CD/IRQ timing proof.'])
    def dispose(self):
        for h in self.hooks:self.u.hook_del(h)
        self.hooks=[]
