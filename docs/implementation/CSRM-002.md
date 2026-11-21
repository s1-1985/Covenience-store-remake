# CSRM-002 v1 — 実装報告

- 採用指示書: muse/analysis / 2b3e990aacf69487520ca1ffd7b6519df7285fdb / docs/muse/ready/CSRM-002.md v1
- 基準コミット: eaaab30bdafda034467f6d54d2886cd13d282f99
- 実装ブランチ: chatgpt/muse-runtime-consistency-20261121
- PR: 作成後追記
- マージ: 未実施、Museレビュー待ち

## 実装

StoreStepOrchestrator.stepの実行前に所有するconveni_simオブジェクト・可変コンテナ・Random状態を記録し、例外時は同一オブジェクトへ復元して再送出する。外部が保持したセッション・リストの参照も維持。通常の呼出し/乱数順は変更しない。外部ポリシー自身の副作用は対象外。Android本体はこのPython処理を実行しない。

既知失敗を通常の回帰へ変更し、時計だけでなく途中購入の在庫/現金/セッション/入れ子リスト/乱数と再試行を確認。古い契約テスト2件と根拠付きのheadless期待2件を更新した。

## 完了条件・逸脱

原子的stepとPython全件は完了。全体Godotの合格条件は未達のためCSRM-002全完了とはしない。指示書の未確定事項を保留する扱いに従い、上記カタログ欠落をMuseへの確認事項として分離した。仕様の独自置換なし。

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

報告・決定: docs/implementation/CSRM-002.md、docs/decisions/0242-reference-step-atomicity-and-test-baseline.md、docs/decisions/0243-checkout-cancel-eject-consistency.md、最新handoff/build/status、PROJECT_MEMORY第19節追記。
