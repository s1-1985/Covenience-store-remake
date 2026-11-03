"""Add original audio140E8 modes to the live graphics/CD adapter.

Only disc SDK endpoints are supplied. The MIPS loader and its buffer/cache
updates run unmodified. Original sector padding is retained, including writes
that overlap previously loaded graphics buffers.
"""
from newgame_resource_bridge import *
from audio_resources import MODES,destination
from startup_sound_resources import ASSETS as SE_ASSETS
BGM_ASSETS={}
for row in json.loads((R/'bgm-sector-assets-20261029.json').read_text())['assets']:
    blob=(R/row['source_file']).read_bytes();sector=blob+base64.b64decode(row['padding_base64'])
    assert digest(blob)==row['sha256'] and digest(sector)==row['sector_sha256']
    descriptor=encode(row['lba'])+b'\0'+struct.pack('<I',len(blob))+row['path'].split('\\')[-1].split(';')[0].encode().ljust(16,b'\0')
    BGM_ASSETS[row['index'],row['mode']]={**row,'blob':blob,'sector':sector,'descriptor':descriptor}
BGM_ASSETS.update(SE_ASSETS)

class AudioResources:
    def __init__(self,resource):
        self.resource=resource;self.loads=[]
        # Replace just the resource entry observer; shared CD SDK hooks retain
        # their single owner. Graphics and GPU histories remain intact.
        resource.u.hook_del(resource.hooks[0])
        resource.hooks[0]=resource.u.hook_add(UC_HOOK_CODE,self.entry,begin=0x800140e8,end=0x800140e8)
    def entry(self,u,a,n,d):
        r=self.resource;m=r.m;index=u.reg_read(UC_MIPS_REG_A0);mode=u.reg_read(UC_MIPS_REG_A1)
        if mode not in MODES:return r.hook(u,a,n,d)
        key=(index,mode);assert key in BGM_ASSETS and r.active is None
        asset=BGM_ASSETS[key];meta=MODES[mode];dest=destination(*key)
        caches={q['cache']:bytearray(m.read(q['cache'],216)) for q in MODES.values()}
        hit=bool(struct.unpack_from('<I',caches[meta['cache']],index*24+4)[0])
        caches[meta['cache']][index*24:index*24+24]=asset['descriptor']
        graphics_cache=m.read(0x8012ab60,768)
        base=0x8016b600;end=0x801ef000
        assert base<=dest and dest+len(asset['sector'])<=end
        expected=bytearray(m.read(base,end-base));expected[dest-base:dest-base+len(asset['sector'])]=asset['sector']
        state=dict(asset=asset,counts=[0]*4,hit=hit,destination=dest);r.active=state;r.last=asset
        def check():
            assert m.word(meta['pointer'])==dest and m.read(base,end-base)==expected,('audio RAM',key)
            assert m.read(0x800e42b0,24)==asset['descriptor'] and m.read(0x8012ab60,768)==graphics_cache
            assert all(m.read(addr,216)==b for addr,b in caches.items())
            fs,fc,fr,fb=r.failures
            assert state['counts']==[0 if hit else fs+1,fc+1+fr,fr+1,fb+1],(key,state['counts'])
            overlaps=[]
            for oldbase,oldshadow in list(r.shadows.items()):
                begin=max(oldbase,dest);finish=min(oldbase+len(oldshadow),dest+len(asset['sector']))
                if begin<finish:
                    patched=bytearray(oldshadow);patched[begin-oldbase:finish-oldbase]=asset['sector'][begin-dest:finish-dest]
                    r.shadows[oldbase]=bytes(patched);overlaps.append([oldbase,begin,finish-begin])
            if BUF in r.shadows:r.shadow=r.shadows[BUF]
            self.loads.append(dict(key=list(key),cache_hit=hit,counts=state['counts'],destination=dest,
                                   source_sha256=asset['sha256'],sector_sha256=asset['sector_sha256'],sector_bytes=len(asset['sector']),
                                   buffer_region_sha256=digest(expected),graphics_overlaps=overlaps))
            r.active=None
        r.onreturn(u.reg_read(UC_MIPS_REG_RA),check)
