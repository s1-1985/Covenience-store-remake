# 0251 — 営業更新後も店内カメラを維持する

## 背景と作業基点

ユーザーの2026-11-26指示「続けて。いつ終わるのか。スマホで再現したい」に対し、通常操作の阻害を優先。基点efa76ff09b88123e2c2e36f1fcdab599c2b11a84、ブランチchatgpt/playability-camera-20261126。最新main688876aと開PR270/284を確認し、自分のPR276までが採用ラインへマージ済みであることを確認。PR284の修正を上書き/マージせず、そのHEADへ差分を積む。PRは作成後追記。

## 再現した症状・原因

店内を拡大/移動した後、実際の_step_source_floor_wear()を1回通しui.layout_screen()を呼ぶと、ズーム/位置が初期化される。新store_camera_persistence_smokeで変更前にexit1「Hourly floor update reset the player's zoom/pan」を再現した。

原因は二つ。store_camera.layoutの店舗判別キーがstore設定辞書全体を文字列化しており、汚れ・清掃値・source_floor_clockの変更まで別店舗扱いして指追跡を消去していた。さらにps1_ui.layout_screenのsuper.layout_screenが旧phone配置の縮尺/座標を毎回書き戻していたため、キーだけ直しても初期化が残った。

## 決定

- 店舗判別はsimulationのinstance ID、店舗UID、表示内容の矩形に限定。汚れや清掃時計だけではreset_viewを呼ばない。
- PS UIで旧phoneレイアウトを呼ぶ際、カメラ所有のTransform2Dを保持/復元する。カメラ初期化前の旧レイアウトは従来どおり。
- 店舗選択や表示寸法が変わった場合はfit/centerし、ドラッグ/ピンチ中の無関係な描画更新では指追跡を保持する。
- 原作シミュレーション、速度、会計/乱数、既存カメラ倍率範囲は変更しない。ユーザー要望のスマホ操作アダプター内のバグ修正である。
- 新回帰に加え、既存mobile_controlsとps1_menu_dispatchをCIへ追加し、操作不具合を次の修正で再導入しにくくする。

## 検証・収録

Godot4.6.3で9本成功、SCRIPT ERRORなし: store_camera_persistence / mobile_controls / ps1_menu_dispatch / ps1_ui / ps1_touch_audit / menu_usability / recovered_game / source_audio_ui / calendar_ui。

新回帰では実際の床更新/床値変更の後も縮尺と位置が同じ、押下中の指を維持、取消で指追跡解除、別店舗選択と寸法変更では中心へ再配置されることを確認。既存mobile_controlsは指ピンチ/パン・△切替・一覧・速度1/4/8/16・64tick同一性を確認。recovered_gameは7200tickの営業/月次/保存/買収等を確認する。

全体headlessは1205step成功、SCRIPT ERROR/ERROR0件。Python804件全成功、外部プラグイン非推奨警告1件。旧カタログ欠落の解消は基点のCSRM-007によるもので、今回の新規修正に数えない。

APK0.8.14-playability/code94を従来touchfix署名v2/v3で出力。store_camera/ps1_ui/touch_controls/vertical_slice_simulationのgdcとsmoke非同梱を確認。PR284の既存レールボタン修正と採用済みCSRM-005/007等も収録される。実機確認・実聴は未実施。完全再現/完成とは呼ばない。

## 変更ファイルと残件

store_camera.gd、ps1_ui.gd、新store_camera_persistence_smoke.gd/uid、native-staff-regression.yml、export_presets.cfg、本文、docs/RELEASE_ACCEPTANCE.md、最新handoff/build/status、PROJECT_MEMORY追記。

完成確認はRELEASE_ACCEPTANCEへ集約。Android実機の通し操作/長時間/中断復帰/原作画面別照合、原通知制御列/原カード/全営業RNG等は未完。既存未解決6件（U-1〜U-6）は維持。Muse ready/レビュー/履歴文書を独断で更新せず、現在の観測を新引継ぎへ記録する。
