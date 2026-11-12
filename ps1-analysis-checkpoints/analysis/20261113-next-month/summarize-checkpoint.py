#!/usr/bin/env python3
"""Update the report/latest pointer from completed, hash-verified evidence only."""
import hashlib,json,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent;BASE=ROOT.parent.parent
rows=[json.loads(p.read_text()) for p in sorted(ROOT.glob('TOWN0001-ci-main-*-single.audit.json'))]
assert rows and all(r['passed'] for r in rows)
assert rows[0]['source']=='TOWN0001-ci-main-25-single' and rows[0]['source_ram_sha256']=='236b0a2fffe3a27c229c63565cda9b11228fbdebd3c063e2ec82bb6d011716fe'
for a,b in zip(rows,rows[1:]):assert a['output']==b['source'] and a['final_ram_sha256']==b['source_ram_sha256']
manifest=json.loads((ROOT/'evidence-encoding.json').read_text())
for e in manifest['files']:
 b=(ROOT/e['stored_path']).read_bytes();assert hashlib.sha256(b).hexdigest()==e['stored_sha256']
 raw=zlib.decompress(b) if e['encoding']=='zlib' else b
 assert hashlib.sha256(raw).hexdigest()==e['sha256'] and len(raw)==e['bytes']
last=rows[-1];name=last['output'];prefix='analysis/20261113-next-month/encoded/evidence/source/opened-snapshots-20261028/'
meta=json.loads(zlib.decompress((BASE/(prefix+name+'.json.zlib')).read_bytes()))
ram=zlib.decompress((BASE/(prefix+name+'.ram.zlib')).read_bytes())
assert len(ram)==2097152 and hashlib.sha256(ram).hexdigest()==last['final_ram_sha256']==meta['ram_sha256']
assert meta['completed_iterations']==last['completed_iterations']
monthly={}
for kind in ('rival','town'):
 p=ROOT/('natural-'+kind+'-audit.json')
 if p.exists():
  d=json.loads(p.read_text());assert d['all_passed'] and d['cases'];monthly[kind]=d
