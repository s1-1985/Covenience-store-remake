# 次の自然月次境界への営業継続（継続中）

2026-11-13（日本時間）。main-25・時計20,960・累積10,488更新から、原営業親処理と独立親モデルを継続比較した。時計・資金・乱数・配属への直接変更なし。

完成済み 2/6区間、追加400更新。未完の区間や診断用の再実行を累積へ加算しない。

| 完成区間 | 時計 | 累積更新 | 自社資金 | 他社資金 |
|---|---:|---:|---:|---:|
| TOWN0001-ci-main-26-single | 21,360 | 10,688 | 99,027,612 | 153,246,629 |
| TOWN0001-ci-main-27-single | 21,760 | 10,888 | 98,986,740 | 153,207,113 |

原描画呼出し 800回、従業員全体処理 1,200件、客全体処理 1,200件を照合した。資金は全書込みの連鎖と、売上・仕入・決算費用・月次調整を台帳から再計算した値の両方が一致。

## 自然到達した決算

| 時計 | カレンダー | 処理順 | 決算前の両社資金 | 決算後の両社資金 |
|---:|---|---|---|---|
| 21,600 | [1, 4, 4, 0, 0] | [0, 2, 1, -1, -1, -1, -1, -1, -1, -1] | [99027712, 153262194] | [98984240, 153235218] |

カレンダーと店舗処理順は原状態の値。決算前後の差は、通常の追加売上・仕入と区別する。月次では締済台帳への倍率反映に伴う資金調整を含む。詳細は各 `*.audit.json` と原比較証跡。

## 町・ライバルの月次照合

町の月次前後RAM・独立モデルの照合は、この保存時点では未完。
ライバルの自然月次前後RAMの厳密整数実行器による再照合は、この保存時点では未完。

## 保存と再現

最新の完成再開点は `TOWN0001-ci-main-27-single`。RAM SHA-256：`72ed30275a6f47c62eabd93382fa7125fa2b8df296c32050495bbb5ea2edec78`。
証跡8ファイルのサイズ・ハッシュと可逆圧縮方法は `evidence-encoding.json`。機能境界で捕捉したRAMは診断専用であり、再開可能なCPU状態と混同しない。

```sh
python ps1-analysis-checkpoints/restore-latest.py --destination /absolute/empty/runtime
python prepare-inputs.py /absolute/empty/runtime/algorithm-analysis
python continue-main.py /absolute/empty/runtime/algorithm-analysis
python audit-natural-town.py /absolute/empty/runtime/algorithm-analysis
python audit-natural-rival.py /absolute/empty/runtime/algorithm-analysis
```

`prepare-inputs.py` は開始点main-25と保存済み完成区間の全入力を検査・展開する。完成証跡があれば再実行せず全体を再監査し、未完区間から続ける。原r2の209部品と原EXEは既存復元スクリプトで照合する。

## 原資料と制限

原EXE `SLPS_007.82` SHA-256：`d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd`。Unicorn 2.1.4、Capstone 5.0.7、Pillow 12.3.0。営業比較は原子関数を共有する。追加のライバル診断では別の厳密整数実行器を使うが、文字列生成・キャッシュ更新には明記した省略境界がある。SDK/BIOS・GPU/SPU/IRQは既存モデルであり、実画面の画素・実音声・実時間速度や全実機動作を証明しない。main・Claudeブランチ・Android本体の変更なし。
