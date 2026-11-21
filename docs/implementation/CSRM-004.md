# CSRM-004 v1 — 実装報告

- 採用指示書: muse/analysis / 2b3e990aacf69487520ca1ffd7b6519df7285fdb / docs/muse/ready/CSRM-004.md v1
- 基準コミット: eaaab30bdafda034467f6d54d2886cd13d282f99
- 実装ブランチ: chatgpt/muse-runtime-consistency-20261121
- PR: #273 https://github.com/s1-1985/Covenience-store-remake/pull/273
- マージ: 未実施、Museレビュー待ち

## 実装

force_eject時に登録済みレジへ通知し、担当者と待機割当を即時解放。cancel_customerはCHECKOUT_CANCELLED状態とsettlement_blockedを持続し、refreshだけで復帰させない。明示resume_checkoutだけが通常の接近経路へ戻せる。これらは参照ハーネスの技術的状態で、PS由来の追加ルールとはしない。

完了処理・セルフ精算・低層purchases.settleへ防御を追加し、古い時間完了通知でも強制退店客を精算しない。罰金・返金・商品返却等は追加しない。回帰4件を追加した。

Godot本体にも相当不具合を確認。try_eject_customerがphaseだけ変更して原状態3/旧目標を残し、次のnative更新で会計できた。既存ProgramPeople.change_state(customer,5)へ接続し、原退店経路へ遷移。nativeレジ担当者は人物ごとの割当モデルではないためPythonのIDLEを機械的に移植していない。新しいejection_consistency_smokeでは会計直前退店、未払い保持、現金/売上不変、JSON再開と乱数/位置一致、退出完了を確認。CI対象へ追加。

## 完了条件・逸脱

逸脱なし。対象回帰とAndroidビルド完了。広域headlessに残る別の構成欠落をCSRM-002へ分離。実機動作/実聴は未確認。Museレビュー待ち。

## 検証結果

Python変更前は786成功・2失敗・1想定失敗。失敗は GameVerticalSliceContractTests.test_slim_engine_template_keeps_what_the_game_uses（旧テンプレート空文字期待）、同test_store_site_is_chosen_freely_with_a_land_price_per_site（旧ガード文字列）。想定失敗は StoreStepKnownIssueTests.test_a_failing_purchase_phase_does_not_leave_the_clock_advanced。

変更後は全793成功、0失敗、想定失敗0。外部pytestプラグインの非推奨警告1件。コマンド: `PYTHONPATH=reference_sim python -m pytest -q reference_sim/tests`（実行環境の追加依存パスも指定）。Godot4.6.3関連9本（ejection_consistency / abandonment / operating_audio / source_people / staff_response / people_service_ui / staff_lifecycle / source_operations / source_notifications）はSCRIPT ERRORなしで成功。

全体headless_smokeの旧町寸法失敗は、docs/ANDROID_PS_UI_HANDOFF.mdのdesktop据置仕様に合わせ12へ訂正。次に買収後の調査キー保持という旧期待を、docs/handoff/2026-11-20-rival-inspection.mdの「買収後の調査キー消去」に合わせ訂正。保存読込も消去を確認する。最終実行は1205stepsの末尾passedへ到達したが、途中で `_step_manager_reports`（vertical_slice_simulation.gd:893）の `config.source_catalog` 欠落SCRIPT ERRORを5回検出したため、全体合格とは判定しない。`_real_game_simulation()` は旧GuideStartingStore構成で、このエラーは会計退店回帰とは別。ソースカタログ無しの旧構成を引き続きサポートするか、テスト構成を本体へ移行するかはMuseへ戻す。例外を握り潰す変更はしない。

## 変更ファイル（同一PRの2指示書を合算）

- `.github/workflows/native-staff-regression.yml`
- `game/export_presets.cfg`
- `game/scripts/headless_smoke.gd`
- `game/scripts/vertical_slice_simulation.gd`
- `reference_sim/conveni_sim/checkout.py`
- `reference_sim/conveni_sim/customer.py`
- `reference_sim/conveni_sim/purchases.py`
- `reference_sim/conveni_sim/store_runtime.py`
- `reference_sim/conveni_sim/store_step.py`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `reference_sim/tests/test_known_issues.py`
- `reference_sim/tests/test_staff_checkout.py`
- `reference_sim/tests/test_store_runtime.py`
- `game/scripts/ejection_consistency_smoke.gd`
- `game/scripts/ejection_consistency_smoke.gd.uid`

報告・決定: docs/implementation/CSRM-004.md、docs/decisions/0242-reference-step-atomicity-and-test-baseline.md、docs/decisions/0243-checkout-cancel-eject-consistency.md、最新handoff/build/status、PROJECT_MEMORY第19節追記。
