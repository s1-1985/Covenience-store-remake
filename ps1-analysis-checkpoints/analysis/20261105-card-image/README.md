# 原セーブ処理と生メモリーカードイメージの接続

2026-11-05。前回 `af3a54ab6dd4df5001bfd40c9f08b692872117ad` から継続。

今回は原セーブ処理の外側にあった「論理ファイルだけの代用」を、ディレクトリと物理ブロック連鎖を持つカードイメージへ接続した。ゲーム側の原命令は変更していない。割当処理は新たな解析用モデルであり、原BIOSを復元したという意味ではない。

## 確認結果

| 検証 | 結果・証拠 |
|---|---|
| 原命令による新規保存・上書き・再読込 | 連続配置と分散配置の各2条件、計4条件が一致。[results.json](results.json) |
| 原保存ファイルと従来の論理ファイル実装の比較 | 114,688バイト全体とBIOSファイル呼出し列が完全一致 |
| 分散配置 | 物理ブロック順 `15,1,14,2,13,3,12,4,11,5,10,6,9,7`、空きは8。連続配置は1〜14、空きは15 |
| 原読書きの境界 | 各条件で本文892回の128バイト転送、合計読込3,568回・書込3,568回。全14ブロックを通る |
| 原デコーダー | 各読込後、37領域をペイロードと照合して一致 |
| 営業画面からの操作 | 両配置で、入力列→原メニュー→原カード処理→営業復帰まで保存・読込の4経路が通る |
| 配置の違いによるゲーム挙動 | 論理ファイル・BIOS呼出し列・最終2MB RAMが一致。[ui-cross-layout-results.json](ui-cross-layout-results.json) |
| 別実装での読込 | PS1VMCツールで直接診断4枚と営業UI保存2枚を抽出し、全バイト一致 |
| 別実装での書込 | 同ツールによる空カード作成→MCS取込→抽出が一致。Pythonモデルでもそのカードを読み込める。[external-results.json](external-results.json) |
| データ破損 | 本文・チェックサムの1ビット変更を原判定 `8005188C` が拒否。加算値を保つバイト交換は通る。[checksum-results.json](checksum-results.json) |

生カードは131,072バイト。管理領域のXORとファイル本文の加算チェックサムは別物である。本文の破損では管理領域が正常でも原ゲームの判定は失敗する。一方、加算チェックサムの一致だけではデータの意味まで保証できない。

各 `.mcr` にカード全体、`.card-file.bin` に原ファイル全体、`.trace.json.zlib` に論理I/Oと物理オフセット対応を保存した。`mutated-*.mcr` は意図的に変更した試験用コピーであり、通常の再開点には使わない。

## 営業UIの接続方法

[play-save.py](play-save.py) は前回までの入力経路を再使用し、`LogicalFiles` のバッファを [raw_card.py](raw_card.py) のブロック連鎖へ差し替える。元のセーブ監視器にあった合成完了処理を除く差分は、各配置フォルダーの `save-monitor.patch` に記録した。保存データ・メニュー選択結果・カード処理完了値を直接注入していない。

両配置とも `main-16` から4更新を比較。保存時の原エンコーダーは時計17640で走る。読込も同じ親状態から始め、保存ファイルを介して原デコーダーを通す。独立した親モデルと到達監視を比較するが、子処理・Unicorn・外部境界は共有している。

## 通常営業の新しい再開点

`TOWN0001-ci-main-17-single`、時計 **17760**、累積 **8,888更新**。

- `main-16` から自然に60更新・120フレームを追加した。
- 所持金：自社99,005,641、他社153,127,491。他社の減少4,605は原資金書込み列と店舗台帳の双方から一致した。
- 従業員・客処理は各180件を照合。今回の区間では日次決算なし。
- RAM SHA-256：`8ba3ea71a158260e5015cc6fe70011d14a5169d16e53020874908041f2ef2fa2`。
- [long-continuation-status.json](long-continuation-status.json) と `evidence/` に検証記録・再開RAM・メタデータを保存した。各カード実験・営業UI分岐は、この自然進行を置き換えない。

## モデルの範囲と未検証部分

新規空きブロックと有効ファイルの連鎖を扱う。管理XOR、循環、範囲外リンク、サイズ不整合、孤立ブロックなどを検査する。14件の拒否試験と、物理末尾から先頭側へ跨ぐ7バイト転送も実施した。拒否規則はこのモデルの仕様であり、原BIOSの異常時挙動とは区別する。

カードイベント・BIOSファイル入口、SDK/GPU/SPU/IRQ等の既存境界は引き続きモデルである。実SIO通信、実BIOS、実機、削除ファイル復旧、不良セクター置換、通信タイミングは未検証。営業UI経路は既存ファイルへの上書きであり、新規作成は原関数を直接呼ぶ診断で検証した。

原エンコーダーの最初の診断では命令予算200万を使い切った。過去のペイロード診断に合わせ1,500万へ変更し、原命令を完走させた。経緯は [harness-notes.json](harness-notes.json) に残した。

## 根拠と再現

- 原ディスク由来EXE：SHA-256 `d6a167a1c9e0fe98d7e44e12968caa489ac3eb7ed3b9e46012a188af8432b1fd`。既存の分割r2アーカイブに全バイトを保持。
- [PSX-SPX: Memory Card Data Format](https://psx-spx.consoledev.net/dev/ps1/sio/controllersandmemorycards/memory-card-data-format/)（2026-11-05参照）。カード管理領域・ブロック連鎖の仕様根拠。
- [bucanero/ps2vmc-tool](https://github.com/bucanero/ps2vmc-tool/tree/32a024518586a47d685d8c4ea58b67dc4e4472ce)、コミット `32a024518586a47d685d8c4ea58b67dc4e4472ce`。無変更のビルド用ソースとGPL-3.0 LICENSEを `ps1vmc-source-32a0245.tar.gz` に同梱。警告を含むビルド記録は `external-build.log`。ゲーム本体への組込みなし。

`restore-latest.py --destination <空フォルダー>` で復元した `algorithm-analysis` を以下の `ALGO` とする。Pythonの依存関係は既存の `source-reference/requirements.txt`、外部ツールにはGCC・make・zlib開発ファイルが必要。以下はこのフォルダーを作業ディレクトリとして実行する。

```sh
python prepare_inputs.py ALGO
python verify_card.py ALGO
python checksum_diagnostics.py ALGO
python continue-main.py ALGO
python play-save.py ALGO save fragmented
python play-save.py ALGO load fragmented
python play-save.py ALGO save contiguous
python play-save.py ALGO load contiguous
python external_verify.py
```

`prepare_inputs.py` はGit内の前回証拠から親の `main-16` を検証して追加配置する。カード状態、入力列、モデル、差分、外部ツールのソース、生成イメージ、再開RAMを揃え、元チャットの一時環境がなくても再実行できる形とした。
