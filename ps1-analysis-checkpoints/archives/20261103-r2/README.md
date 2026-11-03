# 2026-11-03 r2：ZIP原本の分割保存

添付ZIPの全バイトを209個の分割データとして保存した。
元ZIPへのリンクだけを登録したものではない。再圧縮や収録物の変更はしていない。
このディレクトリは解析専用ブランチで管理する。

- 元ZIP名：Conveni-PS1-Analysis-Checkpoint-20261103-r2.zip
- 添付時の名前：Conveni-PS1-Analysis-Checkpoint-20261103-r2(1).zip
- ZIPサイズ：153696391バイト
- SHA-256：afd46b32e0a24e3f2d75723a0c4a3fecc120d80b07993c2e73236e55cf3d54cd
- 収録件数：2346
- 展開時サイズ：1166354414バイト
- 添付ZIPの全項目CRC検査：異常なし
- 分割データ：parts/part-0000.bin から part-0208.bin
- 各分割データのサイズ、SHA-256、Git blob SHA-1はmanifest.jsonに記載
- 全収録項目のパス、サイズ、CRC32、SHA-256はzip-entry-index.jsonに記載

## 復元方法

このブランチをcloneし、このディレクトリで次を実行する。
Python 3標準ライブラリのみを使用する。

検査のみ（ファイル作成なし）：

```sh
python restore.py
```

ZIPを復元する（既存ファイルの上書きは拒否）：

```sh
python restore.py --restore Conveni-PS1-Analysis-Checkpoint-20261103-r2.zip
```

どちらも全209部品のハッシュと、連結した元ZIP全体のSHA-256を確認する。
ZIPを展開して利用する場合は十分な空き容量を確保する。
添付の内容はそのまま保存した履歴資料であり、ゲーム全体の再現完了を意味しない。
[元ZIP内の最新README](source-README-20261103-r2.md) から解析の再開箇所を確認できる。

## 保存・照合状況

アップロード時に全209部品について、添付ZIPから計算したGit blob SHA-1とGitHubの応答が一致した。
復元スクリプトも添付ZIPの分割読取りを用いて実行し、全体サイズ・SHA-256が一致した。
保存確定後、全209部品をGitHubからbase64形式で読み戻し、添付ZIPの各対応範囲と全バイト一致を確認した。
読戻し対象コミット：564fa120c34b34c1005ee8df669a52b0296b60d6。
manifest.jsonのverification.remote_byte_readback=true、remote_parts_verified=209に記録した。
この記録では、元のLibrary項目と再添付ZIPを別々にダウンロードして比較してはいない。
