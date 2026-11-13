#!/usr/bin/env python3
"""Package only completed audited segments; leave partial runtime evidence out."""
import hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent;CHECKPOINTS=ROOT.parent.parent
status=json.loads((ROOT/'long-continuation-status.json').read_text())
assert status['cases'] and all(x['passed'] for x in status['cases'])
subprocess.run([sys.executable,str(ROOT/'encode-evidence.py')],check=True)
last=status['cases'][-1];name=last['output']
meta=json.loads((ROOT/'evidence/source/opened-snapshots-20261028'/(name+'.json')).read_text())
latest=dict(branch='chatgpt/ps1-analysis-recovery-20261103',date_jst='2026-11-13',snapshot=name,phase=meta['phase'],clock=last['clock_after'],completed_iterations=meta['completed_iterations'],cash=last['cash_after'],ram_sha256=meta['ram_sha256'],metadata=f'analysis/{ROOT.name}/encoded/evidence/source/opened-snapshots-20261028/{name}.json.zlib',compressed_ram=f'analysis/{ROOT.name}/encoded/evidence/source/opened-snapshots-20261028/{name}.ram.zlib',report=f'analysis/{ROOT.name}/README.md',limits='Completed/hash-verified segments only. New rival first-day continuation; SDK/GPU/SPU/IRQ boundaries remain modeled.')
(CHECKPOINTS/'LATEST-ANALYSIS.json').write_text(json.dumps(latest,ensure_ascii=False,indent=2)+'\n')
policy=CHECKPOINTS/'ANALYSIS-POLICY.md';s=policy.read_text();link=f'- [2026-11-13：新ライバル店の初日営業と日次決算](analysis/{ROOT.name}/README.md)\n\n'
if link not in s:s=s.replace('## 保存済み\n\n','## 保存済み\n\n'+link);policy.write_text(s)
lines=['# 自然出店したライバル店の初日営業','', '2026-11-13（日本時間）。main-31・時計23,360・累積11,688更新から継続。時計・資金・乱数・配属の直接変更なし。','',f"完成済み {len(status['cases'])}/3区間、追加{status['total_updates']:,}更新。完成区間のみを最新再開点へ採用する。",'', '| 完成区間 | 時計 | 累積更新 | 自社資金 | 他社資金 |','|---|---:|---:|---:|---:|']
for x in status['cases']:lines.append(f"| {x['output']} | {x['clock_after']:,} | {x['completed_iterations']:,} | {x['cash_after'][0]:,} | {x['cash_after'][1]:,} |")
lines+=['','各区間で原営業親処理と独立親モデルを比較し、従業員・客・補充・日次決算の独立監視を実行した。両社資金は全書込みの連鎖と店舗日次台帳からの再計算で一致。','']
audit=ROOT/'new-store-audit.json'
if audit.exists():
 a=json.loads(audit.read_text());assert a['all_passed']
 lines+=['## 新店舗スロット3の検証','',f"他社店舗・従業員ID {a['staff_ids']}。営業時間表の番号{a['schedule_index']}は7時〜23時で、23時台は新規入客しない。",'', '| 照合項目 | 結果 |','|---|---:|',f"| 従業員／客／入客の各監視 | 各{a['verified_loops_per_domain']:,}回 |",f"| 新規入客グループ | {a['created_groups']}組 |",f"| 新規入客人数 | {a['created_people']}人 |",f"| 売上計上 | {a['sales_postings']}回・{a['additional_revenue']:,}円 |",f"| 従業員の座標移動 | {a['staff_movement_steps']}回 |",f"| 向きだけの変更 | {a['staff_direction_only_changes']}回 |",f"| 補充関数の照合 | {a['restock_checks']}回 |",f"| 追加仕入計上 | {a['additional_goods']:,}円 |",'',f"初入客は時計{a['first_created']['clock']}、初売上は時計{a['first_revenue']['clock']}。日次決算は時計{a['midnight']['clock']}、カレンダー{a['midnight']['calendar']}で新店舗も処理対象となった。",'', f"前日台帳の5欄は `{a['previous_day_ledger']}`。開設時の日次費用欄 `{a['opening_day_ledger']}` と、その後の支払／売上を個別伝票で突合した。開設時に支払済みの38,260円を重複して差し引かない。詳細は `new-store-audit.json`。",'']
if audit.exists() and a['restock_checks']==0:lines+=['新店舗の補充関数はこの区間では未到達。追加仕入が発生したとは扱わない。','']
lines+=['## 再現','', '```sh','python ps1-analysis-checkpoints/restore-latest.py --destination /absolute/empty/runtime','python prepare-inputs.py /absolute/empty/runtime/algorithm-analysis','python continue-main.py /absolute/empty/runtime/algorithm-analysis','python audit-new-store.py /absolute/empty/runtime/algorithm-analysis','```','', '完成証跡があれば再実行せず再監査する。`evidence-encoding.json` に全証跡のサイズ・SHA-256と可逆圧縮方法を記録する。原EXE SHA-256は `d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd`。','', '## 制限','', '原子関数を共有する親処理間比較と、自然到達した状態での独立モデル照合である。SDK/BIOS・GPU/SPU/IRQは既存モデルであり、実画面の画素・実音声・実時間速度を証明しない。従業員移動の回数は論理座標の変化である。','', '実行器の命令数制限を外す診断2条件はSIGSEGVで終了したため採用していない。完成区間は原実行器の命令数制限を維持している。失敗診断は主系列の更新回数へ加算しない。','']
(ROOT/'README.md').write_text('\n'.join(lines))
print(json.dumps(dict(snapshot=name,completed_segments=len(status['cases']),clock=last['clock_after'],completed_iterations=meta['completed_iterations'])))
