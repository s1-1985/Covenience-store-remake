# 画面・店舗切替の旧操作を取消（APK未更新）

PLAY-0255、基点cbfb1f7ff28b0e2bd5b7cf45f17f741aa07bf0cc、branch `chatgpt/mobile-resume-20261126`。既存PR #286（https://github.com/s1-1985/Covenience-store-remake/pull/286）を更新する。

前の画面の決定処理が次の描画まで残る問題、同名画面再入場でも古いタップが成立する問題、店舗切替前の確認が別店舗へ適用される問題を変更前に再現して修正した。画面/店舗/ページ等の切替時に古いメニュー操作を無効にし、元の指のreleaseは消費する。新しい入力による営業時間設定と他店舗不変を確認した。詳細decision0255。

関連Godot13本、Python804件、全体headless1205step成功、SCRIPT ERROR/ERROR0。実Viewport入力による確認でありAndroid実機確認ではない。ビルド/版数更新なし。配布済0.8.14/code94にはPLAY-0252〜0255が未収録。原作完全一致の未完と既存未解決6件（U-1〜U-6）は維持する。
