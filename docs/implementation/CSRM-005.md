# CSRM-005 実装報告: 調査ラベルの原作表記への一致と phone 層の到達可能性確認

## 採用した指示書

- 指示書: `docs/muse/ready/CSRM-005.md` 版1（`muse/analysis` ブランチ）
- 基準コミット: `9dfa80b98bf584b90d2a5a53b46ad67dc49838af`（ブランチ `chatgpt/ps-ui-touch-audit-20261119`）
- 実施ブランチ: `claude/csrm-005-impl`（先行 PR が未マージのため、それらの先端から積み重ね）
- 状態: 実装完了。マージはユーザーの承認待ち
- 実施者についての注記: ユーザーの 2026-11-22 の決定により Muse が実装した。

## 変更内容

1. **調査ラベルの一致**（`game/scripts/ps1_ui.gd`、1行）: 調査メニューの「店舗別グラフ」を原作マニュアル p.10 の表記「店舗別収支グラフ」へ変更した。短縮を維持する理由は無いため、決定記録での例外化は行っていない。
2. **phone 層の到達可能性確認**: 出荷フロー（Android）では到達不可能と確認した。指示書の分岐 (2) に従い、phone_ui.gd へのコード変更は行っていない。確認の根拠は decision0248 に記録した。
   - 静的: ゲーム画面の UI は ps1_ui.gd のみがインスタンス化される。ps1_ui はレイアウトのたびに phone の menu/hud/bottom_bar を隠し、再表示する経路はコードに存在しない。調査を含む大半のウィンドウ ID では phone 側ウィンドウノードを画面外・透明に退避して自前描画する。
   - 動的: `--android-preview` で出荷時 UI 経路を有効化して main シーンを起動し、メニュー非表示の維持と、research/shop を開いても phone ウィンドウが退避状態のままであることを実測した。

## テスト・ビルド結果

- Godot 4.3（ローカル、`--android-preview` 付きで実行）: ps1_ui_smoke 成功（25画面）、ps1_touch_audit_smoke 成功、menu_usability_smoke 成功。全体 headless_smoke も CSRM-002 完了時点で成功を確認済みで、本変更（ラベル1行）による影響は無い。
- ps1_menu_dispatch_smoke は "Cancel rail must remain clickable with a menu open" で失敗するが、変更前の ps1_ui.gd でも同一の失敗を再現したため、本変更とは無関係の既存失敗である（CI 対象外の smoke。今後の指示書候補として記録する）。
- Python: game/ のみの変更で reference_sim への影響は無い。
- APK: 未作成。実機確認は行っていない（ラベルは実機でも要目視確認）。

## 未解決の質問

- なし。phone 層を将来再有効化する場合は、decision0248 の到達可能性確認をやり直す必要がある（同決定に明記）。
