# 0255 — 画面・店舗切替後に旧メニュー操作を実行しない

2026-11-26、PLAY-0255。基点cbfb1f7ff28b0e2bd5b7cf45f17f741aa07bf0cc、branch `chatgpt/mobile-resume-20261126`。main6282489と開PR #286のHEADを確認し、同PRへ追加する。ユーザー指示に従いビルドしない。

## 背景・変更前の再現

描画時に作るhits/_active_actionが次の描画まで残り、open_window直後の決定が以前の画面の処理を呼ぶ。指で押したメニュー項目もscreen文字列だけで継続判定するため、同名画面の再入場や店舗切替を識別できなかった。

新menu_context_smokeで、viewを描画→systemへ切替→次の描画前に決定、の順に呼ぶとsystemが旧viewの処理で閉じることを変更前に再現した（exit1）。先行確認を除いた変更前コードでも、hoursの確認を押す→hoursを開き直す→指を離すと旧値を決定することを再現（exit1）。さらに店舗切替時の通知を閉じた条件で、確認を押した店舗とは別の店舗へ営業時間が設定されることを別途再現（exit1）。一時的に変更前へ戻したファイルは全て修正版へ復元済み。

## 決定・実装

ps1_ui.invalidate_menu_actionsを追加し、保持中のタップ/描画済み項目/決定Callable/選択枠と人事ドラッグを無効にする。既に取得した指のreleaseは引き続き消費し、背後の地図へ流さない。次の描画で現在の文脈に合う操作が再生成される。

画面を開く/閉じる、L/Rによるページ・営業時間等の変更、表示切替等のnavigate、什器選択から床配置への遷移で呼ぶ。main.select_storeも成功時に呼び、店舗切替前の確認を無効にする。メニューの階層/選択/未確定案/履歴や営業時間そのものは、この取消処理では変更しない。中断用cancel_pointer_inputは従来どおり別に保持する。

## 検証

menu_context_smoke: 旧画面の即時決定を実行しない、同名画面再入場の旧タップ無効、別店舗への旧営業時間適用なし、L/Rで候補変更した時の旧確認なし、新たなタップは表示された営業時間を設定、もう一方の店舗は不変。実際のViewportのnative touchを使用する。保存ファイルは使わない。

Godot4.6.3の関連13本成功: menu_context / save_feedback / load_ui_restore / ps1_menu_dispatch / mobile_controls / ps1_touch_audit / menu_usability / renovation_ui / renovation_editor / mobile_resume / store_camera_persistence / recovered_ui / personnel_decision。recovered_uiの成功文は「Recovered real UI smoke passed」であり、試験ランナーの_PASS限定判定を訂正してログとexit0から成功を確認した。Python804件成功（外部プラグイン非推奨警告1）、全体headless1205step成功、SCRIPT ERROR/ERROR0。CIへ新回帰を追加。

## ファイルと範囲

game/scripts/main.gd、ps1_ui.gd、新menu_context_smoke.gd、.github/workflows/native-staff-regression.yml、本decision、最新handoff/status、RELEASE_ACCEPTANCE、PROJECT_MEMORY追記。経営数値・原作仕様・保存形式の追加変更なし。Museの新規解析を採用していない。APK/版数未更新、配布済0.8.14/code94にはPLAY-0252〜0255未収録。Android実機の高速入力/複数指を確認済みとはしない。原作完全一致の未完と既存未解決6件（U-1〜U-6）は維持する。
