# 再開点：0.6.4 PSタイトルとタッチ監査

基準22ba479。今回の変更は `docs/decisions/0213-ps-title-readable-touch-and-staff-transfer.md` を参照。

- Androidタイトルは `ps1_title.gd`。原TIM2枚、原登場/START待ち/10分割/2択。既存難易度選択は別画面。
- PS風UIの文字は同梱Noto。原配色とテクスチャを維持。元文字一覧をフォントに全収録。
- Native指入力、店員ドラッグ異動、無効ドロップ取消。異動後は原処理どおり新しい控え室へ。
- SEと月次報告の逆転を修正。原音源がある時は旧合成効果音を抑止。
- 8本の関連Godot確認が成功。Python786成功、既存2失敗、想定失敗1。全体headlessの旧町パネル条件失敗も元から存在。実機未確認。
- APK64は既存touchfix署名/パッケージで作成。鍵を毎回新規に作らない。秘密鍵は既存の非公開署名ZIPを再利用し、Gitへ含めない。
- 既存未解決6件は触らない。起動動画、原シナリオ説明、売却、グラフ履歴等は未完。

再確認は `ps1_title_smoke.gd`、`ps1_ui_smoke.gd`、`ps1_touch_audit_smoke.gd`、`source_audio_ui_smoke.gd` に `-- --android-preview`。加えて `staff_response_smoke.gd`、`source_people_smoke.gd`、`floor_lifecycle_smoke.gd`、`floor_ui_smoke.gd -- --android-preview`。
