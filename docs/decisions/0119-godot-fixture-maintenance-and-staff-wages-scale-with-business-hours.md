# 0119: 什器維持費・スタッフ給与を営業時間に応じてスケールさせる(タスク#50)

## 背景

ユーザーから提供された4件のPDF(攻略本のスキャン、計2冊: 「ザ・コンビニ
新人店長実習マニュアル」と「クイックリファレンス」)を4並列エージェントで
全ページ独立に読み取り・書き起こしさせたところ(`docs/research/strategy-
guide-shopkeeper-manual-part{1,2}-2026-09-19.md`、`docs/research/quick-
reference-guide-part{1,2}-2026-09-19.md`)、「クイックリファレンス」の
時間(p.2)節に以下の明文記述が見つかった:

> 維持費: 設備を良好に保つための…電気代として1日に必要な費用。**営業時間に
> 応じて**、毎日売上げから差し引かれる。
>
> 人件費: 社員の給料として必要な経費。表示は日給だが、内部では**時給計算**が
> されている。計算方法は**時給×営業時間**。営業時間を伸ばすほど人件費が
> かさむので注意してほしい。

同じ書籍のp.6でも独立に「賃金は時給×営業時間で表示される…営業時間0時間の
臨時休業日は、日給表示も0円なのだ」と再確認されている(CONFIRMED_OFFICIAL、
2箇所で独立に確認)。

