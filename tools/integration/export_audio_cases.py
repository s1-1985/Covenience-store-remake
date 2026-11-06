"""Small original-model audio boundary expectations; offline only."""
from pathlib import Path
import argparse, itertools, json, struct, sys

def main():
    p=argparse.ArgumentParser();p.add_argument('analysis',type=Path);a=p.parse_args().analysis
    sys.path.insert(0,str(a.resolve()))
    from audio_dispatch import dispatch
    from save_load_control import settings
    exe=(a/'source/SLPS_007.82').read_bytes()
    offset=0x800b8cb8-0x80010000+0x800
    table=[struct.unpack_from('<III',exe,offset+i*12) for i in range(131)]
    cases=[]
    for identifier,guard,enabled in itertools.product([-1,0,15,16,27,28,157,158,159],[-1,6],[0,1,255]):
        state=dict(disabled=0,status=0,callback=0,start=0,end=0,current=0,retry=0,delay=0,mode=bytes(4))
        calls=dispatch(state,identifier,guard,enabled,11,22,table,1513,0)
        expected=dict(kind='none')
        if guard!=6:
            if identifier==-1:expected=dict(kind='stop')
            elif identifier<28:
                expected=dict(kind=('se' if identifier<16 else 'vos')if enabled==1 else 'none',index=identifier if identifier<16 else identifier-16)
            else:expected=dict(kind='xa',index=identifier-28)
        # Verify independent native-model request correspondence, not only a
        # reimplementation of the GDScript return shape.
        if expected['kind'] in ('se','vos'):assert ('track_play',11 if identifier<16 else 22,expected['index'],1,1) in calls
        if expected['kind']=='xa':assert ('start',expected['index']) in calls
        if expected['kind']=='none':assert not calls
        cases.append(dict(identifier=identifier,guard=guard,enabled=enabled,expected=expected))
    settings_cases=[]
    for high,low in itertools.product(range(3),range(4)):
        bits=high*256+low;writes={};calls=[]
        def read(address,count):
            if address==0x800cd898:return struct.pack('<H',bits)
            return struct.pack('<i',[-1,2,3,4][(address-0x80099864)//4])
        settings(read,lambda address,b:writes.update({address:b}),lambda address,*args:calls.append((address,args)))
        settings_cases.append(dict(bits=bits,expected=dict(se_enabled=writes[0x800cd834][0],monthly_enabled=writes[0x800cd835][0],bgm_choice=high,bgm_id=calls[0][1][0])))
    native=json.loads((a/'main-audio-selection-verification.json').read_text())
    assert native['all_passed']
    main_cases=[{k:r[k]for k in ('flags','enabled','selected','extra','month','requested_ids')}for r in native['cases']]
    root=Path(__file__).resolve().parents[2]
    (root/'game/tests/fixtures/source_audio.json').write_text(json.dumps(dict(dispatch=cases,settings=settings_cases,main=main_cases),separators=(',',':'))+'\n')
    print('audio cases',len(cases),len(settings_cases),len(main_cases))

if __name__=='__main__':main()
