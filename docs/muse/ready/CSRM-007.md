# CSRM-007: `_step_manager_reports` の source_catalog 無防備アクセスの解消

- 指示書ID: CSRM-007
- 版: 1
- 優先順位: 6
- 対象リポジトリ: s1-1985/Covenience-store-remake
- 対象実装ブランチ: 実装時点の最新候補ブランチ（着手時に再確認すること）
- 基準コミット: 着手時点の対象ブランチ先端（着手時に完全なSHAを固定すること）

## 目的・背景
全体 `headless_smoke.gd` は末尾の passed へ到達するが、途中で `_step_manager_reports`（game/scripts/vertical_slice_simulation.gd、893行付近）が `config.source_catalog.product_ids` へ無防備にアクセスし、`source_catalog` を持たない構成（smoke の `_real_game_simulation()` が使う旧 GuideStartingStore 構成）で SCRIPT ERROR が5回発生する。CSRM-002 の完了条件（全体 headless の成功）に対する残件として、ChatGPT の実装報告（PR #273）が論点を分離し、Muse の比較レビュー（analysis/2026-11-22-dual-implementation-review.md）が方針を示した。

## 根拠
- 同ファイル内には `config.has("source_catalog")` で守ってから使う前例がある（_recovery への merge 経路、284行付近）。
- 実ゲームの構成では source_catalog は常に存在する（上記の merge で _recovery に取り込まれる）。エラーになるのは旧構成を使うテスト経路のみ。
- エラーを握り潰す変更はしない（PR #273 の報告方針を踏襲）。

## 対象ファイル
- game/scripts/vertical_slice_simulation.gd（`_step_manager_reports` の該当アクセス箇所）

## 変更内容
- 該当箇所の `config.source_catalog.product_ids` アクセスを、同ファイルの既存パターンに合わせてガードする（source_catalog が無い構成では、その報告候補の生成を「候補なし」として扱う。実ゲーム構成での動作・乱数消費順は変えない）。
- ガードの形は既存の has() 前例に合わせ、独自の例外処理や握り潰しを入れない。

## 対象外
- smoke 側のテスト構成（_real_game_simulation）を本体構成へ移行する作業は本件に含めない（別途必要なら別指示書とする）。
- マネージャーレポートの内容・頻度・乱数仕様の変更。

## 完了条件
- 全体 headless_smoke.gd が SCRIPT ERROR 0件で passed へ到達する。
- 関連 smoke（operating_statement_smoke、source 系の関連 smoke）に悪化が無い。
- Python 全テストが成功を維持する。
- 実装報告 docs/implementation/CSRM-007.md、決定記録（次の空き番号）、PROJECT_MEMORY.md 第19節への追記（U-1〜U-6 併記）を作成する。

## 必要な確認
- Godot headless: headless_smoke.gd（全体）、operating_statement_smoke.gd。
- Python: reference_sim 全テスト。

## 既知の失敗
- 本件で解消する SCRIPT ERROR 以外の既知失敗は、着手時点の基線に従う（着手時に再測定して報告へ記録すること）。

## 依存する指示書
- CSRM-002（本件はその残件）。実装側の採用ライン（ChatGPT チェーン）へ積む場合は、その先端を基準にする。

## ユーザー判断事項
- なし（方針は比較レビューで提示済み。ガード方式に異論がある場合は着手前にユーザーへ確認すること）。
