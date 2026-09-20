# 0125: 店員の雇用(hiring)アクションの実装(タスク#56)

## 背景

`staff_candidates`(タスク#32、CONFIRMED_OFFICIAL)は35名分の実在候補データ
を保持しているが、これまで`staff.members`の2枠(staff-1/staff-2)は
`vertical_slice.json`が起動時に静的に束縛する2名(万田町子/菅原文夫)に
固定されたままで、この35名プールへプレイヤーから実際に触れる手段が
一切存在しなかった。`PROJECT_MEMORY.md`第21.3節はこれを未配線の
CONFIRMED_OFFICIALな仕組みとして記録していた。

クイックリファレンス book p.6を直接再読し、以下の記述を確認した:

> 各店舗に店長が必ず必要。店員は2人まで雇用できる。スーパー社員は
> 3人まで店員として数える。

これはCONFIRMED_OFFICIALであり、(a)雇用プールの存在そのもの、(b)通常
ケースでの店員上限が2人であること、を裏付ける。一方で、(c)店長(店主)
という別枠の存在、および(d)「スーパー社員」(推定: 高齢化後に到達する
全能力値100の特別な店員で、雇用枠を3人分消費する)という別メカニクスに
ついては、具体的な発生条件や数値式がこのページにもどこにも見当たらない。

## 決定

### `VerticalSliceSimulation.try_hire_candidate(staff_id, candidate_id)`

既存の`staff.members`ロースター(固定2枠)のうち、指定した枠が現在雇用
している候補を、`staff_candidates`プールの別候補で置き換える。既存の
他のロースター変更アクション(`try_eject_customer`など)と同じ
`customers.all_settled()`ガードを使用し、追加で以下を拒否する:

- 未知の`staff_id`/`candidate_id`
- 既に「他方の枠」で雇用されている候補(同一人物が2枠を同時に占有する
  ことはできない)

`StaffState.hire()`が識別情報(candidate_id/display_name)・五能力値・
成長上限・給与のすべてを新候補の値で再初期化する(`_start_*`基準値も
含む)。旧占有者が蓄積していたタスク#48のスキル成長は破棄される――現実
の入れ替わり人事で前任者の熟練度が引き継がれないのと同じ扱いとした。

`staff_roster`(`staff_id`/`candidate_id`/`display_name`)を
`snapshot()`/`save_state()`/`load_state()`に追加し、
`SAVE_SCHEMA_VERSION`を3→4に更新した。`load_state()`はガード付きの
`_apply_hire()`ではなく`StaffState.hire()`を直接呼ぶ専用の再適用ループを
使う――`staff.reset()`直後に1件ずつ`_apply_hire()`のクロス枠衝突判定を
適用すると、リセット直後でまだ上書きされていない相手側枠の値と一時的に
衝突して正当な2枠同時スワップの再読込が誤って拒否され得るため。保存
データはそれが記録された時点で既にその判定を通過済みなので、他の全
フィールドと同じ規約(`_require_save_data()`)で信頼して良いと判断した。

### REMAKE_BALANCED_DEFAULTな設計選択(書籍に明記のない部分)

- **ロースターは固定2枠のスワップのみ**: 「店長」用の3枠目は追加して
  いない。「雇用」とは既存2枠のどちらかの占有者を交代させることのみを
  意味し、枠を増やすことはできない。
- **スーパー社員メカニクスは未実装**: 加齢に伴う特別な店員(推定:
  全能力値100、雇用枠を3人分消費)は、発生条件・出現確率・具体的な
  能力値のいずれもどの情報源にも記載がなく、実装しようがない。
- 上記2点はいずれも「情報源が存在しない」ケースであり、CLAUDE.mdの
  優先順位(1)(2)のいずれも使えないため、意図的に「実装しない」という
  選択自体が対象外化の決定である(架空の数値を発明してまで実装する
  ことはしない)。

## テスト

- `game/scripts/headless_smoke.gd`:
  - `try_hire_candidate()`を直接呼ぶ新規シナリオを追加。正常な雇用の
    受理、他枠で雇用中の候補の拒否、未知のcandidate_id/staff_idの拒否、
    拒否時にロースターが変化しないこと、雇用がスキル値を実際に
    再基準化すること(register_skill: 20→14)、`staff_hired`イベントが
    ちょうど1件記録されること、退去した候補が別枠で再雇用可能になる
    ことを検証。
  - 既存の`economy_ui_scene`ブロックへ、UI経由(`StaffSlotOption`/
    `HireCandidateOption`/`HireCandidateButton`)での雇用シナリオを追加
    (タスク#38が確立したUI到達性の慣習に従う)。雇用後、雇用済み候補が
    「他方の枠」の選択肢から除外されることも検証。
  - 既存の save/load 往復テストへ、雇用が保存/復元されることの検証を
    追加(staff-2をtakenaka_sayuriへ雇用 → 保存 → 読込後も維持される
    こと、雇用していないstaff-1は設定由来のデフォルトのままであること)。
  - 構造チェックリストへ`StaffSlotOption`/`HireCandidateOption`/
    `HireCandidateButton`のノードパスを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_staff_hiring_action_is_wired_and_confirmed_official`を追加。
  evidence_noteのタグ、バックエンド関数の存在・配線、UI配線文字列を
  検証。タスク#53のテストが持っていた`SAVE_SCHEMA_VERSION := 3`という
  古いハードコード済みアサーションは、今回のバージョン更新(3→4)で
  無効化されるため、バージョン番号非依存の説明コメントへ置き換えた
  (この番号自体は新規テストが検証する)。
  Godot 4.3公式バイナリで1046ステップでPASS。pytestはフルスイート
  668件(新規テスト関数1件追加)、xfail 1件、全てPASS。

## 実装ファイル

- `game/scripts/domain/staff_state.gd`: `candidate_id`/`display_name`
  フィールド、`hire()`メソッドを新規追加。
- `game/scripts/vertical_slice_simulation.gd`: `_staff_candidate_catalog`、
  `try_hire_candidate()`、`_apply_hire()`、`_staff_roster_snapshot()`を
  新規追加。`snapshot()`/`save_state()`/`load_state()`/
  `_require_save_data()`/`_require_config()`を更新。
  `SAVE_SCHEMA_VERSION`を3→4に更新。
- `game/data/vertical_slice.json`: `simulation.staff_hiring_evidence_note`
  を新規追加。
- `game/scenes/main.tscn`: `StaffSlotOption`/`HireCandidateOption`/
  `HireCandidateButton`ノードを新規追加。
- `game/scripts/main.gd`: 上記ノードの束縛、
  `_populate_staff_slot_option()`/`_refresh_hire_candidate_option()`/
  `_on_staff_slot_selected()`/`_on_hire_candidate_pressed()`を新規追加。
- `game/scripts/headless_smoke.gd`: 新規シナリオ・構造チェックを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  テストを追加、既存の古いアサーション1件を修正。

## 明示的に対象外とした限界

- 「店長」という第3の枠/役割は実装していない――このクライアントの
  ロースターは引き続き固定2枠のままである。
- 「スーパー社員」メカニクス(推定: 加齢により出現する全能力値100の
  特別な店員、雇用枠を3人分消費)は実装していない――発生条件・確率・
  具体的な能力値のいずれも情報源に存在しないため。
- 候補の「解雇」を独立したアクションとして提供してはいない――
  `try_hire_candidate()`による「別候補への置き換え」のみが唯一の
  ロースター変更手段であり、枠を空にする(誰も雇用しない状態にする)
  ことはできない。書籍側にも「枠を空にできる」という記述は見当たら
  ない。
- 候補ごとの雇用コスト(採用時の一時金など)は実装していない――
  情報源に採用時費用の記載がなく、既存の`salary_yen_per_day_24h`
  (日次給与、タスク#47で既に配線済み)以外の追加コストを発明しな
  かった。
