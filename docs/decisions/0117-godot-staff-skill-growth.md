# 0117: スタッフのスキル成長(work-event growth)をGodotクライアントへ配線(タスク#48)

## 背景

`game/scripts/domain/staff_state.gd`自体のコメントが「攻略本の"仕事内容と
パラメータ変化の関係"図(book page 26)は確定しているが、work-event
counting/manager-education bonusを含む成長システム自体は未移植」と明記
しており、`docs/decisions/0116-*.md`(タスク#47)の「明示的に対象外とした
限界」にも「スタッフのスキル成長は依然として未移植」と記載されていた。
ユーザーに次タスク候補を提示したところ、このスキル成長配線が選ばれた。

調査の結果、`game/data/vertical_slice.json`の`staff_candidates`(35名の
CONFIRMED_OFFICIAL採用候補プール)には`*_skill_growth_ceiling`(攻略本の
「能力の分岐ポイント」)フィールドが既に5種類ポート済みであることが判明した
(いつポートされたか明確な記録はないが、少なくともタスク#47の時点で既に
JSONへ存在していた)。ただし`staff.members`(実働staff-1/staff-2)側には
複製されておらず、成長ロジック自体も一切存在しなかった。

`reference_sim/conveni_sim/staff_growth_resolution.py`
(`EvidenceBackedStaffGrowthResolver`)によれば、攻略本の複数スキル成長図
(レジ→レジ+接客、補充→補充+清掃+警備、清掃→清掃+警備)のうち、実際に
コミュニティ検証で増分が確定しているのは「補充作業→補充スキル+1」と
「清掃作業→清掃スキル+1」の2ペアのみ(CONFIRMED_COMMUNITY)。他の3ペア
(レジ→レジ、レジ→接客、補充→清掃、補充→警備)は存在は確定しているが
増分は未確定で、`reference_sim/conveni_sim/remake_staff_growth.py`
(`RemakeBalancedStaffGrowthResolver`)が同じ+1をREMAKE_BALANCED_DEFAULTの
推測値として補っている。

このクライアントには「清掃(clean)」という独立したスタッフタスク/メカニクス
自体が存在しない(タスク#41で休憩室什器を除外して以来、清掃は一度も
実装対象になっていない)ため、清掃タスクに紐づく成長(清掃→清掃+1
CONFIRMED_COMMUNITY、清掃→警備 REMAKE_BALANCED_DEFAULT)はそもそも
発火点が存在せず、今回は対象外とした。同様に、店長教育ボーナス
(`MANAGER_TEACHING_BONUS_CHANCE_PER_EDUCATION_POINT`)も、この
vertical sliceには「staff.membersの誰が店長か」という指定データが
一切存在しないため対象外とした。

## 決定

### `staff.members`への`*_skill_growth_ceiling`複製

タスク#32/#47が確立した「候補者データの値をそのまま`staff.members`へ
複製する」パターンを、5つの新フィールド(service/register/cleaning/
replenishment/security の各`_skill_growth_ceiling`)にも適用した。
staff-1(manda_machiko)=41/55/36/35/42、staff-2(sugawara_fumio)=
35/35/35/42/50を`staff.members`の各エントリへ直接転記した。

### `game/scripts/domain/staff_growth.gd`(新規)

`reference_sim/conveni_sim/staff_growth_resolution.py` +
`remake_staff_growth.py`を1つのクラスに統合してポート。
`apply_checkout_growth(staff_member)`(register_skill+service_skillを
それぞれ+1、ただし`_skill_growth_ceiling`でクランプ)と
`apply_replenish_growth(staff_member)`(replenishment_skill+
cleaning_skill+security_skillを同様に+1)の2メソッドを持つ。戻り値は
実際に成長したスキルのみを含む`Array[Dictionary]`(`{"skill", "before",
"after"}`)。どのペアがCONFIRMED_COMMUNITYでどれがREMAKE_BALANCED_DEFAULT
かをコード先頭コメントで明示している。

### `VerticalSliceSimulation`への配線

- チェックアウト完了時(`_advance_customer()`の"checkout"フェーズ完了
  ブロック): 顧客が実際に購入したかどうかに関わらず(攻略本の成長モデルは
  「作業内容」に基づくものであり、取引結果に基づくものではないため)
  `_staff_growth.apply_checkout_growth(checkout_staff)`を呼び出す。
- 自動補充タスク完了時(`_complete_restock()`): 実際に補充数量が発生したか
  どうかに関わらず、`_staff_growth.apply_replenish_growth(staff_member)`を
  呼び出す。
- どちらも成長が1件以上あった場合のみ`staff_skill_growth`イベントを記録
  する(`staff_id`/`task`/`skills`)。

**明示的に対象外**: `apply_explicit_restock()`(UIから即座に在庫を補充する
別経路、タスク#38で追加)は成長トリガーの対象外とした。これはスタッフの
作業時間を一切モデル化しない即時アクションであり、"仕事をした"という
確定事実に紐づけられないため。

### `StaffState.reset()`の拡張

スキルが初めて可変になったことを受け、`reset()`は5スキルを
コンストラクタ時点の値へ復元するようにした。これは
`VerticalSliceSimulation.load_state()`の既存コメント「Clears every
subsystem back to its config-derived starting point」という契約を、
これまで(スキルが不変だったため)結果的に真だったものを、今後も正しく
保つための変更。逆に言えば、スキル成長はセーブ/ロード形式自体には
まだ含まれておらず、セーブ→ロードを跨ぐと蓄積した成長は失われる
(`save_state()`のコメントに明記)。

## テスト

- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_staff_skill_growth_ceilings_are_wired_into_work_event_growth`を
  追加。`staff.members`の5つの`*_skill_growth_ceiling`が対応する
  `staff_candidates`のCONFIRMED_OFFICIAL値と一致すること、
  `staff_growth.gd`にREMAKE_BALANCED_DEFAULT/CONFIRMED_COMMUNITYの
  両タグが存在すること、`vertical_slice_simulation.gd`の2箇所
  (チェックアウト/補充)に実際に配線されていること、
  `apply_explicit_restock()`の関数本体には成長呼び出しが一切含まれない
  こと、`staff_candidates_evidence_note`/`staff.skill_evidence_note`から
  古い「未消費」記述が除去されていることを検証。フルスイート662件
  (新規テスト含む、xfail 1件)全てPASS。
- `headless_smoke.gd`:
  - `StaffGrowth`の直接単体テストを追加(CheckoutTiming/RestockTimingと
    同じ形): +1成長、ceilingでのクランプ、クランプ後は成長結果が空になる
    こと、`StaffState.reset()`がスキルを起点値へ戻すことを検証。
  - タスク#40の既存の自動補充シナリオ(`restock_simulation`)を流用し、
    その中で既に発生していた1回のチェックアウトと1回の自動補充完了の
    直後に、staff-1のregister_skill/service_skillとstaff-2の
    replenishment_skill/cleaning_skill/security_skillがそれぞれ+1されて
    いること、`staff_skill_growth`イベントが正確に2件(チェックアウト1件
    +補充1件)記録されていることを検証。
  - 月末レーティングシナリオ(`rating_simulation`)の`service_value`
    ハードコード値(17.0)は、チェックアウト成長でstaff-1のservice_skillが
    17→18へ変化するため壊れた。実際のスタッフ状態から動的に期待値を
    再計算するよう修正し、`customer_share_percent`の期待値も
    `CustomerShare`クラスを直接呼び出して再計算する形に変更した
    (ハードコードされた再計算コメントは、成長により入力値が変わる
    たびに陳腐化するため)。
  - Godot 4.3公式バイナリで764ステップ(タスク#47時点と同じ、既存
    シナリオへのアサーション追加のみで新規の独立ステップ実行シナリオは
    追加していないため)でPASS。

## 実装ファイル

- `game/scripts/domain/staff_growth.gd`(新規): 成長ロジック本体。
- `game/scripts/domain/staff_state.gd`: 5つの`*_skill_growth_ceiling`
  フィールドを追加、`reset()`がスキルを起点値へ復元するよう拡張。
- `game/scripts/vertical_slice_simulation.gd`: `_staff_growth`を追加、
  チェックアウト完了/自動補充完了の2箇所に配線、`save_state()`の
  コメントにスキル成長が未セーブである旨を追記。
- `game/data/vertical_slice.json`: `staff.members`の2エントリに
  `*_skill_growth_ceiling`を追加、`staff.skill_evidence_note`/
  `staff_candidates_evidence_note`を更新。
- `game/scripts/headless_smoke.gd`: `StaffGrowth`単体テストを追加、
  既存の自動補充シナリオへ成長アサーションを追加、月末レーティング
  シナリオの`service_value`/`customer_share_percent`期待値を動的化。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- 店長教育ボーナス(`MANAGER_TEACHING_BONUS_CHANCE_PER_EDUCATION_POINT`):
  このvertical sliceに「誰が店長か」という指定データが存在しないため。
- 清掃(clean)タスクに紐づく成長(清掃→清掃+1 CONFIRMED_COMMUNITY、
  清掃→警備 REMAKE_BALANCED_DEFAULT): このクライアントに清掃タスク/
  メカニクス自体が存在しないため。
- スキル成長のセーブ/ロード永続化: `SAVE_SCHEMA_VERSION`の拡張を伴う
  別スコープの変更として見送った。現状、セーブ→ロードを跨ぐと蓄積した
  成長は失われる(`save_state()`のコメントに明記済み)。
- `apply_explicit_restock()`(即時在庫補充UIアクション)経由の成長は
  対象外(上記「決定」参照)。
