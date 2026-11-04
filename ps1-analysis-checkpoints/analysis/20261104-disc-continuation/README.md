# 添付ディスク照合と決算後の継続解析（2026-11-04）

前回の解析専用ブランチ `chatgpt/ps1-analysis-recovery-20261103`、コミット
`179ef0667f6a87c0dcdd24669467e8b502442cca` から継続する。
main・Claude管理ブランチは変更しない。

## 解析元の同一性

添付BINは90,166,272バイト、38,336セクタ。SHA-256は
`8d8eda789c5a2fe892a4722719b0466dd7d126eed6cd99ad05a807d81b57d1c1`。
ISOボリュームIDはSLPS_00782。全セクタの同期・mode2・二重サブヘッダに不一致はなかった。
EDC/ECCは再計算していない。

ISO9660を走査して77ファイル・6ディレクトリを台帳化した。
従来のZIPに格納されたsource直下の同名ファイル69本が全バイト一致した。
原EXE `SLPS_007.82` のSHA-256も従来の
`d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd` と一致する。
既存の資源マニフェスト41記録について、LBA・ファイルサイズ・本文・末尾セクタ余白まで一致した。
41はマニフェスト記録数であり、重複しないファイル数ではない。

`disc-verification.json` は全ファイルのLBA・サイズ・ハッシュを保持する。
Form 2を含む2ファイルのISO投影ハッシュは音声デコード結果ではない。
CUE内の元名SLPS_00782.BINと添付名SLPS_00782(1).BINの差を記録し、入力は変更していない。
添付BIN全体のGit複製を作ったという記録ではない。

## 決算の境界条件：17条件一致

`probe-finance-boundaries.py` は時計14400の確定済みRAMを条件ごとに複製し、
原29334を独立した診断としてもう一度呼ぶ。通常営業の追加日数には含めない。
既存のSourceFinanceMonitorが原処理と独立した決算モデルを比較し、店舗50,800バイト・
従業員2,100バイト・イベントキュー・対象状態・通知文字列を照合する。
さらに以下の閾値を明示的に期待値で確認した。

| 制御した条件 | 結果 |
|---|---|
| 自社決算前43,471 / 43,472 / 43,473 | 引落43,472後は−1 / 0 / 1。−1のみ終了状態4へ |
| 他社資金0 | 他社は−26,976になるが、この関数の終了判定は発火しない |
| 年フィールド98 / 99 / 100 | 99以上で終了状態4へ |
| 年フィールド0xffffffff | signed 32bitとして負数。年数条件では発火しない |
| 連番98 / 99 / 100 / 32767 | 99以上で終了状態4へ |
| 連番32768 / 65535 | signed 16bitとして負数。連番条件では発火しない |
| 時間ゲート614/618が非0 | 引落も末尾の終了判定も実行せず復帰 |

終了時は800CD9B4=4、シナリオ800CD948=255。
年・連番の負数は型境界診断であり、プレイヤーが自然に到達する条件ではない。
描画・音声・文字列の6端点は既存試験と同じゼロ戻りの非変更境界で、
到達した呼出しは各条件のexternal_callsに残す。物理PS1全体の動作証明ではない。
詳しい入力・決算前後の資金・RAMハッシュ・独立モデル照合は`finance-boundaries.json`。

## 再現

解析ブランチの原ZIPをrestore.pyで復元し、algorithm-analysis/を作業領域へ展開する。
以降のコマンドのalgoは展開したalgorithm-analysis、priorは
`../20261103-operating-continuation`への絶対パスである。

```sh
python verify-disc.py /path/to/disc.bin /path/to/disc.cue /path/to/algo
python continue-and-audit.py /path/to/algo /path/to/prior
python probe-finance-boundaries.py /path/to/algo /path/to/algo/source/opened-snapshots-20261028/TOWN0001-ci-main-04-single
```

continue-and-audit.pyは過去のCPU保存状態を原ZIPへ重ね、原継続コードを変更せず120更新を実行する。
時計・資金・従業員・乱数は途中で注入しない。
自然営業の結果は最終照合後にcontinuation-audit.jsonとevidence/へ保存する。
原入力・過去状態は既存のGit保存物を参照し、新しいコード・出力は本ディレクトリへ分離する。
