# 自然出店したライバル店の初日営業

2026-11-13（日本時間）。main-31・時計23,360・累積11,688更新から継続。時計・資金・乱数・配属の直接変更なし。

完成済み 1/3区間、追加200更新。完成区間のみを最新再開点へ採用する。

| 完成区間 | 時計 | 累積更新 | 自社資金 | 他社資金 |
|---|---:|---:|---:|---:|
| TOWN0001-ci-main-32-single | 23,760 | 11,888 | 99,052,002 | 97,743,149 |

各区間で原営業親処理と独立親モデルを比較し、従業員・客・補充・日次決算の独立監視を実行した。両社資金は全書込みの連鎖と店舗日次台帳からの再計算で一致。

## 再現

```sh
python ps1-analysis-checkpoints/restore-latest.py --destination /absolute/empty/runtime
python prepare-inputs.py /absolute/empty/runtime/algorithm-analysis
python continue-main.py /absolute/empty/runtime/algorithm-analysis
python audit-new-store.py /absolute/empty/runtime/algorithm-analysis
```

完成証跡があれば再実行せず再監査する。`evidence-encoding.json` に全証跡のサイズ・SHA-256と可逆圧縮方法を記録する。原EXE SHA-256は `d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd`。

## 制限

原子関数を共有する親処理間比較と、自然到達した状態での独立モデル照合である。SDK/BIOS・GPU/SPU/IRQは既存モデルであり、実画面の画素・実音声・実時間速度を証明しない。従業員移動の回数は論理座標の変化である。

実行器の命令数制限を外す診断2条件はSIGSEGVで終了したため採用していない。完成区間は原実行器の命令数制限を維持している。失敗診断は主系列の更新回数へ加算しない。
