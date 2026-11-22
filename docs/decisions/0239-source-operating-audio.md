# 0239 — 解析済み営業音声の接続

## 背景
原SE/VOSの資産と番号は導入済みだが、即時決済/万引き成功/清掃完了/体力切れが未接続だった。既存イベントの再生順も発生時系列で、原bit昇順とは異なっていた。

## 決定
既存の成功イベントを原ID9/21へ接続。native清掃と体力切れの既存完了分岐でイベントを生成し、ID24/25へ接続。既知の8イベントを7bitへまとめ、原main_requestsの昇順を使う。表示店舗ガードと既存設定を維持。新しい仮値/セリフ/音源は追加しない。音声の呼出しで営業RNGは消費しない。

## 検証
Godot4.6.3関連10本成功。Python789件中786成功/既存2失敗/想定1。清掃完了の日本語訳漏れを修正済み。Android0.8.9/code89を従来署名で出力し、変更5gdc、テスト除外、署名/パッケージ/versionを確認。実機/実聴未確認。

## ファイルと出典
program_audio.gd、source_integration.gd、program_people.gd、main.gd、ja.po、operating_audio_smoke.gd、export_presetsとCI。既存資料の出典はdocs/research/operating-audio-bridge-2026-11-21/。

## 範囲外
全フラグ生成元、SE OFF時の原フラグ持越し/原保存形式、原割込み周期、SPU音質、全営業RNG/行列幾何、原カード形式。原作全音声完全一致とはしない。
