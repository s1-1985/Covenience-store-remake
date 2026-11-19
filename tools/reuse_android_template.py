#!/usr/bin/env python3
"""Reuse engine/Android resources from a prior Godot APK, without game assets.
Restore the app-label placeholder expected by Godot4.6 _fix_resources().
No signing key, game data or former APK signatures are copied.
"""
import argparse,struct,zipfile
from pathlib import Path

def restore_label(data, old_label):
    pos=struct.unpack_from('<H',data,2)[0]
    typ,header,size,count,styles,flags,start,style_start=struct.unpack_from('<HHI5I',data,pos)
    assert (typ,header,styles,flags,style_start)==(1,28,0,0,0), 'Expected Godot UTF16 resource string pool'
    offsets=struct.unpack_from('<%dI'%count,data,pos+header)
    result=bytearray();new_offsets=[];changed=0
    for off in offsets:
        p=pos+start+off;n=struct.unpack_from('<H',data,p)[0];p+=2
        if n&0x8000:n=((n&0x7fff)<<16)|struct.unpack_from('<H',data,p)[0];p+=2
        text=data[p:p+2*n].decode('utf-16le')
        if text==old_label:text='godot-project-name';changed+=1
        raw=text.encode('utf-16le');units=len(raw)//2;assert units<32768
        new_offsets.append(len(result));result.extend(struct.pack('<H',units)+raw+b'\0\0')
    assert changed>0,'Old app label not found'
    result.extend(bytes((-len(result))%4))
    pool=bytearray(data[pos:pos+header]);struct.pack_into('<I',pool,4,start+len(result))
    pool.extend(struct.pack('<%dI'%count,*new_offsets));assert len(pool)==start
    pool.extend(result)
    rebuilt=bytearray(data[:pos])+pool+data[pos+size:]
    struct.pack_into('<I',rebuilt,4,len(rebuilt))
    return rebuilt

def main():
    p=argparse.ArgumentParser();p.add_argument('previous_apk',type=Path);p.add_argument('output_template',type=Path);p.add_argument('--old-label',required=True);a=p.parse_args()
    a.output_template.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.previous_apk) as src,zipfile.ZipFile(a.output_template,'w') as out:
        for entry in src.infolist():
            if entry.filename.startswith(('assets/','META-INF/')):continue
            data=src.read(entry.filename)
            if entry.filename=='resources.arsc':data=restore_label(data,a.old_label)
            out.writestr(entry,data)
    print('Reused Android template; removed former assets/signatures and restored label placeholder')
if __name__=='__main__':main()
