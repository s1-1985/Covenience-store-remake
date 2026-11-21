# 0235 — ライバル会社の宣伝

## 背景
0.8.5では自社宣伝だけが営業へ接続され、既存原作解析にあるライバルの月初選択と実施が未反映だった。

## 決定
原800275F8の会社処理へ対応し、原町先頭のmode、月初1乱数、費用10倍条件、最大1広告の選択/全解除、実施時の再資金判定なし、1社1回支払、全活動ライバルの人気、kind4/sound101通知を接続。初期0時・保存再開の重複・子店舗の二重実行を防止する。会社費用の表現は既存company_advertising/UID0を利用する。

## 検証
原233限定区間をfixtureとして保存。rival_advertising_smoke.gdとadvertising_ui_smoke.gdで資金分離、休業店、通知、日本語、JSON、初月/月越しを確認。回帰結果は最新handoffに記録。

## ファイル
program_advertising.gd、vertical_slice_simulation.gd、phone_ui.gd、両smoke、source_rival_advertising.json、研究README/probe/命令抜粋。

## 範囲外
原物理スロット履歴順、全営業RNG一致、原通知全文の制御列、年初通知の原順序、原カード形式、既存未解決6件。Android実機確認は未実施。
