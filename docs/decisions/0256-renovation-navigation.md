# 0256 — 改築の終了確認で画面遷移を止める

2026-11-26、PLAY-0256。基点bc0a0f2740c16b25c008781edfd767b359516b4b、branch `chatgpt/mobile-resume-20261126`。main6282489と開PR #286のHEADを確認し、既存PRへ追加する。ユーザー指示に従いAPKをビルドしない。

## 背景・再現

close_windowはrenovation_sessionがあると終了確認を表示して閉鎖を拒否するが、_navigateの表示切替/店舗/新規出店と、店舗一覧の選択callbackは、その後も処理を継続していた。これにより、確認があるのに町へ表示が変わる、別画面で終了確認を上書きする、新規出店の位置選択へ進む、カメラをresetする経路があった。店舗そのものの変更はシミュレーション側にも拒否ガードがあるため、UIの矛盾と分けて扱う。

新renovation_navigation_smokeの実改築・実viewメニューcallbackで、変更前に「Town navigation continued after renovation exit was blocked」exit1を再現した。

## 決定・変更

4箇所でclose_window後のwindow_idを確認し、閉鎖されていなければ後続の遷移を実行しない。touch_controls._storeが既に採用していた拒否判定と同じ方式である。終了確認の確定/取消/内装継続そのものは変更せず、編集中のデータ、UID、費用、営業時間を維持する。

## 検証

新回帰は実renovation_sessionを作り、view/店舗/新装開店/全店舗一覧の実callbackで終了確認の保持を確認。店舗UID/カメラ/現金/休業状態が不変、内装継続と明示確定が有効、確定後は町/店内/新規出店が再び利用できることを確認した。保存IOは使わない。

Godot4.6.3関連10本成功: renovation_navigation / renovation_ui / renovation_editor / menu_context / ps1_menu_dispatch / mobile_controls / menu_usability / load_ui_restore / save_feedback / graph_sale。Python804件成功（外部プラグイン非推奨警告1）、全体headless1205step成功、SCRIPT ERROR/ERROR0。CIへ新回帰を追加。

## ファイル・範囲

game/scripts/ps1_ui.gd、新renovation_navigation_smoke.gd、.github/workflows/native-staff-regression.yml、本decision、最新handoff/status、RELEASE_ACCEPTANCE、PROJECT_MEMORY追記。原作の経営数値/改築料金/仕様/保存形式は変更せず、Museの新規解析を採用していない。APK/版数更新なし、配布済0.8.14/code94にはPLAY-0252〜0256未収録。Android実機未確認、原作完全一致の未完と既存未解決6件（U-1〜U-6）は維持する。
