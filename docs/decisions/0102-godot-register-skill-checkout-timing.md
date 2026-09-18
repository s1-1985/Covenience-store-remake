# 0102: `game/`(Godot)にレジ能力(register_skill)のチェック時間反映を実装(タスク#33)

## 背景

タスク#33は、ユーザー承認済みの優先順位リストの3番目の項目。これまで
`checkout_ticks`(既定値3)は、どのスタッフがレジを担当していても常に
固定のチェックアウト所要ティック数として使われており、タスク#32で
実在candidateへ差し替えたばかりの`register_skill`フィールドは
(意図通り)いかなるロジックにも消費されていなかった。

`docs/research/checkout-staff-dispatch-evidence-2026-09-05.md`第5節は
「レジ能力が最低の店員だと1人の接客に丸1日かかることもあるほど遅く、
高スキルの店員は極端に速くなる」という**CONFIRMED_COMMUNITY/QUALITATIVE**
な定性的証拠を記録しているが、同時に「具体的な秒数/ティック数の関数は
発明してはならない」と明記している。`reference_sim/conveni_sim/
checkout_service_timing.py`も、`CheckoutServiceDurationPolicy`という
差し替え可能なProtocol(抽象インターフェース)のみを持ち、具体的な数式は
一切実装していない(テストでは`FixedDurationPolicy`という固定値モックを
使う)ことを確認した。

このため、本タスクは「原作の数式を移植する」タスクではなく、この
プロジェクトが既に採用している手法(demand_policy.gdの客数発生式などと
同じ)に倣い、**明示的にREMAKE_BALANCED_DEFAULTタグを付けた、この
プロジェクト独自の仮置き数式**を実装する。

## 決定

### `CheckoutTiming`(新規)

`game/scripts/domain/checkout_timing.gd`を新設し、
`required_ticks(register_skill: int, reference_ticks: int) -> int`を実装。

- `reference_ticks`(=既存の`simulation.checkout_ticks`設定値)を
  「`REFERENCE_REGISTER_SKILL`のスタッフが担当した場合の所要ティック数」
  として再解釈し、実際に担当するスタッフの`register_skill`に応じて
  反比例的にスケーリングする(`ticks = round(reference_ticks *
  REFERENCE_REGISTER_SKILL / register_skill)`、下限`MIN_CHECKOUT_TICKS=1`)。
- `REFERENCE_REGISTER_SKILL := 13`は完全な当て推量ではなく、タスク#32で
  移植した35名のCONFIRMED_OFFICIAL candidateの`register_skill`の
  **中央値**(実測: min=8, max=20, mean≈13.9, median=13)を採用した。
  これにより、中央値ちょうどのスタッフが担当する場合は挙動が変わらない
  (`checkout_ticks=3`のまま)。
- `register_skill<=0`の場合はゼロ除算を避けるためのガードとして
  `reference_ticks * REFERENCE_REGISTER_SKILL`(最も遅いケース)を返す。

ファイル冒頭のコメントで、この反比例スケーリングの「形」自体がこの
プロジェクトの発明であり、原作から回収した数式ではないことを明記した。

### `StaffState`への`register_skill`フィールド追加

`game/scripts/domain/staff_state.gd`に`register_skill: int`フィールドを
追加し、`service_skill`等と同じパターン(`staff_config.get("register_skill",
0)`、非負アサート)で初期化するようにした。

### `VerticalSliceSimulation`への配線

`vertical_slice_simulation.gd`に`CheckoutTimingScript`をpreloadし、`_init()`
で`_checkout_timing`インスタンスを生成。`step()`の`"to_checkout"`フェーズで
`customer.checkout_ticks_remaining = _checkout_ticks`だった箇所を
`_checkout_timing.required_ticks(checkout_staff.register_skill,
_checkout_ticks)`に置き換えた。これにより、実際にそのフェーズを担当する
`checkout_staff`(`staff.checkout_staff()`が返す、タスク#32でmanda_machiko
(register_skill=20)にバインドされたstaff-1)のスキルが、そのままシミュレー
ション上のチェックアウト所要時間に反映されるようになった。

### `vertical_slice.json`の`checkout_ticks_evidence_note`

`simulation`セクションに新しい`checkout_ticks_evidence_note`を追加し、
`checkout_ticks`が「フラットな固定値」から「基準スキルでの所要ティック数」
へ再解釈されたこと、およびこのスケーリング自体が原作から回収した数式では
なくこのプロジェクト独自のREMAKE_BALANCED_DEFAULT仮置きであることを明記
した(既存の`restock_task_evidence_note`と同じパターン)。

## テスト

- `headless_smoke.gd`: `CheckoutTiming.required_ticks()`の直接呼び出しに
  よる単体テストを追加(基準スキルちょうどで不変、基準の2倍のスキルで
  半分になる、スキル1での極端な遅さ、スキル0でのゼロ除算ガード、
  非常に高いスキルでの`MIN_CHECKOUT_TICKS`下限)。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_register_skill_checkout_timing_is_a_tagged_remake_default`を追加。
  `REFERENCE_REGISTER_SKILL`が実際に35名candidateのregister_skill中央値と
  一致することをPython側で独立に再計算して検証し、`checkout_timing.gd`が
  REMAKE_BALANCED_DEFAULTタグと「発明した数式である」旨の記述を持つこと、
  `VerticalSliceSimulation`の実際のチェックアウト開始処理に配線されている
  ことを検証する。`test_godot_entry_scene_and_scripts_exist`に新規ファイルを
  追加。
- Godot 4.3公式バイナリで`headless_smoke.gd`を実行し、全テストPASSを確認
  (`Vertical-slice headless smoke passed in 500 steps.` -- 旧515ステップから
  減少しているのは、staff-1(register_skill=20)のチェックアウトが基準
  スキル13でのticks=3から2へ短縮された効果が実際に反映されているため)。
- `reference_sim/tests`フルスイート(651件、新規テスト含む)が全てPASS。
- Xvfbでの実レンダリングによりクラッシュ/表示崩れがないことを確認。

## 実装ファイル

- `game/scripts/domain/checkout_timing.gd`(新規): `CheckoutTiming`。
- `game/scripts/domain/staff_state.gd`: `register_skill`フィールドを追加。
- `game/scripts/vertical_slice_simulation.gd`: `CheckoutTimingScript`の
  preload、`_checkout_timing`フィールド、チェックアウト開始処理への配線。
- `game/data/vertical_slice.json`: `simulation.checkout_ticks_evidence_note`
  を追加。
- `game/scripts/headless_smoke.gd`: `CheckoutTiming`の単体テストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## タスク#33の完了

`register_skill`が実際にチェックアウト所要時間へ反映されるようになり、
タスク#32で移植した実在candidateデータが初めて挙動に影響するように
なった。数式自体は原作から回収したものではなく、この点を評価ノート・
コード内コメント・テストの全てで明示的にタグ付けした。
