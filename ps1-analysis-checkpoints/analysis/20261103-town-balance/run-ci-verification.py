#!/usr/bin/env python3
"""Run the town-balance verification plan and preserve every result."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import runpy
import sys
import traceback

def main():
    p=argparse.ArgumentParser()
    p.add_argument("archive")
    args=p.parse_args()
    root=Path(__file__).resolve().parent
    out=root/"results"
    out.mkdir(exist_ok=True)
    model=root/"balance-analysis.py"
    tested_sha=os.environ.get("GITHUB_SHA")
    cache_path=root/"status.json"
    if cache_path.exists():
        cached=json.loads(cache_path.read_text(encoding="utf-8"))
        cases=cached.get("cases",[])
        if (cached.get("status")=="native_validation_passed"
            and cached.get("model_sha256")==hashlib.sha256(model.read_bytes()).hexdigest()
            and len(cases)==33 and all(r.get("passed") for r in cases)
            and all((root/r["result"]).is_file() and
                    hashlib.sha256((root/r["result"]).read_bytes()).hexdigest()==r["result_sha256"]
                    for r in cases)):
            print("Verified cached town-balance results: 33/33; model and result hashes unchanged",flush=True)
            return 0

    records=[]
    fatal=None
    try:
        previous=sys.argv[:]
        sys.argv=[str(model),args.archive]
        try:module=runpy.run_path(str(model),run_name="balance_ci_module")
        finally:sys.argv=previous
        plan=[(name,seed) for name,config in module["CASES"].items() if not config.get("whole") for seed in (0,1,7)]
        plan += [(name,1) for name,config in module["CASES"].items() if config.get("whole")]
        for name,seed in plan:
            filename=name+"-seed-"+str(seed)+".json"
            try:
                data=module["run_balance_case"](name,seed)
                text=json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n"
                (out/filename).write_text(text,encoding="utf-8")
                record=dict(case=name,seed=seed,passed=True,mode=data["mode"],steps=data["steps"],
                            details=data["details"],result="results/"+filename,
                            result_sha256=hashlib.sha256(text.encode()).hexdigest())
            except Exception:
                error=traceback.format_exc()
                (out/(filename+".error.txt")).write_text(error,encoding="utf-8")
                record=dict(case=name,seed=seed,passed=False,error="results/"+filename+".error.txt")
            records.append(record)
            print(json.dumps(record,ensure_ascii=False),flush=True)
    except Exception:
        fatal=traceback.format_exc()
        (out/"fatal.error.txt").write_text(fatal,encoding="utf-8")
    passed=not fatal and bool(records) and all(r["passed"] for r in records)
    status=dict(status="native_validation_passed" if passed else "native_validation_failed",
                tested_commit=tested_sha,model_sha256=hashlib.sha256(model.read_bytes()).hexdigest(),
                source_zip_sha256="afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd",
                total_cases=len(records),passed_cases=sum(r["passed"] for r in records),
                failed_cases=sum(not r["passed"] for r in records),fatal_error=bool(fatal),
                results_saved=True,cases=records,
                scope="27 controlled parent-slice cases plus 6 original whole-function arrival cases; no full-game or physical PS1 claim")
    (root/"status.json").write_text(json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    heading="全条件一致" if passed else "失敗あり・要確認"
    readme=f"""# 会社・商業施設の増減：追加モデル照合

検証状態：{heading}。{len(records)}条件中{sum(r["passed"] for r in records)}条件が一致。
試験したコミット：{tested_sha}。
詳細はstatus.jsonとresults/に保存する。失敗を成功件数へ含めない。

## 復元した規則

- 会社の差 = 住宅カテゴリ3の人口集計 − 会社カテゴリ4の人口集計。
- 商業の差 = 住宅集計を4でゼロ方向切捨て − 商業カテゴリ5の人口集計。
- 住宅集計は会社処理前に取得し、商業処理でも同じ値を使う。
- 差が正・内部レベル9以上なら種類を抽選し、配置可能な1件を配置して探索を終了。
- 差が負・内部レベル3未満なら対象カテゴリの建物を1件解体して探索を終了。
- 差が0では増減しないが、探索開始座標の乱数は消費する。
- 開始座標は乱数%60、乱数%50。地図を折り返して走査する。

## 検証範囲

9種類の境界入力×seed 0/1/7の27例は、原8002D1CCから8002D770までの制御区間試験。
FP/SPを明示して入るため、自然な呼出し到達の証明ではない。
別の6例は原8002BD54の入口から終端まで実行し、その中で同じ増減区間を照合する。
いずれも町24000バイトと乱数を独立計算し、到達した補助処理も照合する。

土地レベルや住民グループを変えた人工的入力をcontrolsへ記録する。
ゲームの自然月送り、GPU/SPU/IRQ、実BIOS、全ゲーム互換性の証明ではない。

## 再実行

Python標準ライブラリのみ。
python balance-analysis.py /path/to/r2.zip company_add_9 1
python balance-analysis.py /path/to/r2.zip whole_level15 1
python run-ci-verification.py /path/to/r2.zip

GitHub側では、保存済み209分割から原ZIPを復元して実行する。
結果のGit保存は解析専用ブランチに限り、main・Claude管理ブランチは変更しない。
"""
    (root/"README.md").write_text(readme,encoding="utf-8")
    return 0 if passed else 1

if __name__=="__main__":
    raise SystemExit(main())
