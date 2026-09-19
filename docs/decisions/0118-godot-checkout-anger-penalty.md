# 0118: チェックアウト待ちによる顧客の怒り(-2ペナルティ)をGodotクライアントへ配線(タスク#49)

## 背景

`PROJECT_MEMORY.md`第6節(スタッフシステム)は「Low register skill can make
checkout extremely slow and cause customer anger」という確定事実
(CONFIRMED_COMMUNITY)を記録しており、`reference_sim/conveni_sim/
checkout_anger_penalty.py`は「怒りが発生するとレジ/補充/警備/清掃/接客の
5スキルが-2される」という確定済みの効果を実装済みだった。一方
`checkout_anger_timing.py`(発火タイミングの調整役)は「いつ発火するか」の
閾値をあえて未確定のまま呼び出し側に委ねており
(`CheckoutAngerTriggerPolicy`はコールバック形式)、`checkout_anger_
penalty.py`の`resolve()`も下限値(フロア)を呼び出し側に要求する設計だった。

タスク#48完了後、ユーザーに次の候補として本タスクを提示する際、当初は
「閾値が未確定だから見送り」と判断しかけたが、再検討の結果、これは
タスク#33の`checkout_timing.gd`(レジ待ち時間の逆比例式)と全く同じ構造の
問題であることに気づいた: 効果自体は確定しているが、数式の形はこの
プロジェクト自身のREMAKE_BALANCED_DEFAULTとして発明する、という
CLAUDE.mdの優先順位(3)に正当に該当するケース。ユーザーはこの再評価を
踏まえて本タスクを選択した。

## 決定

### `game/scripts/domain/checkout_anger.gd`(新規)

`checkout_anger_penalty.py` + `checkout_anger_timing.py`を1クラスに
統合してポート。

- `SKILL_DELTA := -2`(CONFIRMED_COMMUNITY、レジ/補充/警備/清掃/接客の
  5スキル対象、教育・スタミナは対象外)。
- `MINIMUM_SKILL_VALUE := 0`(下限値の発明が必要だったが、このコード
  ベースが既に全スキルフィールドに課している非負制約を再利用しただけで、
  この機能専用の新しい数字を発明してはいない)。
- `TRIGGER_MULTIPLIER := 2.0`(REMAKE_BALANCED_DEFAULT): 発火閾値を、
  無関係な新しい絶対時間ではなく、タスク#33で既に確定済みの
  `CheckoutTiming`の基準所要時間(`REFERENCE_REGISTER_SKILL`=13における
  所要ティック数、すなわち`simulation.checkout_ticks`設定値そのもの)に
  対する倍率として表現した。「基準スキル以上のスタッフでは絶対に
  発火しない」という設計になり、攻略本の「低レジスキルが原因」という
  因果関係とも一致する。
- `trigger_ticks(reference_ticks)`: 閾値ティック数を返す。
- `apply_penalty(staff_member)`: 5スキルへ-2を適用し(フロアでクランプ)、
  `{"skill_name": {"before", "after"}}`を返す。

### `VerticalSliceSimulation`への配線

`_advance_customer()`の"checkout"フェーズ処理で、毎ティックの
`checkout_ticks_remaining -= 1`の直後に、まだ発火していなければ
`elapsed_ticks = checkout_assigned_ticks - checkout_ticks_remaining`を
計算し、`_checkout_anger.trigger_ticks(_checkout_ticks)`を超えた時点で
一度だけ`_checkout_anger.apply_penalty(現在接客中のスタッフ)`を呼び出し、
`checkout_anger_triggered`イベントを記録する。`CustomerState`に
`checkout_assigned_ticks`(ディスパッチ時点の所要ティック総数)と
`checkout_anger_triggered`(発火済みフラグ、1顧客につき最大1回)を追加した。

既定のstaff-1(register_skill=20)・staff-2は基準スキル(13)を上回っている
ため、`CheckoutTiming.required_ticks()`が基準ティック数を超えることが
なく、この機構は既定構成では発火しない(スキル成長で更に上がる一方
なので、タスク#48との相互作用による退行リスクもない)。低スキルの
スタッフを採用した場合にのみ実際に発火する。

## テスト

- `headless_smoke.gd`:
  - `CheckoutAnger`の直接単体テストを追加(`StaffGrowth`と同じ形):
    `trigger_ticks()`の倍率適用、`apply_penalty()`の-2適用とフロア
    クランプ、`before`/`after`の報告値を検証。
  - 新規シナリオ(`anger_simulation`): checkout担当スタッフの
    `register_skill`を1へ意図的に下げ(かつ`register_skill_growth_
    ceiling`/`service_skill_growth_ceiling`を0にオーバーライドして
    タスク#48の成長機構がこのテストの期待値に干渉しないよう分離した
    上で)1回の来店を実行し、`checkout_anger_triggered`イベントが
    正確に1件、5スキル全てが期待通り-2(フロアでクランプ)されている
    ことを検証。
  - Godot 4.3公式バイナリで831ステップ(タスク#48時点の764から、新規
    シナリオの低スキル接客の長い所要ティック分だけ増加)でPASS。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_checkout_anger_penalty_is_wired_into_checkout_service`を追加。
  `checkout_anger_penalty.py`のSKILL_DELTA/対象スキルとGDScript側の
  定数が一致すること、`checkout_anger.gd`にCONFIRMED_COMMUNITY/
  REMAKE_BALANCED_DEFAULTの両タグが存在すること、実際の配線箇所
  (`_checkout_anger.trigger_ticks`/`apply_penalty`/イベント記録)が
  存在すること、`vertical_slice.json`の`checkout_anger_evidence_note`に
  両タグが存在することを検証。フルスイート663件(新規テスト含む、
  xfail 1件)全てPASS。

## 実装ファイル

- `game/scripts/domain/checkout_anger.gd`(新規): ペナルティ・発火閾値の
  ロジック本体。
- `game/scripts/domain/customer_state.gd`: `checkout_assigned_ticks`/
  `checkout_anger_triggered`フィールドを追加。
- `game/scripts/vertical_slice_simulation.gd`: `_checkout_anger`を追加、
  チェックアウトディスパッチ時の`checkout_assigned_ticks`記録と、毎
  ティックの発火判定・ペナルティ適用を配線。
- `game/data/vertical_slice.json`: `simulation.checkout_anger_evidence_
  note`を新規追加。
- `game/scripts/headless_smoke.gd`: `CheckoutAnger`単体テストと新規
  シナリオを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- スタミナ/休憩室に絡む「レジ担当スタッフが低スタミナで接客前に離脱する」
  という別の確定メカニクス(`checkout_pre_service_departure.py`)は、
  このクライアントに休憩室什器・スタミナ追跡が一切存在しないため今回も
  対象外(タスク#41からの既存の割り切りを継続)。
- ペナルティ発火後にスキルが自然回復する仕組みは、reference_sim自体にも
  存在しないため実装していない(スキル成長(タスク#48)による+1が唯一の
  回復経路)。
- 顧客側の「マナー値」等、`checkout_anger_penalty.py`が要求する対象客の
  識別情報は使っていない(`apply_penalty`は対象スタッフのみを引数に取る、
  reference_sim側の設計をそのまま踏襲)。
