# 0086: `store_evaluation.py`/`town.py` として8公式を配線する(store_runtime.pyには配線しない)

## 背景

2026-09-16のセッション引き継ぎ資料は、`store_value.py`/`store_rating.py`/`store_events.py`
(攻略本の8公式)が実装・テスト済みにもかかわらずどこからも呼ばれておらず、`store_runtime.py`
に配線する」という決定書0079の前提が誤りだったと記録していた。`store_runtime.py`は
promotion.py/month_boundary.py/monthly_report.py等と同様、外部の呼び出し元が組み立てる
独立モジュールの一つに過ぎず、これらを内部でimportしていない(`PROJECT_MEMORY.md`セクション19)。

このため、「いつ・どの呼び出し元が・どういう順序で8公式を呼ぶか」は設計判断が必要な状態の
まま残っていた。本セッションでユーザーから「town/評価状態の新設まで含めて設計・実装する」
との明示的な指示を受け、以下の設計で解決した。

## 決定

`store_runtime.py`(`StoreRuntimeHarness`)や`month_boundary.py`には一切手を入れない。
代わりに、既存モジュールと全く同じ「独立した、外部から組み立てられるモジュール」という
アーキテクチャパターンに従い、2つの新規モジュールを追加した。

### `reference_sim/conveni_sim/store_evaluation.py`

`StoreEvaluationRuntime`データクラスが、既存の`StoreStaffRoster`(社員のservice/security/
cleaningスキル値)と`StoreGrid`(新規追加した`size_tier`属性)から、`store_value.py`の
3公式(`compute_service_value`/`compute_security_value`/`compute_cleaning_value`)と
`store_rating.py`の`evaluate_monthly_rating_change`を呼び出せるようブリッジする。

- `internal_rating_value`(0〜100の内部評価値)は`None`から始まる。攻略本は新規開店時の
  初期評価値を明記していないため、発明せず`set_internal_rating_value`で明示的に設定する
  までは月次評価を実行できない(呼ぶと`ValueError`)。
- サービス設備のボーナス値(`fixture_service_bonuses`)は、既存のruntime層が
  `baseline_data`に一切依存していない設計原則(`store_grid.py`の`place_fixture`も
  fixture_idのみ保持し`FixtureDefinition`は保持しない)を踏襲し、呼び出し側が
  `StoreGrid.placements`の`fixture_id`から`baseline_data.FIXTURES`を引いて解決した
  数値リストとして渡す。このモジュール自身は`baseline_data`をimportしない。
- 施設によるセキュリティ加点(`SecurityFacilityCoverage`)も同様に呼び出し側から渡す。
  マップ上の交番/消防署とストアの位置関係を計算する空間シミュレーションは
  `reference_sim`にまだ存在しないため、ここでは発明しない。

### `reference_sim/conveni_sim/town.py`

`TownState`データクラスが、`store_events.py`の`magazine_or_contest_event_is_eligible`/
`compute_contest_prize_yen`が必要とする`population`/`store_count_including_rivals`を
保持する入れ物を提供する。これは町マップ・人口成長式・施設配置のシミュレーションでは
なく、単なる状態保持である。値は依然として呼び出し側(テストや将来の町シミュレーション層)
が更新する責務を負う。

### 配線しなかったもの

- `store_events.shoplifting_is_possible`の`customer_manner_value`引数: `CUSTOMER_VISIT_SCHEDULE`
  の`behavior_stats_raw[2]`(マ=マナー)から取得できる値だが、`store_runtime.py`の
  顧客セッション(`CustomerLifecycleHarness.add_customer`)は特定の顧客アーキタイプに
  紐付いていない(需要生成そのものが未実装のため)。これを紐付けるには顧客生成アルゴリズム
  自体の設計が必要であり、本決定のスコープ外とする。
- `month_boundary.py`への`scenario_time_limit_exceeded`(ゲームオーバー、100年経過)の
  統合: シナリオの`clear_condition_met`を判定する仕組み自体が`reference_sim`にまだ
  存在しないため、既存の`MonthBoundaryTerminalGate`(倒産判定専用)を拡張せず見送った。

## 影響

`reference_sim/conveni_sim/store_grid.py`の`StoreGrid`に`size_tier: Optional[str] = None`
属性を追加し、`from_store_variant`が`StoreVariant.size_tier`から設定するようにした
(既存の`(width_tiles, height_tiles)`のみのコンストラクタ呼び出しには影響しない)。

テストは`reference_sim/tests/test_store_evaluation.py`と`test_town.py`に追加。
