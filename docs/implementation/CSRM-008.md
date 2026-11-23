# CSRM-008 実装報告: レールボタンの重なり配送の是正

## 採用した指示書

- 指示書: `docs/muse/ready/CSRM-008.md` 版1（`muse/analysis` ブランチ）
- 基準コミット: `b75fef5882808a7a26b71f53709dc8b5772821bd`（ブランチ `chatgpt/ps-ui-touch-audit-20261119`、ChatGPT チェーン・CSRM-005/006/007 のマージ後）
- 実施ブランチ: `claude/csrm-008-impl`
- 状態: 実装完了。マージはユーザーの承認待ち
- 実施者についての注記: ユーザーの 2026-11-22 の決定により Muse が実装した。

## 変更内容

- `game/scripts/touch_controls.gd`
  1. `_input` の手動タッチ配送: タッチ点を含むボタンの中から、中心が最も近いボタンを選ぶよう変更した（従来は最初に一致した子ボタン）。重なり帯以外では選択は従来と同一。
  2. 最下段ボタン（SELECT / START）の配置を y=620 から y=606 へ移し、実効高さ114pxでも画面（720px）内に収まるようにした。
- 選択した方法と理由は decision0250 に記録した（指示書の選択肢 (a) + (c) の部分的適用。(b) 実効高さの是正は影響範囲が広いため不採用）。
- `handle_cancel` / `handle_accept` には触れていない。

## テスト・ビルド結果

- 修正前（基準コミット）: ps1_menu_dispatch_smoke は "Cancel rail must remain clickable with a menu open" で失敗（チェーン先端でも再現済み）。
- 修正後（Godot 4.3 ローカル）: ps1_menu_dispatch_smoke が成功（PS1_MENU_DISPATCH_PASS）。ps1_ui_smoke、ps1_touch_audit_smoke、menu_usability_smoke も成功。全体 headless_smoke は SCRIPT ERROR 0件で passed。
- Python: 804件全成功。
- APK: 未作成（指示書の完了条件に含まれていない）。

## 提案・未解決の質問

- 指示書の提案どおり、ps1_menu_dispatch_smoke を CI の godot ジョブへ追加することを推奨する。追加の可否はリポジトリ所有者の判断とする（本実装では CI 設定を変更していない）。
- 未解決の質問はなし。既存未解決6件（U-1〜U-6）は維持。
