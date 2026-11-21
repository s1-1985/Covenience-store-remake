# CSRM-004 実装報告: レビューメモ項目3・12の解消（force_eject と cancel_customer の整合性）

## 採用した指示書

- 指示書: `docs/muse/ready/CSRM-004.md` 版1（`muse/analysis` ブランチ、コミット `2b3e990aacf69487520ca1ffd7b6519df7285fdb`）
- 基準コミット: `9dfa80b98bf584b90d2a5a53b46ad67dc49838af`（ブランチ `chatgpt/ps-ui-touch-audit-20261119`）
- 実装ブランチ: `claude/csrm-004-impl`（基準コミットから分岐）
- 状態: 実装完了。マージはユーザーの承認待ち（PR を参照）
- 実装者についての注記: 本件はユーザーの 2026-11-22 の指示により、従来の「Muse は解析のみ」分業を試行的に離れ、Muse が実装まで行ったパイロットである。

## 変更ファイル

- `reference_sim/conveni_sim/checkout.py`
  - `refresh_waiting()` が、セッション状態が WAITING_CHECKOUT でなくなった接客割当を解放する（`_release_stale_services()`。担当店員は roster 上 IDLE へ戻る）。項目3。
  - `cancel_customer()` が取消集合へ記録し、`refresh_waiting()` は取消済みの客を再登録しない。取消はセッションが WAITING_CHECKOUT に留まる間だけ有効で、状態遷移で失効する（再入場は状態遷移で判断）。項目12。
- `reference_sim/conveni_sim/store_runtime.py`
  - `finish_checkout_sale()` が接客中客の解決前に `checkout.refresh_waiting()` を呼び、eject 済みの客については精算前に KeyError で止まるようにした（精算だけが済む部分適用の解消）。項目3。
- `reference_sim/tests/test_staff_checkout.py`: 回帰テスト3件追加（項目3の割当解放、項目12の非復活、到着前 cancel の過剰ブロック防止）。
- `reference_sim/tests/test_known_issues.py`: 回帰テスト1件追加（項目3: eject 済み接客中客が finish_checkout_sale で精算されないこと）。
- `docs/decisions/0239-checkout-eject-cancel-consistency.md`: 新規作成（結合の置き場所と取消意味論の決定記録）。
- `PROJECT_MEMORY.md`: 第19節末尾へチェックポイントを追記。

## 指示書からの逸脱

- なし。結合の置き場所（チェックアウト側の refresh 時整合＋取消集合、`finish_checkout_sale` の精算前整合）は指示書が実装側の選択に委ねた範囲であり、理由を decision0239 に記録した。

## テスト・ビルド結果

- 着手前基線（基準コミット、ローカルで実測）: Python 789件 = 786成功／2失敗／想定失敗1。
- 修正前: 追加した再現テスト4件のうち3件が期待どおり失敗（接客割当の残留、取消の復活、精算の部分適用）。残り1件（到着前 cancel の過剰ブロック防止）は修正前後とも成功するガードテスト。
- 完了後: Python 793件 = 790成功／2失敗／想定失敗1。基線からの悪化なし。
- 残る2失敗は着手前から存在し、今回初めてテスト名を特定した（CSRM-002 の対象）:
  - `test_game_vertical_slice_contract.GameVerticalSliceContractTests.test_slim_engine_template_keeps_what_the_game_uses`
  - `test_game_vertical_slice_contract.GameVerticalSliceContractTests.test_store_site_is_chosen_freely_with_a_land_price_per_site`
- 想定失敗1はメモ項目11（CSRM-002 の対象）で不変。
- Godot: コード変更が無いため smoke は実施していない（下記の同型確認はコード精読による）。
- APK: 作成していない（本指示書では必須とされていない）。実機確認: 行っていない。

## Godot 側の同型問題の確認結果（指示書 §7）

- `game/scripts/vertical_slice_simulation.gd` の `try_eject_customer()` は、待ち客なら `_checkout_queue` から除去し、接客中なら `staff.checkout_staff().state = "idle"` へ戻す。項目3型の「割当が残る」不整合は無い。
- `_checkout_queue` への登録は `_advance_customer` のフェーズ遷移時に一回だけ行われ、セッション状態を走査して再登録する refresh 相当の経路が存在しない。項目12型の「取り消した客の復活」は構造上起きない。取消に相当する独立 API も無い。
- 断念経路 `_program_wait_at_checkout()` も、キュー除去とレジ担当の idle 化を対で行う（なお断念時は原作証拠に基づきバスケットを先に精算する設計で、eject とは意図的に異なる）。
- 結論: Godot 側に同型の問題は無く、変更は不要。

## 未解決の質問

- なし。