一方、既存実装(タスク#46/#47、決定書0115/0116)は
`_apply_daily_fixture_maintenance()`/`_apply_daily_staff_wages()`が
`maintenance_yen_per_day`/`salary_yen_per_day_24h`をそのまま日額として
全額控除しており、決定書0116は明示的に「実労働時間による按分は対象外
(勤務時間追跡の仕組みが存在しないため)」としていた。今回発見した書籍の
記述は、まさにこの「対象外」の根拠だった欠落公式そのものであり、
`reference_sim/conveni_sim/baseline_data.py`の`salary_yen_per_day_24h`
導出コメント自体も既に「hourly_wage_yen \* 24」という24時間基準の値である
ことを示唆していた(`_sg_staff_candidate`まわりのdocstring)。CLAUDE.mdの
優先順位ルール(確認済み証拠 > 類推 > 独自発明)に従い、独自発明として
据え置いていた「按分しない」判断を、新たに確認された公式へ置き換える。

## 決定

### `VerticalSliceSimulation._scale_yen_to_configured_business_hours()`(新規共通ヘルパー)

`maintenance_yen_per_day`/`salary_yen_per_day_24h`をいずれも「24時間営業
基準の日額」とみなし、`demand.opening_minutes_per_day`(このクライアント
唯一の「設定済み営業時間」を表す既存フィールド。`DemandPolicy`が来客率の
按分に既に使っている)に応じて按分する共通ヘルパーを追加した:

```gdscript
func _scale_yen_to_configured_business_hours(value_at_24h_basis: int) -> int:
    const MINUTES_PER_24H_DAY := 24 * 60
    return int(floor(
        float(value_at_24h_basis) * demand.opening_minutes_per_day / float(MINUTES_PER_24H_DAY)
    ))
```

按分の比例関係そのものはCONFIRMED_OFFICIAL(書籍に2箇所で明記)。ただし
端数(1円未満)の丸め方は書籍のどこにも明記されていないため、既存の
`CheckoutTiming`/`RestockTiming`が採用しているfloor丸めの慣習をそのまま
踏襲し、この丸め方自体はREMAKE_BALANCED_DEFAULTとしてタグ付けした。

### `_apply_daily_fixture_maintenance()`/`_apply_daily_staff_wages()`の更新

両関数とも、これまでの生の`maintenance_yen_per_day`/`salary_yen_per_day_24h`
の単純合計から、各項目ごとに上記ヘルパーでスケールしてから合計する形へ
変更した。日次経済へ流し込む先(`economy.record_explicit_expense`)や
イベント名(`fixture_maintenance_charged`/`staff_wages_charged`)、月末
決済(`_settle_month_end()`のx8倍)との統合方法は変更していない――
`demand.opening_minutes_per_day`は現状このクライアントでは起動時固定の
静的設定値(960分=16時間)であり、営業時間を動的に変更するUI/臨時休業
機構自体がまだ存在しないため、値そのものは日ごとに変わらない。

スタッフ給与については、決定書0116が挙げていた「実労働時間による按分には
勤務時間追跡の発明が必要」という理由は、今回の発見によって不要になった:
書籍の公式は「店舗の設定営業時間」に対する按分であり、「各スタッフが
個人として何時間働いたか」への按分ではない。したがってStaffStateに新たな
勤務時間追跡を追加する必要はなく、既存の`StaffState`のタスクベース状態
機械(idle/to_restock/restocking/checkout)はそのまま変更していない。

## テスト

- `game/scripts/headless_smoke.gd`: タスク#46/#47が追加した什器維持費・
  スタッフ給与テストシナリオ(月末決済テスト/広告発火テスト/専用の維持費
  テスト)の期待値計算を、`_scale_yen_to_configured_business_hours()`と
  全く同じ丸め方を再実装した`_expected_daily_yen_at_business_hours()`
  ヘルパー経由に変更した(実装の丸め方が将来変わってもテストが追従できる
  よう、値のハードコードではなく同一の公式を再実装する形にした)。Godot
  4.3公式バイナリで831ステップ(タスク#49時点と同じ、新規シナリオを
  追加していないため)でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 既存の
  `test_fixture_maintenance_is_charged_daily`/
  `test_staff_wages_are_charged_daily`を更新。変更前コード
  (`total_wages_yen += staff_member.salary_yen_per_day_24h`のような生の
  加算)を直接文字列アサートしていた箇所を、新しい
  `_scale_yen_to_configured_business_hours()`呼び出しの存在確認へ置き換え、
  `REMAKE_BALANCED_DEFAULT`タグの存在確認アサーションを新規追加した(タグ
  付け規律の(c)を満たす)。フルスイート663件(既存テスト更新のみ、新規
  テスト関数は追加していない)、xfail 1件、全てPASS。

## 実装ファイル

- `game/scripts/vertical_slice_simulation.gd`:
  `_scale_yen_to_configured_business_hours()`を新規追加し、
  `_apply_daily_fixture_maintenance()`/`_apply_daily_staff_wages()`から
  呼び出すよう変更。
- `game/data/vertical_slice.json`: `fixture_catalog`の
  potted_plant/bench/fountainの`evidence_note`(他の32エントリは
  「potted_plantのevidence_noteを参照」という委譲形式のため個別更新は
  不要)、および`staff.skill_evidence_note`のsalary部分を、今回の公式
  発見を反映するよう更新。
- `game/scripts/headless_smoke.gd`: `_expected_daily_yen_at_business_hours()`
  ヘルパーを新規追加し、3箇所の期待値計算をこれ経由に変更。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 上記2テストを
  更新。
- `docs/research/quick-reference-guide-part1-2026-09-19.md`: このタスクの
  根拠となった一次資料の書き起こし(本タスクより前のコミットで追加済み)。

## 明示的に対象外とした限界

- `demand.opening_minutes_per_day`自体を動的に変更できる営業時間選択UI・
  臨時休業機構は、このクライアントにまだ一切存在しない(既存の別課題)。
  そのため「営業時間0時間の臨時休業日は日給表示も0円」という書籍の記述は、
  公式としては既にこの実装で正しく再現される(`opening_minutes_per_day`
  が0なら按分結果も0)が、実際にその状態を作り出す手段が無いため、
  この変更単体では体感できない。
- スタッフ個人ごとの勤務時間・シフト追跡は今回も追加していない(上記の
  通り、書籍の公式が店舗の設定営業時間に対する按分であるため不要と判断)。
- 什器維持費の丸め方(端数の扱い)は依然としてこのプロジェクト自身の
  REMAKE_BALANCED_DEFAULT推測であり、書籍に明記された確定ルールではない。
