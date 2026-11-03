"""Restore a verified CPU snapshot and reinstall explicitly modeled hardware boundaries."""
from check_machine import *
from caller_connection_harness import Memory
from category_background_frame_harness import BackgroundCategoryRunner
from title_resources_20261028 import NativeNewgameResources,ASSETS,BUF
from async_initial_voice_bridge import AsyncInitialVoice
from native_upload_probe import PATCHES
from native_music_bridge_20261029 import NativeMusic
from menu_generator_monitor import MenuGeneratorMonitor
import zlib,hashlib,json
R=Path(__file__).resolve().parent
def restore(name,plans):
    root=R/'source/opened-snapshots-20261028';meta=json.loads((root/(name+'.json')).read_text())
    ram=zlib.decompress((root/(name+'.ram.zlib')).read_bytes())
    assert hashlib.sha256(ram).hexdigest()==meta['ram_sha256']
    assert hashlib.sha256(EXE.read_bytes()).hexdigest()==meta['source_executable_sha256']
    u=machine();u.mem_write(0,ram)
    for reg,value in meta['registers'].items():u.reg_write(int(reg),value)
    exe=EXE.read_bytes()
    for a in PATCHES:Memory(u).write(a,exe[a-0x80010000+2048:a-0x80010000+2052])
    runner=BackgroundCategoryRunner(u,meta['bank'],plans,allow_scaled=True,table_address=0x800e3b20+64*meta['bank'])
    resource=NativeNewgameResources(u,runner,native_gpu=True,preserve_cache=True,stack_floor=0x801ff000)
    resource.shadows={int(a,16):bytes.fromhex(b) for a,b in meta['resource_shadows'].items()}
    resource.buffer_assets={int(a,16):ASSETS[tuple(k)] for a,k in meta['resource_assets'].items()}
    resource.shadow=resource.shadows.get(BUF);resource.buffer_asset=resource.buffer_assets.get(BUF)
    voice=AsyncInitialVoice(u,runner,base=None,profile=meta['bank']);voice.registered=meta['voice_registered'];voice.allowed_voices=range(131)
    music=NativeMusic(u,resource);menu=MenuGeneratorMonitor(u,runner,192,9216,272)
    return u,runner,resource,voice,music,menu,meta
