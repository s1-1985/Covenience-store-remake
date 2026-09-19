# 0116: スタッフの`salary_yen_per_day_24h`を日次収支へ配線(タスク#47)

## 背景

タスク#46(什器維持費の日次配線)の調査中に、`staff_candidates`(35名の
採用候補プール、CONFIRMED_OFFICIAL)が持つ`salary_yen_per_day_24h`も
同様に一切消費されていないことが判明した。ただし実働中の
`staff.members`(staff-1/staff-2)エントリ自体には給与フィールドが
存在せず、`candidate_id`経由で候補データを逆引きしないと値を得られない
状態だった。タスク#46では意図的に対象外としたが、続けてこの給与配線に
着手した。

## 決定

### `staff.members`への`salary_yen_per_day_24h`複製

タスク#32が既に確立した「候補者データの値をそのまま`staff.members`へ
複製する」パターン(service_skill/security_skill/cleaning_skill/
register_skill/replenishment_skillの5フィールドが既にこの方式)を、
6つ目のフィールドとして`salary_yen_per_day_24h`にも適用した。
staff-1(manda_machiko)=7,680円、staff-2(sugawara_fumio)=7,920円を
`staff.members`の各エントリへ直接転記した。

### `VerticalSliceSimulation._apply_daily_staff_wages()`(新規)

タスク#46の`_apply_daily_fixture_maintenance()`と全く同じ形で、
`_handle_day_boundary()`から呼び出す新関数を追加。現在アクティブな
全スタッフ(`staff.all_staff()`)の`salary_yen_per_day_24h`を合計し、
1日1回`economy.record_explicit_expense("staff_wages", ...)`として
一括控除する。

`salary_yen_per_day_24h`という名前自体が示す通り、この値は「1日あたり」
の確定額として扱い、実労働時間に応じて按分するような計算は行っていない。
理由: このクライアントにはスタッフの勤務時間・シフトを追跡する仕組みが
一切存在しない(`StaffState`はidle/to_restock/restocking/checkoutという
タスクベースの状態機械であり、勤務時間の概念を持たない)。実労働時間で
按分するには、按分の仕組みと「実際何時間働いたとみなすか」という新しい
仮定を発明する必要があり、既に確定しているこの日額をそのまま使う方が
発明を最小限に抑えられる。

## テスト

- `headless_smoke.gd`: タスク#46で追加した什器維持費テストシナリオを
  流用し、同じ日境界を跨いだ時点でスタッフ給与も正確に控除されている
  こと、`staff_wages_charged`イベントが1件記録されることを検証する
  アサーションを追加。この変更により、以下の既存テストが「日境界を
  跨ぐと給与も控除される」という新しい事実に合わせて期待値を再計算する
  必要が生じたため修正した:
  - 月末決済テスト: 4日分の給与(スタッフ2名合計15,600円×4日=62,400円)
    を`expected_four_day_net_result_yen`に反映。さらに`expected_cash_
    after_month_end`の導出式自体を、たまたま成立していた旧来の式
    (`cash_before_month_end`を基準にする)から、`_settle_month_end()`の
    実装から直接導ける、より頑健な式(`_cash_at_month_start +
    month_result_yen`)に置き換えた。
  - 広告(プロモーション)発火テスト: `trigger_day`に到達するまでに
    日境界を跨ぐため、実際に跨いだ日数分の給与を期待値へ反映するよう
    動的化した。
  Godot 4.3公式バイナリで764ステップ(タスク#46時点と同じ、新規の
  独立シナリオを追加していないため)でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_staff_wages_are_charged_daily`を追加。`staff.members`の
  `salary_yen_per_day_24h`が対応する`staff_candidates`のCONFIRMED_
  OFFICIAL値と一致すること、実際の日境界処理に配線されていること、
  `staff_candidates_evidence_note`から古い「未消費」記述(salaryを
  含む)が除去されていることを検証。フルスイート661件(新規テスト含む、
  xfail 1件)全てPASS。

## 実装ファイル

- `game/scripts/domain/staff_state.gd`: `salary_yen_per_day_24h`
  フィールドを追加。
- `game/scripts/vertical_slice_simulation.gd`:
  `_apply_daily_staff_wages()`を新規追加し、`_handle_day_boundary()`
  から呼び出す。
- `game/data/vertical_slice.json`: `staff.members`の2エントリに
  `salary_yen_per_day_24h`を追加、`staff.skill_evidence_note`/
  `staff_candidates_evidence_note`を更新(後者は今回のタスクと無関係な
  register_skill/replenishment_skillに関する古い記述も、タスク#43是正の
  精神に沿って併せて是正した)。
- `game/scripts/headless_smoke.gd`: 既存テストの期待値を動的化・修正。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- 実労働時間による按分は上記の通り対象外(勤務時間追跡自体が未実装)。
- `staff_candidates`の35名分の給与を「候補者プールとして一括表示する」
  ような機能は今回も追加していない(スタッフ雇用・解雇UI自体が別タスク
  として残っている)。
- スタッフのスキル成長(`reference_sim/conveni_sim/staff.py`の
  work-event counting/manager-educationボーナス)は依然として未移植。
