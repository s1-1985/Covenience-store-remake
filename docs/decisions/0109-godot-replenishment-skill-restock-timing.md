# 0109: `game/`(Godot)に補充能力(replenishment_skill)の補充所要時間反映を実装(タスク#40)

## 背景

PR #210(タスク#39、商品カタログ拡充)のマージ後、引き続き「新規発明より
配線待ちの確認済みロジックを優先する」方針で次候補を探したところ、
`vertical_slice.json`の`staff.skill_evidence_note`自体が「register_skill/
replenishment_skillはデータとして存在するが、いかなるGDScriptロジックにも
消費されていない(タスク#33がregister_skillをチェックアウト時間に配線する
予定)」と明記していたことを再確認した。タスク#33で`register_skill`は
既に`CheckoutTiming`へ配線済みだが、`replenishment_skill`は依然として
未消費のまま残っていた。`_step_restock_tasks()`の`_restock_ticks`は、
担当スタッフによらず常に固定値だった。

`docs/research/ss-early-store-operations-and-acquisition-2026-09-06.md`
第4節は「スキルの低いスタッフは補充作業にも追われて掃除が遅い」
(CONFIRMED_COMMUNITY/DIRECT-PLAY-SS、実プレイ観察)、
`docs/research/checkout-staff-dispatch-evidence-2026-09-05.md`第6節は
「agility(敏捷性)がreplenishmentの上限に関係する」(攻略本の店員ページ)
と、それぞれ定性的な証拠を記録しているが、具体的な秒数/ティック数の
関数はどちらにも記載がない。これはタスク#33がregister_skillについて
参照した証拠と全く同じ性質(定性的効果は確認済み、数式は未確認)であり、
本タスクはタスク#33が確立した「反比例スケーリングというこのプロジェクト
独自の仮置き数式」の形をそのまま再利用する。

## 決定

### `RestockTiming`(新規、`CheckoutTiming`と同型)

`game/scripts/domain/restock_timing.gd`を新設し、`required_ticks(
replenishment_skill: int, reference_ticks: int) -> int`を実装。
`CheckoutTiming`と全く同じ反比例スケーリングの形(`ticks = round(
reference_ticks * REFERENCE_REPLENISHMENT_SKILL / replenishment_skill)`、
下限`MIN_RESTOCK_TICKS=1`、スキル0はゼロ除算ガードとして最も遅いケースを
返す)を採用した。`REFERENCE_REPLENISHMENT_SKILL := 13`は、タスク#32で
移植した35名のCONFIRMED_OFFICIAL candidateの`replenishment_skill`の
中央値(実測: min=8, max=20, mean≈13.66, median=13、偶然`register_skill`の
中央値と同じ値)を採用した。これにより、中央値ちょうどのスタッフが担当
する場合は既存の`restock_ticks`設定値のまま挙動が変わらない。

### `StaffState`への`replenishment_skill`フィールド追加

`game/scripts/domain/staff_state.gd`に`replenishment_skill: int`フィールド
を追加し、`register_skill`等と同じパターン(`staff_config.get(
"replenishment_skill", 0)`、非負アサート)で初期化するようにした。

### `VerticalSliceSimulation`への配線

`RestockTimingScript`をpreloadし、`_init()`で`_restock_timing`インスタンス
を生成。`_step_restock_tasks()`の`"to_restock"`ケースで
`staff_member.restock_ticks_remaining = _restock_ticks`だった箇所を
`_restock_timing.required_ticks(staff_member.replenishment_skill,
_restock_ticks)`に置き換えた。これにより、実際に補充を担当するスタッフの
`replenishment_skill`(staff-2=sugawara_fumioの20、staff-1=manda_machikoの
17)が、そのままシミュレーション上の補充所要時間に反映されるようになった
(`_step_restock_tasks()`はチェックアウト担当スタッフを除外するループの
ため、実質staff-2側が主に補充を担当する既存の挙動は変わらない)。

自動補充タスク(`restock_task_enabled`)は既定で無効のままであり(タスク
#36の既存の据え置き、変更なし)、メインの`headless_smoke.gd`長時間シナリオ
はこのタスクの配線によって挙動が変わらない(734ステップのまま不変)。
専用の`restock_task_enabled=true`テストブロックでのみ、この配線が実際に
可観測になる。

### `vertical_slice.json`の`restock_ticks_evidence_note`/`skill_evidence_note`更新

`simulation`セクションに新しい`restock_ticks_evidence_note`を、
`checkout_ticks_evidence_note`(タスク#33)と全く同じパターンで追加した。
`staff.skill_evidence_note`も、「タスク#33がregister_skillを配線する予定」
という古い記述を「register_skillはCheckoutTiming、replenishment_skillは
RestockTimingでそれぞれ消費される」という現状に更新した。

## テスト

- `headless_smoke.gd`: `RestockTiming.required_ticks()`の直接呼び出しに
  よる単体テストを追加(`CheckoutTiming`の単体テストと全く同じ5ケース:
  基準スキルちょうどで不変、基準の2倍のスキルで半分になる、スキル1での
  極端な遅さ、スキル0でのゼロ除算ガード、非常に高いスキルでの
  `MIN_RESTOCK_TICKS`下限)。Godot 4.3公式バイナリで実行し、全テストPASS
  (`Vertical-slice headless smoke passed in 734 steps.` -- 自動補充が既定で
  無効なため、メインシナリオのステップ数はタスク#39時点と不変)。既存の
  専用restockテストブロック(`restock_task_enabled=true`、`restock_ticks=2`
  設定)は`while state != "idle"`ループで完了を待つ作りのため、実際の
  ティック数が2→1に変わっても(staff-2のreplenishment_skill=20による
  スケーリング)引き続きPASSすることを確認。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_replenishment_skill_restock_timing_is_a_tagged_remake_default`を
  追加(`test_register_skill_checkout_timing_is_a_tagged_remake_default`と
  ほぼ同型)。`REFERENCE_REPLENISHMENT_SKILL`が実際に35名candidateの
  replenishment_skill中央値と一致することをPython側で独立に再計算して
  検証し、`restock_timing.gd`がREMAKE_BALANCED_DEFAULTタグと「発明した
  数式である」旨の記述を持つこと、`VerticalSliceSimulation`の実際の補充
  開始処理に配線されていることを検証する。`test_godot_entry_scene_and_
  scripts_exist`に新規ファイルを追加。フルスイート656件(新規テスト含む、
  xfail 1件)全てPASS。

## 実装ファイル

- `game/scripts/domain/restock_timing.gd`(新規): `RestockTiming`。
- `game/scripts/domain/staff_state.gd`: `replenishment_skill`フィールドを
  追加。
- `game/scripts/vertical_slice_simulation.gd`: `RestockTimingScript`の
  preload、`_restock_timing`フィールド、補充開始処理への配線。
- `game/data/vertical_slice.json`: `simulation.restock_ticks_evidence_note`
  を追加、`staff.skill_evidence_note`を更新。
- `game/scripts/headless_smoke.gd`: `RestockTiming`の単体テストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## タスク#40の完了

`replenishment_skill`が実際に補充所要時間へ反映されるようになり、
タスク#32で移植した実在candidateデータのうち、最後まで未消費だった
`replenishment_skill`フィールドが初めて挙動に影響するようになった。
数式自体はタスク#33が確立した形をそのまま再利用したこのプロジェクト
独自のREMAKE_BALANCED_DEFAULTであり、この点を評価ノート・コード内
コメント・テストの全てで明示的にタグ付けした。