complete=len(rows)==6
summary=dict(completed_segments=len(rows),planned_segments=6,verified_updates=sum(r['updates'] for r in rows),completed_plan=complete,latest=dict(snapshot=name,clock=last['clock_after'],completed_iterations=last['completed_iterations'],cash=last['cash_after'],ram_sha256=last['final_ram_sha256']),independent_monthly_audits=list(monthly),evidence_files=len(manifest['files']))
(ROOT/'checkpoint-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
latest=json.loads((BASE/'LATEST-ANALYSIS.json').read_text());latest.update(date_jst='2026-11-13',**summary['latest'],metadata=prefix+name+'.json.zlib',compressed_ram=prefix+name+'.ram.zlib',report='analysis/20261113-next-month/README.md',limits='Completed/hash-verified segments only. '+('Six-segment natural trajectory completed. ' if complete else 'Longer trajectory still running. ')+('Natural monthly town/rival independent audits passed. ' if len(monthly)==2 else 'Monthly independent audits remain pending. ')+'SDK/GPU/SPU/IRQ boundaries remain modeled.')
(BASE/'LATEST-ANALYSIS.json').write_text(json.dumps(latest,indent=2)+'\n')
lines=['# 次の自然月次境界への営業継続'+('' if complete else '（継続中）'),'','2026-11-13（日本時間）。main-25・時計20,960・累積10,488更新から、原営業親処理と独立親モデルを継続比較した。時計・資金・乱数・配属への直接変更なし。','',f'完成済み {len(rows)}/6区間、追加{summary["verified_updates"]:,}更新。未完の区間や診断用の再実行を累積へ加算しない。','','| 完成区間 | 時計 | 累積更新 | 自社資金 | 他社資金 |','|---|---:|---:|---:|---:|']
for r in rows:lines.append(f'| {r["output"]} | {r["clock_after"]:,} | {r["completed_iterations"]:,} | {r["cash_after"][0]:,} | {r["cash_after"][1]:,} |')
lines+=['',f'原描画呼出し {sum(r["frames"] for r in rows):,}回、従業員全体処理 {sum(r["staff_checks"] for r in rows):,}件、客全体処理 {sum(r["customer_checks"] for r in rows):,}件を照合した。資金は全書込みの連鎖と、売上・仕入・決算費用・月次調整を台帳から再計算した値の両方が一致。','','## 自然到達した決算','', '| 時計 | カレンダー | 処理順 | 決算前の両社資金 | 決算後の両社資金 |','|---:|---|---|---|---|']
for r in rows:
 for d in r['daily_close_checks']:lines.append(f'| {d["clock"]:,} | {d["calendar"]} | {d["store_order"]} | {d["cash_before"]} | {d["cash_after"]} |')
lines+=['','カレンダーと店舗処理順は原状態の値。決算前後の差は、通常の追加売上・仕入と区別する。月次では締済台帳への倍率反映に伴う資金調整を含む。詳細は各 `*.audit.json` と原比較証跡。','','## 町・ライバルの月次照合','']
if 'town' in monthly:
 for r in monthly['town']['cases']:lines += [f'- 時計{r["clock"]:,}：変化区画{r["changed_cells"]}、内部レベル変化{r["level_changes"]}、画像タイル変化{r["tile_changes"]}。人口{r["population_before"]}→{r["population_after"]}。',f'- 原町24,000バイト・乱数・履歴・フラグ・通知文字列・キューと独立モデルが一致。建築/解体操作は `{r["actions"]}`、通知予約は `{r["events"]}`。']
else:lines+=['町の月次前後RAM・独立モデルの照合は、この保存時点では未完。']
if 'rival' in monthly:
 for r in monthly['rival']['cases']:lines += [f'- ライバルの自然月次判断：`{r["reason"]}`。厳密MIPS-I実行器で原命令を{r["steps"]:,}命令実行し、独立方針モデル・自然到達後の対象領域と照合。',f'- 店舗・従業員・町・資金・資本・乱数・通番・更新フラグが一致。通知/キャッシュ省略境界と、非スタックRAM前方領域の比較結果は `natural-rival-audit.json` に明記。']
else:lines+=['ライバルの自然月次前後RAMの厳密整数実行器による再照合は、この保存時点では未完。']
lines+=['','## 保存と再現','',f'最新の完成再開点は `{name}`。RAM SHA-256：`{last["final_ram_sha256"]}`。',f'証跡{len(manifest["files"])}ファイルのサイズ・ハッシュと可逆圧縮方法は `evidence-encoding.json`。機能境界で捕捉したRAMは診断専用であり、再開可能なCPU状態と混同しない。','','```sh','python ps1-analysis-checkpoints/restore-latest.py --destination /absolute/empty/runtime','python prepare-inputs.py /absolute/empty/runtime/algorithm-analysis','python continue-main.py /absolute/empty/runtime/algorithm-analysis','python audit-natural-town.py /absolute/empty/runtime/algorithm-analysis','python audit-natural-rival.py /absolute/empty/runtime/algorithm-analysis','```','','`prepare-inputs.py` は開始点main-25と保存済み完成区間の全入力を検査・展開する。完成証跡があれば再実行せず全体を再監査し、未完区間から続ける。原r2の209部品と原EXEは既存復元スクリプトで照合する。','','## 原資料と制限','','原EXE `SLPS_007.82` SHA-256：`d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd`。Unicorn 2.1.4、Capstone 5.0.7、Pillow 12.3.0。営業比較は原子関数を共有する。追加のライバル診断では別の厳密整数実行器を使うが、文字列生成・キャッシュ更新には明記した省略境界がある。SDK/BIOS・GPU/SPU/IRQは既存モデルであり、実画面の画素・実音声・実時間速度や全実機動作を証明しない。main・Claudeブランチ・Android本体の変更なし。']
(ROOT/'README.md').write_text('\n'.join(lines)+'\n');print(json.dumps(summary))
