# 0148: 内装編集への「入れ替え」「売却」「終了」コマンドの追加(タスク#78)

## 背景

タスク#77(カレンダー表示修正)と同じ、ユーザーからの再現度ドリフト
指摘への対応の続き。`docs/research/menu-hierarchy-evidence-2026-09-05.md`
/`official-ui-state-reconstruction-2026-09-05.md`/`version-boundary-
original-vs-2-2026-09-05.md`はいずれも、公式PS画像(`ss02`)から内装
編集画面のトップコマンドが`配置`/`移動`/`入れ替え`/`売却`/`終了`の
5つであることをCONFIRMED_OFFICIAL/VISUALとして確認している。

このクライアント(`game/`)は`配置`(`try_purchase_fixture`)と`移動`
(`try_relocate_fixture`)に相当する機能を既に持っていたが、`入れ替え`
`売却``終了`に相当する機能は一度も実装されておらず、`docs/decisions/`
のどのファイルもこの5コマンド構造への言及がなかった。

さらに調査したところ、タスク#37(サンプルレイアウト読み込み)の
既存コントラクトテストに`self.assertNotIn("func try_sell_fixture",
simulation)`という、当時の調査ノート(`docs/research/ss-layout-
entrance-register-and-chain-cannibalization-2026-09-06.md`)が
「`sell/remove fixture`は別途の調査課題として保留する」としていた
境界を明示的に固定するアサーションが存在していた。今回はユーザーの
承認を得た上でこの境界を意図的に見直し、そのテストを更新した
(`try_undo_sample_layout`が引き続き対象外であることは維持)。

## 決定

### 発明が必要な2箇所は REMAKE_BALANCED_DEFAULT で進める(ユーザー承認済み)

ユーザーに確認したところ、「REMAKE_BALANCED_DEFAULTで発明して進める」
との回答を得た。

1. **売却の払い戻し率**: `FIXTURE_SELL_REFUND_PERCENT := 50`
   (`vertical_slice_simulation.gd`)。カタログ購入価格の50%を返金する
   ——「返金なし」と「全額返金」の中間という、それらしい妥協点。
   根拠となる確定データは存在しない。
2. **入れ替えの意味**: 「既に配置済みの2つの什器の位置を直接交換する」
   と解釈した。これは`移動`(単一什器を空きセルへ移動)では実現
   できない唯一のケース(什器が密集していて、どちらの什器も
   経由できる空きセルがない場合)に対応する、区別された第3の
   コマンドとして意味を持つ最も自然な読みである。

### 実装

- `store_layout.gd`: `try_remove_fixture(fixture_id)`(バリデーション
  再チェック不要——什器を減らすだけなので既存の妥当なレイアウトを
  不正にすることはあり得ない)、`try_swap_fixture_positions(id_a,
  id_b)`(`try_move_fixture()`と同じdelta-shift方式を2什器へ同時適用)。
- `vertical_slice_simulation.gd`: `try_sell_fixture(fixture_id)`
  (ゲームオーバー/客未精算/補充作業中でないことに加え、チェックアウト
  什器自体は売却不可、カタログ出自のない什器(プロトタイプ什器)は
  価格が不明なため売却不可、在庫を保持中の什器は`try_load_sample_
  layout()`が既に確立した「在庫を黙って破棄せず拒否する」という
  前例をそのまま踏襲して売却不可)、`try_swap_fixtures(id_a, id_b)`
  (他の什器編集アクションと同じ、ルート到達性・店員歩行可能性の
  ロールバック検証パターンを踏襲)。
- `economy_state.gd`: `record_explicit_expense()`の`amount_yen >= 0`
  アサーションを緩和し、負の値(返金)を同じ元帳経由で記録できる
  ようにした。既存の呼び出し元は全て非負の値のみを渡していたため、
  この変更は既存呼び出し元の挙動を一切変えない。
- `store_view.gd`: `edit_mode`("move"既定/"swap")を追加。"swap"
  モード中に2つ目の什器をタップすると、既存の「選択し直す」動作の
  代わりに新規`fixture_swap_requested`シグナルを発火する——"move"
  モードの既存タップ挙動は完全に維持。
- `main.tscn`/`main.gd`: `EditModeOption`(Move/Swap切替)、
  `SellFixtureButton`(売却、50%返金)、`DeselectFixtureButton`
  (終了に相当する選択解除)を追加。

## テスト

- `reference_sim`フルスイート743件パス/1件xfail(741→743、新規
  コントラクトテスト1件+タスク#37の旧境界テスト更新1件)。
- `game/scripts/headless_smoke.gd`: ドメイン層で`try_sell_fixture`
  (チェックアウト拒否・カタログなし拒否・在庫保持拒否・正常売却の
  返金額検証・イベント記録)と`try_swap_fixtures`(自己交換拒否・
  不明ID拒否・正常交換の位置検証・イベント記録)を直接検証。UI層
  (`economy_ui_scene`)でも`EditModeOption`/`SellFixtureButton`/
  `DeselectFixtureButton`の実際の配線を検証。ローカルにGodot実行
  環境がないためCIで最終検証。

## 対象ファイル

- `game/scripts/domain/store_layout.gd`
- `game/scripts/domain/economy_state.gd`
- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/store_view.gd`
- `game/scripts/main.gd`
- `game/scenes/main.tscn`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- `try_undo_sample_layout`(サンプルレイアウト読み込みの取り消し)は
  引き続き対象外——タスク#37の元の境界のうち、今回見直したのは
  `sell/remove fixture`のみ。
- `reference_sim`側への同等ロジックの移植は行っていない——
  `reference_sim`にはこのクライアントの什器編集アクション自体に
  相当する実行モデルが存在しない(タスク#74の決定0144が同じ理由で
  `_checkout_queue`について明示した対象外事項と同様)。
- `入れ替え`の別解釈(同じ位置の什器を別カタログ品目に交換する、
  という読み)は採用しなかった——上記の通り、この方が`移動`との
  機能的な差別化が明確だと判断したため。
