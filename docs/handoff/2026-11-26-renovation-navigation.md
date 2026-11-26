# 改築中の画面遷移を終了確認で止める（APK未更新）

PLAY-0256、基点bc0a0f2740c16b25c008781edfd767b359516b4b、branch `chatgpt/mobile-resume-20261126`。既存PR #286（https://github.com/s1-1985/Covenience-store-remake/pull/286）へ追加。

改築中のclose_windowが終了確認へ戻しても表示切替/店舗/新規出店/店舗一覧の処理が進んでいた。閉鎖拒否時は後続処理を止め、終了確認と店舗/カメラ/資金/営業時間を保持する。変更前にviewの実callbackで再現し、明示的な改築確定後は通常遷移へ戻れることも確認。詳細decision0256。

関連Godot10本、Python804件、全体headless1205step成功、SCRIPT ERROR/ERROR0。ユーザー指示でAPK/版数変更なし、配布済0.8.14/code94にPLAY-0252〜0256未収録。Android実機未確認、原作完全一致の未完と既存未解決6件（U-1〜U-6）は維持。
