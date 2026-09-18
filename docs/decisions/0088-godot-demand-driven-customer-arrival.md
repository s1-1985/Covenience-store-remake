# 0088: `game/`(Godot)にREMAKE_BALANCED_DEFAULTの来店ポリシーを移植する

## 背景

ユーザーから「画像・音声を除いてゲームとして動くために何が残っているか」という質問があり、
`reference_sim/`(Python)には`REMAKE_BALANCED_DEFAULT`の各種ロジック(来店率・購入確率・
社員成長・ライバルAI・地価変動等、決定書0087)が実装済みである一方、実際にプレイヤーが
触る唯一のクライアントである`game/`(Godot 4 vertical slice)には一切配線されておらず、
客の来店すら手動ボタン(`start_next_customer`)に依存していることを回答した。

ユーザーから「それらのGodotへの移植を粛々と進めてくれ」との指示を受け、最も基礎的かつ
他の全ての仕組み(複数店員・日次ループ・経営破綻判定等)の前提となる「客の自動来店」から
着手した。

## 決定

`reference_sim/conveni_sim/remake_demand_policy.py`の`RemakeBalancedDemandPolicy`が持つ
来店率の考え方(人口 × 店舗シェア% × 人口あたり日次来店率、営業時間で按分、悪天候で減衰)を
`game/scripts/domain/demand_policy.gd`としてGodot(GDScript)に移植した。

### 実装した内容

- `DemandPolicy`(`demand_policy.gd`): `expected_arrivals_per_minute()`と
  `customer_arrives_this_minute()`を持つ。Python版と同じ式構造だが、係数の組み合わせ自体が
  推測(REMAKE_BALANCED_DEFAULT)であることをファイル冒頭のhouse ruleコメントで明記した。
- `VerticalSliceSimulation`(`vertical_slice_simulation.gd`)に`demand`(`DemandPolicy`
  インスタンス)を追加。`demand_admit_if_due()`は店舗が空(`customers.can_admit()`)のときのみ
  確率判定を行い、成功すれば次の客を自動入店させる。`tick_idle_for_demand()`は時計を1step分
  進めたうえで`demand_admit_if_due()`を呼ぶ、客不在時のアイドルtick用ラッパー。
- `main.gd`の`_process()`を変更し、客が"done"状態のときに何もせず停止していた挙動を廃止。
  代わりに`tick_idle_for_demand()`を毎tick呼び、時計を進めながら来店判定を行うようにした。
  手動の「Admit next customer」ボタンは、来店を待たずに強制的に次の客を入れる上書き手段として
  残す。
- `data/vertical_slice.json`に`demand`セクション(`nearby_population`/
  `customer_share_percent`/`daily_visit_rate_per_population`/`opening_minutes_per_day`/
  `bad_weather_visit_multiplier`/`is_bad_weather`/`rng_seed`)を追加し、
  `schema_version`を5→6に上げた。`nearby_population`/`customer_share_percent`は、
  町・商圏の空間シミュレーションがPython側/Godot側のどちらにもまだ存在しないため、
  直接の設定値として与えている(将来の町シミュレーション層から供給されるまでの暫定値)。

### 意図的に変更しなかったもの

- **同時に活動できる客は1人のまま**: `customer_roster.gd`の`can_admit()`(既存の
  single-active-customer制約)は変更していない。この移植は「次の客がいつ来るか」を
  自動化するだけであり、複数客の同時来店・衝突・行列といった、まだ復元されていない
  原作ルールを発明するものではない。複数客対応は別タスク(タスク#22以降)に残す。
  `demand_policy.gd`自体は(Python版と同様)1tickにつき最大1人しか生成しない設計であり、
  この制約とは独立に、将来の複数客対応時にも再利用できる。
- **来店率の時間帯依存**: `expected_arrivals_per_minute()`は時刻に依存しないフラットな率
  であり、`CUSTOMER_VISIT_SCHEDULE`が示す時間帯別の来店傾向は考慮していない。これは
  Python版の`RemakeBalancedDemandPolicy`と同じ簡略化であり、本移植で新たに追加した簡略化
  ではない。
- **町・商圏シミュレーションの実装**: `nearby_population`/`customer_share_percent`を
  設定値として直接与えるに留め、町マップ・ライバル店・商圏重複からこれらを算出する
  空間シミュレーションは実装していない(タスク#26)。

## 影響

- `game/scripts/domain/demand_policy.gd`(新規)。
- `game/scripts/vertical_slice_simulation.gd`: `demand`/`_demand_rng`フィールド追加、
  `demand_admit_if_due()`/`tick_idle_for_demand()`追加、`_require_config()`が
  `demand`キーとその必須フィールドを検証するよう変更、`snapshot()`に
  `expected_arrivals_per_minute`を追加。
- `game/scripts/main.gd`: `_process()`が客不在時に停止せず、自動来店判定を継続するように変更。
- `game/data/vertical_slice.json`: `schema_version`を6に更新し`demand`セクションを追加。
- `game/scripts/headless_smoke.gd`: `DemandPolicy`の単体的な確率境界(飽和/ゼロ/悪天候)の
  検証と、`VerticalSliceSimulation.demand_admit_if_due()`/`tick_idle_for_demand()`が
  客の在店中はブロックされ、空席時には確定的に入店させることを検証するテストを追加した。
- `game/README.md`/`PROJECT_MEMORY.md`セクション19を本変更に合わせて更新した。
