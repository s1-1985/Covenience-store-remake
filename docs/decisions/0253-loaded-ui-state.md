# 0253 — 読込後の操作状態を保存内容へ合わせる

2026-11-26、PLAY-0253。基点050c4122a4157c0983e95f5d3a91f6763e091bfe、branch chatgpt/mobile-resume-20261126。main6282489/採用ライン1257d3と開PR286のHEADを確認。前回の中断・復帰修正と同じPR #286（https://github.com/s1-1985/Covenience-store-remake/pull/286）へ追加する。ユーザー指示に従いビルドしない。

## 変更前の再現

- 追加出店の位置選択中に既存店舗の保存データを読むと、choosing_new_storeが残り、再び出店位置の選択状態になる。新load_ui_restore_smokeでexit1を確認。
- PSシステムメニューのロードはmainの読込後にclose_windowを呼んでいた。旧内装UIのclose_hours/店舗UIDが残っていると、close_windowが保存データの営業時間へ旧値を書き戻す。第1ケースだけを除いた回帰を変更前のmain/ps1_uiで実行し、exit1「Old menu cleanup overwrote the loaded opening hours」を別途確認。確認後に作業ファイルを元の修正版へ復元した。

## 決定・実装

成功した読込では以前の出店選択と壁時計基点、旧什器/ライバルパネルを解除して保存状態へ同期する。PS UIにrestore_loaded_gameを設け、古い入力待ち/確認見積り/メニュー履歴/価格等の未確定案/旧通知参照を破棄する。close_windowを使った旧営業時間の復元や、保存前と無関係な取引は行わない。

保存内容にrenovation_sessionがあれば、既存_resume_renovation_editを呼んで保存された対象UIDとrestore_hoursを採用し、内装画面へ戻す。システムのロード項目はこの成功処理に画面同期を任せ、読み込んだ直後に再度close_windowを呼ばない。

読めない形式のテストファイル（JSON配列）では成功用UIリセットを呼ばず、現在のゲーム/メニューを維持する。保存形式、IO手順、原作の経営数値、ゲームルールは変更しない。本変更はすべての破損セーブ内容に対するload_state内部の原子性を保証する変更ではない。

## 検証

新回帰は一意なuser://tests/パスへ実際のSaveGameServiceでJSONを書き、実際のロード処理とPSシステムメニューのcallbackを通す。既定のユーザー保存ファイルは使わない。出店選択解除、読込後の24h保持、実renovation_sessionの内装再開/UID/restore_hours、JSON配列での失敗時不変を確認。テストファイルは終了時に削除する。メニューhits生成には描画フレームが必要なため、初回のテスト設定を1フレーム待機へ訂正した。

Godot4.6.3の関連10本成功: load_ui_restore / mobile_resume / store_camera_persistence / ps1_menu_dispatch / renovation_ui / renovation_editor / source_audio_ui / calendar_ui / source_notifications_ui / recovered_ui。Python804件成功、外部プラグイン非推奨警告1件。全体headless1205step、SCRIPT ERROR/ERROR0件。

## ファイル・配布状態

main.gd、ps1_ui.gd、新load_ui_restore_smoke.gd、CI、本文、最新handoff/status、RELEASE_ACCEPTANCE、PROJECT_MEMORY追記。APK/版数は更新せず、配布済0.8.14/code94にはPLAY-0252/0253とも未収録。Android実機/実OS確認は未実施。

原作完全一致の未完と既存未解決6件（U-1〜U-6）は維持する。内部の詳細schema検査/読込拒否の全原子性、原カード形式互換は本作業とは別の未確認範囲として残す。
