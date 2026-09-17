# 0090: `game/`(Godot)に代表4日間→月間集計(確定倍率×8)のサイクルを実装する

## 背景

タスク#23として「日次/月次ゲームループ」に着手した。`game/`(Godot vertical slice)の
`minute_of_day`はこれまで24時間で単に剰余(`% (24 * 60)`)を取って無限にラップするだけで、
「日」「月」という区切り自体が存在しなかった。

一方`reference_sim/conveni_sim/month_aggregation.py`には、攻略本のクイックリファレンスに
明記された`CONFIRMED_OFFICIAL`(推測ではなく確定)の値として次の関係が実装済みである。

> "1月=4日間×8" / "4日間の収支を8倍することで、1月の収支が決定する。実質32日間の営業と
> 考えよう。"

これは決定書0087/0088/0089とは異なり、係数自体がREMAKE_BALANCED_DEFAULTの推測ではなく、
攻略本が直接明記した確定値である。今回はこの確定式をGodot側に移植した。

## 決定

### 実装した内容

- `vertical_slice_simulation.gd`にクラス定数`REPRESENTATIVE_DAYS_PER_MONTH := 4`と
  `MONTH_MULTIPLIER := 8`を追加(`reference_sim`と同じ値、CONFIRMED_OFFICIALである根拠を
  コメントで明記)。
- `minute_of_day`の進行を`_advance_minute_of_day()`に集約。24時60分を超えるたびに
  `_handle_day_boundary()`を呼び、`day_count`を1増やす。
- `_days_completed_this_month`が`REPRESENTATIVE_DAYS_PER_MONTH`に達すると
  `_settle_month_end()`を実行する:
  - `four_day_net_result_yen = economy.cash_yen - _cash_at_month_start`
    (月初からの4日間で実際に動いたキャッシュフローの純額)
  - `month_result_yen = four_day_net_result_yen * MONTH_MULTIPLIER`
  - その差額(`month_result_yen - four_day_net_result_yen`、つまり8倍のうち
    「実際にシミュレートしていない残り7倍分」)を、新設した
    `EconomyState.record_month_end_settlement()`で一括計上する。
  - `month_count`を1増やし、`_cash_at_month_start`を更新して次の月のカウントを開始する。
- `EconomyState`に`month_end_records`配列と`record_month_end_settlement()`を追加。
  既存の`sale_records`/`expense_records`と同じパターンの、正負どちらの値も扱える
  イミュータブルな記録配列。
- `_record_event("month_end_settlement", {...})`でイベントログにも記録する。

### 何を発明していないか

攻略本が確定しているのは倍率(×8)そのものであり、「4日間それぞれの収支をどう計算するか」
(どの経費が含まれるか、代表4日目=休日を他の3日と同じ重みで扱ってよいか等)は確定していない。
本実装は`reference_sim`の`aggregate_representative_days_to_month()`と全く同じ立場を取り、
「4日間の純キャッシュ変動」という、呼び出し側(=このシミュレーション自身の`economy.cash_yen`)
が既に計算済みの値をそのまま8倍するだけである。日次の内訳を分解したり、代表日ごとに異なる
重みを与えたりする独自ロジックは一切追加していない。

### JSON設定への影響なし

この機能は攻略本確定値であるため、`REMAKE_BALANCED_DEFAULT`の各種機能(需要・補充)とは異なり
`data/vertical_slice.json`に新しい調整可能な設定キーを追加していない
(`REPRESENTATIVE_DAYS_PER_MONTH`/`MONTH_MULTIPLIER`はGDScript側の定数のまま)。
`schema_version`も7のまま変更していない。

## 影響

- `game/scripts/vertical_slice_simulation.gd`: `REPRESENTATIVE_DAYS_PER_MONTH`/
  `MONTH_MULTIPLIER`定数、`day_count`/`month_count`/`_days_completed_this_month`/
  `_cash_at_month_start`フィールド、`_advance_minute_of_day`/`_handle_day_boundary`/
  `_settle_month_end`メソッドを追加。`step()`/`tick_idle_for_demand()`の両方が
  `_advance_minute_of_day()`を呼ぶよう変更(既存の直接的な剰余計算を置き換え)。
  `snapshot()`に`day_count`/`month_count`を追加。
- `game/scripts/domain/economy_state.gd`: `month_end_records`配列と
  `record_month_end_settlement()`を追加。
- `game/scripts/headless_smoke.gd`: 需要ゼロの専用構成で4日間ちょうど経過させ、
  手動補充で作った既知の収支から月末調整額が`four_day_net_result_yen × 8`と一致すること、
  調整の記録・イベントログが正確であることを検証するテストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 本機能の存在と
  CONFIRMED_OFFICIALタグを検証する新規contractテストを追加。
- 既存のvertical sliceのテストシナリオ(`start_minute_of_day: 540`)は、テスト内で実行される
  ステップ数が900分(=真夜中まで)に遠く及ばないため、この変更によって挙動が変化しない
  ことを確認済み。
