# 0249 — `_step_manager_reports` の source_catalog アクセスのガード（CSRM-007）

## 背景
全体 `headless_smoke.gd` は末尾の passed へ到達するが、途中で `_step_manager_reports`（game/scripts/vertical_slice_simulation.gd）が `config.source_catalog.product_ids` へ無防備にアクセスし、`source_catalog` を持たない旧構成（smoke の `_real_game_simulation()` が使う GuideStartingStore 構成）で SCRIPT ERROR が5回発生していた。CSRM-002 の完了条件に対する残件として ChatGPT の実装報告（PR #273）が論点を分離し、Muse の比較レビュー（docs/muse/analysis/2026-11-22-dual-implementation-review.md）が方針を示し、指示書 CSRM-007 が切り出された。ChatGPT チェーンの 0.8.13 チェックポイント（decision0246）でも「全体headless既存source_catalog欠落SCRIPT ERROR5回は継続」と引き継がれていた。

## 決定
当該アクセスを、同ファイル内の既存前例（`config.has("source_catalog")` で守ってから使う、_recovery への merge 経路）と同じ形でガードする。`source_catalog` が無い構成では product_ids を空配列として `program_manager_reports.candidates` へ渡す。candidates は順序が空なら best/worst とも空を返すため、その回の売上報告は発生しない。エラーを握り潰す処理は入れない。

## 影響
- 実ゲームの構成では `source_catalog` は常に存在する（起動時に _recovery へ merge される）ため、実ゲームでの動作・乱数消費順は一切変わらない。ガードの前にある乱数ロールにも触れていない。
- 旧構成では、従来は SCRIPT ERROR で関数が中断し末尾のカウンタリセット（`_sold_counts` 等）も実行されなかったが、ガード後は関数が最後まで実行され、実ゲーム構成と同じ後処理になる。

## 確認
- Godot 4.3（ローカル）: headless_smoke.gd が SCRIPT ERROR 0件で "passed in 1205 steps" へ到達（修正前は同一条件で SCRIPT ERROR 5件）。operating_statement_smoke、source_notifications_smoke、source_operations_smoke も成功。
- Python: 793件全成功（本変更は Godot 側のみ）。
- APK は作成していない。基準は採用ライン（ChatGPT チェーン）先端であり、ビルドは同チェーンの流れに委ねる。
