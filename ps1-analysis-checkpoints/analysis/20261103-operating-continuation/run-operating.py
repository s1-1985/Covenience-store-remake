#!/usr/bin/env python3
"""Continue archived native CPU trajectories and preserve complete results."""
import hashlib,json,os,shutil,struct,subprocess,sys,tempfile,traceback,zipfile,zlib
from pathlib import Path

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    root=Path(__file__).resolve().parent
    plan_path=root/"plan.json";plan=json.loads(plan_path.read_text())
    fingerprint=dict(plan_sha256=sha(plan_path),driver_sha256=sha(Path(__file__)))
    status_path=root/"operating-status.json"
    if status_path.exists():
        old=json.loads(status_path.read_text())
        if old.get("status")=="passed" and old.get("fingerprint")==fingerprint and old.get("files") and all(
            (root/r["path"]).is_file() and sha(root/r["path"])==r["sha256"] for r in old["files"]):
            print("Exact operating plan already passed; all result hashes verified",flush=True);return 0
    dest=root/"runs"/plan["batch"];dest.mkdir(parents=True,exist_ok=True)
    records=[]
    status=dict(status="running",fingerprint=fingerprint,tested_commit=os.environ.get("GITHUB_SHA"),
                batch=plan["batch"],results=records,source_zip_sha256=sha(Path(sys.argv[1])))
    assert status["source_zip_sha256"]=="afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd"
    with tempfile.TemporaryDirectory(prefix="ps1-operating-") as temp:
        work=Path(temp)
        with zipfile.ZipFile(sys.argv[1]) as archive:
            for item in archive.infolist():
                if not item.filename.startswith("algorithm-analysis/"):continue
                path=work/item.filename
                if not path.resolve().is_relative_to(work.resolve()):raise ValueError("unsafe archive path")
                if item.is_dir():path.mkdir(parents=True,exist_ok=True)
                else:
                    path.parent.mkdir(parents=True,exist_ok=True)
                    with archive.open(item) as src,path.open("wb") as out:shutil.copyfileobj(src,out)
        algo=work/"algorithm-analysis";snapshots=algo/"source/opened-snapshots-20261028"
        # Previously committed CPU checkpoints retain original bytes.
        for previous in sorted((root/"runs").glob("*/generated/source/opened-snapshots-20261028/*")):
            if previous.is_file():
                target=snapshots/previous.name
                if target.exists() and sha(target)!=sha(previous):raise ValueError("ambiguous checkpoint "+previous.name)
                shutil.copy2(previous,target)
        before={p.relative_to(algo):(p.stat().st_size,p.stat().st_mtime_ns) for p in algo.rglob("*") if p.is_file()}
        try:
            for segment in plan["segments"]:
                source,name,count=segment["source"],segment["output"],segment["updates"]
                assert name.startswith("TOWN0001-ci-") and name.endswith("-single")
                meta=json.loads((snapshots/(source+".json")).read_text())
                ram=zlib.decompress((snapshots/(source+".ram.zlib")).read_bytes())
                assert hashlib.sha256(ram).hexdigest()==meta["ram_sha256"]
                clock=struct.unpack_from("<I",ram,0xcd93c)[0]
                command=[sys.executable,"verify_operating_branch_segment_20261103.py",source,str(count),name]
                rec=dict(source=source,output=name,requested_updates=count,opening_clock=clock,
                         opening_completed_iterations=meta["completed_iterations"],opening_ram_sha256=meta["ram_sha256"],
                         command=command[1:],passed=False)
                records.append(rec);print("Starting "+json.dumps(rec),flush=True)
                with (dest/(name+".log")).open("w") as log:
                    proc=subprocess.run(command,cwd=algo,stdout=log,stderr=subprocess.STDOUT,timeout=900)
                rec["returncode"]=proc.returncode
                if proc.returncode:raise RuntimeError("original continuation failed: "+name)
                data=json.loads((algo/("opened-snapshot-"+name+"-verification-20261103.json")).read_text())
                assert data["all_passed"] and data["iterations_verified"]==count
                row=data["cases"][0];last=row["steps"][-1]
                assert row["opening_clock"]==clock and row["snapshot_sha256"]==meta["ram_sha256"]
                assert last["clock"]==clock+2*count
                final=json.loads((snapshots/(name+".json")).read_text())
                assert final["parent_snapshot_sha256"]==meta["ram_sha256"] and final["completed_iterations"]==meta["completed_iterations"]+count
                rec.update(passed=True,final_clock=last["clock"],final_cash=last["cash"],
                           final_completed_iterations=final["completed_iterations"],final_ram_sha256=final["ram_sha256"],
                           frames=data["frames_verified"],checks={k:len(v) for k,v in row.items() if k.endswith("_checks") and isinstance(v,list)},
                           single_conversion=row["runtime_table_provenance"],appearance_verified=row["single_conversion_appearance_verified"])
                print("Completed "+json.dumps(rec),flush=True)
            for name in plan.get("roundtrips",[]):
                print("Starting native save/title-load/play roundtrip "+name,flush=True)
                with (dest/(name+".roundtrip.log")).open("w") as log:
                    proc=subprocess.run([sys.executable,"verify_single_roundtrip_20261030.py",name],cwd=algo,
                                        stdout=log,stderr=subprocess.STDOUT,timeout=900)
                if proc.returncode:raise RuntimeError("native roundtrip failed: "+name)
                data=json.loads((algo/("title-native-load-roundtrip-"+name+"-verification-20261030.json")).read_text())
                assert data["all_passed"]
                row=data["cases"][0]
                assert row["payload_valid"] and row["runtime_table_provenance"]=="single_conversion"
                assert row["runtime_tables_preserved_after_resume"]["both_cpus"]
                status.setdefault("roundtrips",[]).append(dict(snapshot=name,passed=True,payload_sha256=row["payload_sha256"],
                         frames=data["frames_verified"],runtime_tables=row["runtime_tables_preserved_after_resume"]))
                print("Native save/load passed "+name,flush=True)
            if plan.get("card_chain"):
                print("Starting original card file chain diagnostics",flush=True)
                with (dest/"card-chain.log").open("w") as log:
                    proc=subprocess.run([sys.executable,str(root/"audit-card-file-chain.py"),str(algo),*plan["card_chain"]],
                                        cwd=algo,stdout=log,stderr=subprocess.STDOUT,timeout=900)
                if proc.returncode:raise RuntimeError("original card-file chain failed; see card-chain.log")
                chain=json.loads((algo/"source/card-file-chain-20261103-ci/summary.json").read_text())
                assert chain["all_passed"]
                status["card_chain"]=dict(total=chain["total"],passed=True,cases=chain["cases"])
        except Exception:
            status["error"]=traceback.format_exc();(dest/"failure.txt").write_text(status["error"])
        finally:
            for path in algo.rglob("*"):
                if not path.is_file() or "__pycache__" in path.parts or path.suffix==".pyc":continue
                rel=path.relative_to(algo)
                if before.get(rel)==(path.stat().st_size,path.stat().st_mtime_ns):continue
                output=dest/"generated"/rel;output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,output)
    status["status"]="passed" if len(records)==len(plan["segments"]) and all(r["passed"] for r in records) and "error" not in status else "failed"
    status["files"]=[dict(path=str(p.relative_to(root)),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(dest.rglob("*")) if p.is_file()]
    status["limits"]=["CPU snapshots and controlled SDK adapters; no physical GPU/SPU/IRQ restoration.",
                      "Independent parent and reached monitor checks with original native children; not a whole-game independent reimplementation.",
                      "No clock, roster, cash or RNG injection after restoring each source state.",
                      "Branches have different UI/RNG histories; revenue differences are not causal estimates."]
    status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n")
    (dest/"batch-status.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n")
    lines=["# 営業状態からの継続検証","","状態："+status["status"],"",
           "原ZIP内の実行コードを変更せず使用し、各更新で原処理と既存の独立モデル・監視を照合した。","",
           "| 開始状態 | 追加更新 | 時計 | 最終現金 | 一致 |","|---|---:|---:|---:|---|"]
    for r in records:lines.append("| "+r["source"]+" | "+str(r["requested_updates"])+" | "+str(r["opening_clock"])+"→"+str(r.get("final_clock","未完"))+" | "+str(r.get("final_cash","未完"))+" | "+str(r["passed"])+" |")
    lines+=["","詳細・監視件数・ファイルSHA256はoperating-status.json。ログ、結果JSON、再開可能なCPU RAMとメタデータはruns/へ保存。","時計・資金・従業員・乱数の注入なし。描画と音声は既存のSDK境界を使用し、物理機の完全再現とは扱わない。","枝の操作履歴と乱数は異なるため、売上差を店長交代だけの効果とは解釈しない。"]
    (root/"README.md").write_text("\n".join(lines)+"\n")
    return 0 if status["status"]=="passed" else 1
if __name__=="__main__":raise SystemExit(main())
