# 0122: 価格設定(値引き)メカニクスの配線(タスク#53)

## 背景

タスク#52までの一連のPDF再読と並行して、`store_rating.gd`/`store_value.gd`
(タスク#27)以来ずっと`price_change_pct`(店舗評価の増加・減少要因の1つ、
書籍p.38-39の「販売価格率」列)が固定で`0`のまま渡され続けていた
(`VerticalSliceSimulation._evaluate_store_rating()`の既存コメント:
「No price-setting mechanic exists in this vertical slice yet」)。

「クイックリファレンス」book pp.5-6を直接再読したところ、以下の明文・
画面写真を確認した:

- p.5: 「商品価格を決定して下さい。利益率の割合。通常は全て40%に設定
  されており、これが定価と考えられる。個別に設定」
- p.6付近のスクリーンショット: 「全商品平均利益率 20% / 全体に設定
  <20%OFFに> / 個別に設定」という、全商品一律の値引き率スライダーと、
  商品ごとの個別設定の両方が存在するUI。

これはCONFIRMED_OFFICIALな一次資料であり、`PROJECT_MEMORY.md`第21.3節に
「まだ未実装の候補」として記録されていた。本タスクではこの欠落
メカニクスを実装した。

## 決定

### `VerticalSliceSimulation.try_set_price_policy(new_price_change_pct: int) -> bool`(新規)

プレイヤーが設定する「定価からの変化率」(全商品一律)を保持する新しい
状態`price_change_pct`(既定値0 = 変化なし、書籍の「通常は40%が定価」と
いう基準線の解釈に対応)を追加した。`-100`未満(定価の0%を下回る=あり
得ない値引き)は拒否する――これは書籍に明記された下限ではなく、この
プロジェクト独自のREMAKE_BALANCED_DEFAULTな健全性チェックである。

### 実際の販売価格への反映

客が商品を棚から取った瞬間(`inventory.try_take_one()`が返す確定済みの
`unit_price_yen`、すなわち`product_catalog`のCONFIRMED_OFFICIALな定価)に
対して、新規ヘルパー`_apply_price_policy()`が`price_change_pct`を適用し、
実際に会計時に請求される単価を決定する。端数(1円未満)の切り捨てはこの
プロジェクト独自のREMAKE_BALANCED_DEFAULT選択。

### 月次店舗評価への反映

`_evaluate_store_rating()`が`evaluate_monthly_rating_change()`へ渡す
第2引数を、ハードコードされた`0`から実際の`price_change_pct`へ変更した。
これによりタスク#27以来ずっと機能していなかった「価格改定と評価変動」
の連動が、ついに実際にプレイヤー操作から到達可能になった。

### 意図的に配線しなかったもの

- **商品ごとの個別価格設定**: 書籍は全体スライダーと個別設定の両方を
  示しているが、このタスクでは全体スライダーのみを実装した
  (REMAKE_BALANCED_DEFAULTなスコープ限定であり、原作に個別設定が
  存在しないという主張ではない)。
- **価格が客の来店(需要)に与える影響**: `PROJECT_MEMORY.md`第8節は
  「merchandise price」が顧客独占率の確認済み要因の1つだとしている。
  しかし価格→需要の具体的な公式はどの一次資料にも存在しないため、
  `demand_policy.gd`の来客率計算は`price_change_pct`から独立したまま
  にした。ここに発明した公式を追加するのは、このタスクの「既に確定
  している`price_change_pct`消費先(月次評価)を配線する」という狭い
  スコープを大きく超える。

### セーブ/ロード

`price_change_pct`は`popularity`等と同じ扱いの永続状態として
`snapshot()`/`save_state()`/`load_state()`へ追加した。既存セーブ
データとの構造的な互換性が変わるため、`SAVE_SCHEMA_VERSION`を2から
3へ引き上げた(タスク#30が2へ上げた際と同じ理由・同じ運用)。

## テスト

- `game/scripts/headless_smoke.gd`: 新規シナリオを追加。(a) `-101%`の
  拒否と状態不変、(b) 有効な`-50%`設定の受理と`price_policy_changed`
  イベント記録、(c) 実際に-50%設定下で商品を購入した客の合計金額が、
  両商品の定価の50%(各々切り捨て)の合計と正確に一致すること、を検証。
  Godot 4.3公式バイナリで957ステップ(タスク#52時点の897から、新規
  シナリオ分増加)でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_price_policy_action_is_wired_and_confirmed_official`を追加。
  evidence_noteのタグ、バックエンド関数・月次評価への配線・セーブ/
  ロード対応・UI配線を検証。また、タスク#27時点の既存テストが
  `price_change_pct`が常に`0`であることを直接文字列アサートしていた
  箇所(陳腐化)を、新しい配線を反映するよう修正した。フルスイート
  665件(新規テスト関数1件追加)、xfail 1件、全てPASS。

## 実装ファイル

- `game/scripts/vertical_slice_simulation.gd`: `price_change_pct`状態、
  `try_set_price_policy()`、`_apply_price_policy()`を新規追加。
  `_evaluate_store_rating()`・`snapshot()`・`save_state()`・
  `load_state()`・`_require_save_data()`を更新。`SAVE_SCHEMA_VERSION`を
  2→3へ。
- `game/data/vertical_slice.json`: `simulation.price_policy_evidence_note`
  を新規追加。
- `game/scenes/main.tscn`: `PriceChangeSpinBox`(SpinBox)/
  `SetPricePolicyButton`ノードを追加。
- `game/scripts/main.gd`: `_on_set_price_policy_pressed()`を新規追加し、
  `_refresh_ui()`から現在の価格ポリシーを表示するよう配線。
- `game/scripts/headless_smoke.gd`: 新規シナリオを追加、構造チェックの
  対象ノードリストへ2件追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テスト
  を追加、タスク#27時点の陳腐化したアサーションを修正。

## 明示的に対象外とした限界

- 商品ごとの個別価格設定UIは実装していない(上記の通り)。
- 価格変更が客の来店率・需要に与える影響は配線していない(確認済みの
  公式が存在しないため)。
- 価格変更に対するクールダウンや、月内での複数回変更に関する制限は、
  書籍に明記がないため一切設けていない(いつでも何度でも変更可能)。
