# 営業中の新規保存・エラー回復・取消し

2026-11-05。初代PS版 SLPS_00782 の原実行コードと既存チェックポイントから継続した。mainやゲーム実装ブランチは変更しない。

## 結果

| 経路 | 原のカード初期化結果 | 最終結果 |
|---|---|---|
| 空の論理カード | 2 | ヘッダ・ファイル新規作成、本文保存、営業復帰 |
| 初回エラー後に再試行 | 5 → 0 | 初回は書込みなし、再試行で保存、営業復帰 |
| エラー後に取消し | 5 | 書込みなし、既存114688バイトが完全一致、営業復帰 |

3経路とも、main09の営業中から操作入力で上位メニュー・設定・保存画面へ進んだ。原505A0処理の呼出順を独立したポリシーと照合した。保存成功2経路の本文は同一で、時計15960、所持金98754969 / 153777535を含む。892回の128バイト書込み後の全ファイルを独立実行と照合し、実ファイルを原7AB2Cの892回読込み、原5188Cチェックサム、原6BC40デコードにかけ、37領域を全バイト確認した。デコード処理の戻り値は成功ステータスと解釈しない。

エラーはBIOS infoの応答を再試行では[1,1,1,0]、取消しでは[1]として発生させた。ゲーム内の結果5やメニュー選択値、成功フラグは注入していない。カード初期化・作成・保存は原MIPS処理、BIOS・イベント・論理ファイルは既存の代用境界である。実機カード通信・実BIOS・GPU/SPU/IRQ、実画面表示は検証範囲外。

## 新規ファイル作成時の一時バッファ

最初の試行は、一時初期化バッファのSHA差を検出して停止した。原5FE54が入口SP-4へ保存する戻り先が、原の親呼出しでは0x8005d06c、独立呼出しでは0x80001000であり、その3バイト差が新規ファイルのオフセット34116～34118に含まれていた。先頭512バイトは一致する。原作成処理が0x801f7920から114688バイトを読むため、2MB RAMのミラー境界をまたぐ。

この差は、後続892回の本文書込みで全て上書きされる。比較を省略して済ませず、元の両バッファを保存し、差分位置が原命令と実行時SP/RAに一致することをaudit.pyで確認した。最終ファイルと全I/Oは正規化せず完全一致で照合している。履歴はcreate/development-initial-fill.*、元バッファはcreate/initial-{native,reference}-0.bin、命令根拠はsource-instructions.jsonに保存した。

## 自然営業の最新再開点

メニュー実験3経路は独立分岐として保持した。自然営業はmain09から60更新継続し、main10を最新とした。

| 項目 | 開始 | 終了 |
|---|---:|---:|
| 時計 | 15960 | 16080 |
| 累積更新 | 7988 | 8048 |
| 自社所持金 | 98754969 | 98724409 |
| 他社所持金 | 153777535 | 153780885 |

自社2店舗の仕入れ2400+28160で-30560、他社店舗の売上4050・仕入れ700で+3350。32回の所持金書込みと独立した店舗台帳差分が一致し、スタッフ・客ループ各180件も検証した。この区間では日次決算は通過していない。RAM SHA256は6b5eda41f932569a9489bd6bf79206c2daa8ffdfbc89f3a1b203a01e82418dba。

## 保存物・再現

- recovery.py: create / retry / cancel の営業入力から原保存UI・カード処理への接続。
- audit.py: 自然営業の会計照合、原読込み・チェックサム・37領域復元、一時バッファ差の検証。
- 各経路ディレクトリ: 呼出トレース、入力、代用境界、I/O、実保存ファイル、検証結果。
- evidence/: main10と3実験分岐のメタデータ・圧縮RAM、60更新の完全検証記録。
- natural-audit.json / recovery-audit.json: 全検証結果。
- development-dependency.log: 実行環境初期化後のunicorn不足。依存を再導入して実行完了した記録。

原r2アーカイブを復元し、既存レポートに従いmain09と継続解析コードを復元する。main09は../20261105-play-save/evidence/source/opened-snapshots-20261028/から同名の解析source配下へ置く。main10生成コマンドは解析ディレクトリ内で以下を実行する。

```sh
python verify_operating_branch_segment_20261103.py TOWN0001-ci-main-09-single 60 TOWN0001-ci-main-10-single
```

続いてこのフォルダのスクリプトを使用する。

```sh
python recovery.py /absolute/path/to/algorithm-analysis create
python recovery.py /absolute/path/to/algorithm-analysis retry
python recovery.py /absolute/path/to/algorithm-analysis cancel
python audit.py /absolute/path/to/algorithm-analysis
```

実行環境はPython、unicorn 2.1.4、capstone 5.0.7、Pillow 13.0.0。原EXE SHA256はd6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd。入力ディスクの過去の同一性確認は../20261104-disc-continuation/README.mdを参照。

Git保存後はuploaded-checkpoint-manifest-01.jsonとgit-readback-01.jsonで全成果物のサイズ・Git blob・SHA256を読み戻し確認する。読み戻し記録が保証するコミットと、その記録自体を保存する後続コミットは区別する。
