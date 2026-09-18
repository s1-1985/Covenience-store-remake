# 0091: `game/`(Godot)に経営破綻・100年制限ゲームオーバーを実装する

## 背景

タスク#24として「経営破綻・シナリオクリア条件」に着手した。`reference_sim/`には既に
2つの独立したゲームオーバー経路が、いずれも`REMAKE_BALANCED_DEFAULT`ではなく
**確定情報**として実装されている。

1. `reference_sim/conveni_sim/month_boundary.py`の`MonthBoundaryTerminalGate`/
   `MonthBoundaryBankruptcyPolicy`: PS版の実機映像とSS版のプレイ記録が、月/日境界で
   現金がマイナスになった場合の破産(ゲームオーバー)を裏付けている
   (`bankrupt_when_negative: bool = True`)。一方、現金がちょうど0になる場合の挙動は
   裏付けとなるサンプルが存在しないため、`bankrupt_when_zero: Optional[bool] = None`
   として明示的に未解決のまま残されている。
2. `reference_sim/conveni_sim/store_events.py`の`scenario_time_limit_exceeded()`:
   攻略本が示す、クリア条件を達成しないまま100年(`GAME_OVER_YEAR_LIMIT = 100`)が
   経過した場合のもう一つのゲームオーバー経路。

決定書0086は、`shoplifting`の`customer_manner_value`連携と並び、この
`month_boundary.py`のゲームオーバー統合を「シナリオの`clear_condition_met`判定機構自体が
まだ存在しないため見送った」項目として記録していた。今回、タスク#23で追加した
月次決算(`_settle_month_end()`)がまさにこの統合の自然な差し込み点になったため、
このタイミングで実装した。

## 決定

### 実装した内容

- `vertical_slice_simulation.gd`に`GAME_OVER_YEAR_LIMIT := 100`と
  `MONTHS_PER_YEAR := 12`(`reference_sim/conveni_sim/observations.py`と同じ値)を追加。
- `is_game_over: bool`/`game_over_reason: String`/`clear_condition_met: bool`を追加。
  `clear_condition_met`はシナリオ/クリア条件システムがまだ存在しないため常に`false`から
  始まる、呼び出し側(将来のシナリオ層)が設定するためのプレースホルダーである。
- `_settle_month_end()`の末尾で`_evaluate_terminal_state()`を呼ぶ:
  - `economy.cash_yen < 0` → `_trigger_game_over("bankrupt")`。
  - 現金がちょうど0の場合は`MonthBoundaryBankruptcyPolicy.bankrupt_when_zero=None`と
    同じ立場を取り、**破産と判定しない**(未解決のまま継続)。
  - `current_year = (month_count / MONTHS_PER_YEAR) + 1`が`GAME_OVER_YEAR_LIMIT`を超え、
    かつ`clear_condition_met`が偽の場合 → `_trigger_game_over("time_limit_exceeded")`。
- `_trigger_game_over(reason)`が`is_game_over`を立て、`game_over_reason`を記録し、
  `game_over`イベントをログに残す。
- `is_game_over`が真になった後は、`step()`/`tick_idle_for_demand()`/
  `start_next_customer()`/`start_explicit_customer()`/`demand_admit_if_due()`/
  `apply_explicit_restock()`/`try_relocate_fixture()`/`try_rotate_fixture_clockwise()`
  という、状態を変更する全ての公開メソッドが早期リターンするようになる。ゲームオーバー後の
  画面遷移・リスタート導線は何も発明していない(凍結された状態がそのまま観測できるのみ)。

### 何を発明していないか

- クリア条件そのもの(町の人口目標、店舗数、等)は依然として未実装であり、
  `clear_condition_met`は常に`false`のプレースホルダーのままである。将来のシナリオ層が
  実際の判定結果をここに書き込むまで、時間切れゲームオーバーは事実上「100年経てば必ず
  発生する」経路として動作する。これは攻略本の確定情報(クリア条件未達成なら時間切れで
  ゲームオーバー)をそのまま反映した結果であり、クリア条件自体を推測で埋めたものではない。
- 現金ちょうど0のケースを「継続」と断定してもいない。これも証拠が存在しないため
  `MonthBoundaryBankruptcyPolicy`同様、判定不能な状態として扱っている
  (本実装では「ゲームオーバーにしない」という形でしか未解決状態を表現できないため、
  結果的にゲームは継続するが、これは「0円は安全」という確定情報ではなく、単に
  証拠がないため破産と断定しない、という消極的な選択である)。

### テスト方法についての注記

100年分(1200ヶ月 × 代表4日間 × 1440分)を実際にティックで進めるのはCI上非現実的なため、
`headless_smoke.gd`では`month_count`/`economy.cash_yen`を直接操作したうえで
`_evaluate_terminal_state()`を単体的に呼び出し、判定ロジックそのものを検証している。
これは本ファイルが既に採用している「テスト目的でのサブオブジェクト直接操作」パターン
(例: 不変性検証のための`basket`直接書き換え)の延長である。

## 影響

- `game/scripts/vertical_slice_simulation.gd`: `GAME_OVER_YEAR_LIMIT`/`MONTHS_PER_YEAR`
  定数、`is_game_over`/`game_over_reason`/`clear_condition_met`フィールド、
  `_evaluate_terminal_state`/`_trigger_game_over`メソッドを追加。既存の全公開ミューテーション
  メソッドに`is_game_over`ガードを追加。`snapshot()`に`is_game_over`/`game_over_reason`を
  追加。
- `game/scripts/headless_smoke.gd`: 破産・0円未解決・時間切れ・クリア条件達成による
  時間切れ回避、および凍結後の全メソッドが副作用を持たないことを検証するテストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 本機能の存在と
  確定情報としての根拠を検証する新規contractテストを追加。
- JSON設定への変更なし(`schema_version`は7のまま)。両ゲームオーバー条件は確定値であり
  調整可能にする理由がないため。
