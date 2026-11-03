#!/usr/bin/env python3
"""Recover original continuation source references without executing them."""
import ast
import hashlib
import json
from pathlib import Path
import sys
import zipfile

def main():
    target=Path(__file__).resolve().parent
    refs=target/"source-reference"
    refs.mkdir(exist_ok=True)
    records=[]
    roots=["verify_operating_branch_segment_20261103.py","main_update_native_oracle.py",
           "requirements-verified.txt","verify_single_roundtrip_20261030.py"]
    with zipfile.ZipFile(sys.argv[1]) as archive:
        names=set(archive.namelist())
        prefix="algorithm-analysis/"
        pending=[(name,0) for name in roots]
        seen=set()
        while pending:
            name,depth=pending.pop(0)
            if name in seen:continue
            seen.add(name)
            source=prefix+name
            if source not in names:
                records.append(dict(path=source,missing=True))
                continue
            data=archive.read(source)
            (refs/name).write_bytes(data)
            records.append(dict(path=source,output="source-reference/"+name,
                                bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),depth=depth))
            if name.endswith(".py") and depth<3:
                tree=ast.parse(data.decode("utf-8-sig"))
                for node in ast.walk(tree):
                    imports=[]
                    if isinstance(node,ast.Import):imports=[i.name for i in node.names]
                    elif isinstance(node,ast.ImportFrom) and node.module:imports=[node.module]
                    for imported in imports:
                        child=imported.split(".")[0]+".py"
                        if prefix+child in names:pending.append((child,depth+1))
        snapshots=[]
        for directory in ("opened-snapshots-20261028","interrupted-snapshots-20261103"):
            path=prefix+"source/"+directory+"/TOWN0001-nov3-two-own-nextday-single.json"
            if path not in names:continue
            raw=archive.read(path)
            obj=json.loads(raw)
            schema={}
            for key,value in obj.items():
                if value is None or isinstance(value,(int,float,bool)):schema[key]=value
                elif isinstance(value,str):schema[key]=value if len(value)<300 else dict(type="str",length=len(value),prefix=value[:60])
                elif isinstance(value,dict):
                    schema[key]=dict(type="dict",keys=list(value),scalars={k:v for k,v in value.items() if v is None or isinstance(v,(int,float,bool))})
                elif isinstance(value,list):schema[key]=dict(type="list",length=len(value),first=value[:3] if all(isinstance(i,(int,float,bool,str)) for i in value[:3]) else None)
                else:schema[key]=dict(type=type(value).__name__)
            snapshots.append(dict(path=path,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),schema=schema))
    report=dict(status="source_inspection_only",source_zip_sha256="afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd",files=records,snapshots=snapshots)
    (target/"inspection.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (target/"README.md").write_text("# 営業継続解析\n\n原ZIP内の継続実行コードを同一バイトで取り出し、依存関係と開始スナップショットの構造を保存した。\n現段階はコードの確認用であり、新しい営業更新の実行結果ではない。\n各参照ファイルの原パス・SHA256はinspection.jsonに記録する。\n",encoding="utf-8")
    print(json.dumps(dict(source_files=len(records),snapshots=len(snapshots)),ensure_ascii=False))

if __name__=="__main__":main()
