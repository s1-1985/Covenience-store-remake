# 0089: `game/`(Godot)にレジ以外の店員向けタスク自動割当(自動補充)を追加する

## 背景

決定書0088で自動来店を移植した後、タスク#22として「複数店員のタスク自動割当」に着手した。
`game/`(Godot vertical slice)は元々2人の店員を設定できるが、実際に動くのはレジ担当
(`checkout_staff_id`)1人だけで、もう1人(`staff-2`)は開店から閉店まで一度も動かない
「家具」状態だった。

`reference_sim/`には店員のタスク割当そのもの(レジ/補充/清掃の振り分けアルゴリズム)を
扱うモジュールが存在しない(`staff.py`はスキル成長、`staff_rest_recovery.py`/
`staff_rest_timing.py`は休憩、`staff_growth_resolution.py`は成長量解決のみ)。攻略本側の
証拠も「店員能力が上がると、多数の客がいてもレジを1人で回そうとして買えない客が出ることが
ある」(`ps-gameplay-economy-evidence-2026-09-05.md`セクション10)という、レジ割当AIが
不完全であることを示す間接的な観測のみで、閾値や優先順位のアルゴリズムは確定していない
(`strategy-guide-full-decode-2026-09-16.md`セクション41の「店員AIのレジ割当閾値」)。

このため、移植元となるPython実装が存在せず、今回はGodot側で新規にPROVISIONALなタスク割当
ルールを設計した。

## 決定

### 実装した内容

- `staff_state.gd`: 各店員に`route`/`restock_target_product_id`/`restock_ticks_remaining`を
  追加し、`begin_restock`/`finish_restock`/`move_along_route`(`CustomerState`と同型)を実装。
  デフォルト状態を`"waiting_checkout"`から`"idle"`に変更(レジ担当・非レジ担当共通)。
- `vertical_slice_simulation.gd`:
  - `_step_restock_tasks()`が毎tick、レジ担当以外の全店員について`to_restock`(移動中)→
    `restocking`(在庫補充中、`restock_ticks`だけ待機)の状態を進める。
  - `_assign_idle_restock_tasks()`が、在庫が閾値
    (`restock_trigger_stock_units_at_or_below`)以下になった商品を、まだ誰も担当していない
    ものから順に、最初に見つかったアイドル状態の非レジ店員へ割り当てる単純な貪欲マッチング。
    スキル・優先順位・複数商品の同時判断は発明していない。
  - `_complete_restock()`は在庫を各商品自身の`initial_stock_units`まで戻し、
    `quantity × restock_unit_cost_yen`を`economy.record_explicit_expense`で計上する。
    これは既存の手動`apply_explicit_restock`と同じ経費/イベントログの仕組みを再利用している。
  - `try_relocate_fixture`/`try_rotate_fixture_clockwise`に`_any_restock_task_active()`の
    チェックを追加し、補充タスク進行中のレイアウト編集をブロックする(既存の
    「来店中はブロック」ロジックと同様の考え方)。
- `data/vertical_slice.json`: `schema_version`を6→7に更新。各商品に
  `restock_unit_cost_yen`(PROVISIONAL、原価/売価比率の根拠はない)を追加し、
  `simulation`ブロックに`restock_ticks`/`restock_trigger_stock_units_at_or_below`/
  `restock_task_enabled`を追加した。

### `restock_task_enabled`をデフォルトで`false`にした理由

このvertical sliceの基本シナリオには、既存の`headless_smoke.gd`/Python側contractテストが
明示的に検証している「売り切れ後の棚は補充されないままになる」という挙動
(README: "a later empty-shelf visit exits without creating revenue")が存在する。これは
攻略本から検証すべき確定挙動ではなく、あくまで「補充式・数量・コストを発明しない」という
既存方針の帰結として保持されてきたテストシナリオである。

今回追加した自動補充をこのシナリオでデフォルト有効にすると、最初に売り切れた瞬間に
非レジ店員が自動的に補充してしまい、上記の「売り切れ後は補充されない」という既存の
確認済みテスト前提を静かに壊してしまう。そこで、基本シナリオでは
`restock_task_enabled: false`のままとし、`headless_smoke.gd`内に需要をゼロにした
専用のテスト用構成(`restock_config`、`restock_task_enabled: true`)を別途用意して
機能自体を検証した。これは決定書0088で「飽和した来店確率」の検証に専用の
`saturated_demand_config`を使ったのと同じパターンである。

## 影響

- `game/scripts/domain/staff_state.gd`: 新規フィールド・メソッド追加、デフォルト状態を
  `"idle"`に変更。
- `game/scripts/domain/inventory_state.gd`: `restock_unit_cost_yen`フィールド追加。
- `game/scripts/vertical_slice_simulation.gd`: `_step_restock_tasks`/
  `_assign_idle_restock_tasks`/`_complete_restock`/`_find_idle_restock_staff`/
  `_any_restock_task_active`/`_restock_staff_snapshot`を追加。`step()`/
  `tick_idle_for_demand()`の両方から`_step_restock_tasks()`を呼ぶ。`_require_config()`が
  新しい`simulation`キー3種を検証するよう変更。`schema_version`要求を7に更新。
- `game/data/vertical_slice.json`: 前述のとおり更新。
- `game/scenes/main.tscn`: HUDの店員状態ラベルの初期表示テキストを`"waiting_checkout"`から
  `"idle"`に変更(初回リフレッシュ前のプレースホルダーのみ、機能に影響なし)。
- `game/scripts/headless_smoke.gd`: 専用の`restock_config`シミュレーションで、
  (a) 非レジ店員が売り切れ商品へ自動的にディスパッチされること、(b) 対象商品のみが
  `initial_stock_units`まで補充されコストが正しく計上されること、(c) 補充タスク中は
  什器移動がブロックされること、を検証するテストを追加した。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: `schema_version`を7に更新し、
  `restock_unit_cost_yen`の非負性チェックと、本機能がデフォルト無効であることを含む
  新規contractテストを追加した。
- まだ実装していないもの: レジ側の動的な人員再配置(需要が高いときに非レジ店員が
  レジへ応援に入る、等)、清掃タスク、スキルベースの優先順位付け。これらは
  引き続きPROVISIONAL/未着手として残す。
