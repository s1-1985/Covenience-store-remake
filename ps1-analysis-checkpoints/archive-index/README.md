# 過去成果物の管理台帳

記録日：2026-11-03（日本時間）
保存先：chatgpt/ps1-analysis-recovery-20261103

## 現在の保存状況

今回、保存元の現行ファイルから解析関係11件（ZIP5件）を確認した。
この台帳・元ファイルへのリンク・版・サイズをGitで管理する。
**ZIP本体のGit保存は未完了であり、リンク登録を本体バックアップとは扱わない。**
現在の読取り専用実行環境では、必要なファイル転送を実行できない。
転送できる環境になった時点で、本体を検査して保存する必要がある。

既存のセッション復旧記録と再構成コードは
[2026-11-03-session-recovery](../2026-11-03-session-recovery/README.md) に保存済み。

## 取得できた過去文書

[historical-texts](../historical-texts/) に、次の文書の全文読取結果を保存した。

- Conveni-PS1-Algorithms.read-text.md
- Conveni-PS1-Report.read-text.md

保存元の読取結果はどちらも has_more=false で、全391行・122行を取得した。
ただし読取テキストのUTF-8サイズは元メタデータより各1バイト少ない。
したがって、原ファイルとバイト単位で同一とは主張しない。
差分の原因を末尾改行と断定したり、補って同一と見なしたりしていない。
ファイル名のread-textはその区別を表す。原文の解析結論を今回の新規検証結果と混同しない。
旧報告の未検証事項や後続解析による訂正も、原文のまま保存している。
取得テキストのSHA-256はinventory.jsonに記録した。

## ファイル一覧

| 保存元ファイル | 元サイズ（バイト） | 現行版 | Gitの状態 |
|---|---:|---|---|
| [Conveni-PS1-Analysis-Checkpoint-20261103-r2.zip](https://chatgpt.com/library?file_id=libfile_dd7eacb0b7348191ba76a0d9186ec777&account_id=personal) | 153,696,391 | 25 | 本体転送待ち |
| [Conveni-PS1-Analysis-Checkpoint-20261013(1).zip](https://chatgpt.com/library?file_id=libfile_e29b8fbed5e081919c4f8b1d38ea7990&account_id=personal) | 13,833,932 | 未提示 | 本体転送待ち |
| [Conveni-PS1-Analysis-Checkpoint-20261013.zip](https://chatgpt.com/library?file_id=libfile_955a9402ab308191bd53c589df824a1b&account_id=personal) | 13,833,932 | 9 | 本体転送待ち |
| [Conveni-PS1-Claude-Handoff.md](https://chatgpt.com/library?file_id=libfile_3ea8d6967664819196d29a0bb72e951c&account_id=personal) | 29,526,568 | 103 | 本体転送待ち |
| [Conveni-PS1-Algorithms.zip](https://chatgpt.com/library?file_id=libfile_04dfc8b9b1988191bad1424b20d42d69&account_id=personal) | 334,908 | 1 | 本体転送待ち |
| [Conveni-PS1-Algorithms.html](https://chatgpt.com/library?file_id=libfile_7e7500bdb7dc8191a9ee5cd20407670d&account_id=personal) | 57,365 | 1 | 本体転送待ち |
| [Conveni-PS1-Algorithms.md](https://chatgpt.com/library?file_id=libfile_371ecc3f356881918d576e406712eb41&account_id=personal) | 26,928 | 1 | 読取テキストを保存 |
| [Conveni-PS1-Analysis.zip](https://chatgpt.com/library?file_id=libfile_acb43c22af108191943e7763f631e9da&account_id=personal) | 5,624,605 | 未提示 | 本体転送待ち |
| [Conveni-PS1-Analysis.html](https://chatgpt.com/library?file_id=libfile_4a9be42d82088191bbd8ecd681d62840&account_id=personal) | 1,644,487 | 未提示 | 本体転送待ち |
| [Conveni-PS1-Preview.png](https://chatgpt.com/library?file_id=libfile_ba99f85fe1448191ae7328fc20ed0163&account_id=personal) | 142,385 | 未提示 | 本体転送待ち |
| [Conveni-PS1-Report.md](https://chatgpt.com/library?file_id=libfile_30ef410c51c48191bc80b839dd95e09b&account_id=personal) | 9,916 | 未提示 | 読取テキストを保存 |

サイズが同じ20261013の2件も、実バイト・ハッシュ未取得のため同一と断定しない。
ファイル名が更新された同じ保存IDの旧版は、この一覧から別ZIPとして数え直していない。
たとえば20261103.zipという過去名の履歴があっても、今回取得した現行版はr2.zipである。
過去の全バージョンを列挙・取得したものではない。

## 本体を保存する際の完了条件

1. 保存元ID・file_id・versionとダウンロードした実ファイルを対応させる。
2. 実サイズとSHA-256を取得する。ZIPはCRCと収録ファイル一覧も確認する。
3. 元ZIPを履歴用に保管し、必要なコード・解析文書を作業用ディレクトリへ展開する。
4. 大きなバイナリは通常のGitコミットで扱えるか確認し、必要ならLFSやReleaseを使用する。
5. 公開保存先に適した内容か収録一覧を確認する。ゲーム本体等を分離した場合は、
   元ZIPの完全バックアップと解析コードの公開保存を別の達成状況として記録する。
6. 保存先から読み戻してSHA-256を照合した後に、その対象だけを保存完了へ変更する。
7. 保存済み原本を削除・置換しない。元ZIPや元保存物への変更は今回行っていない。

## 状態の意味

- read_text_copy_saved：取得した全文読取テキストをGitへ保存。原ファイルの完全コピーではない。
- binary_transfer_pending：メタデータ・所在を登録したのみ。本体未取得・未保存。

inventory.json内のgit_statusはこの保存コミットの内容を表す。
これは移行作業の途中記録であり、全成果物のGit移行完了報告ではない。
