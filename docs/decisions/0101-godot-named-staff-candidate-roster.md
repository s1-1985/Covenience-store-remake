# 0101: `game/`(Godot)にスタッフ実名候補データ(35名)を移植(タスク#32)

## 背景

タスク#32は、ユーザー承認済みの優先順位リストの2番目の項目。`vertical_slice.json`
の`staff.members`(staff-1/staff-2)は、これまで両者とも同一の
`service_skill=20, security_skill=15, cleaning_skill=15`という、いかなる
実在の候補者にも対応しない、単なる平坦な仮置き数値だった。

一方`reference_sim/conveni_sim/baseline_data.py`には、既に
`STAFF_CANDIDATES`という**CONFIRMED_OFFICIAL**な35名分のフルロースターが
存在した。これは攻略本「ザ・コンビニ完全攻略ガイド」相当資料の店員データ
個別カード(書籍127-133ページ)から直接転記されたもので、
`docs/research/strategy-guide-full-decode-2026-09-16.md`「店員データ」節に
出典が記録されている。氏名表記についても、`_sg_staff_candidate()`の
docstringにより、このデータは2026-09-16の一次スキャン読み取りに基づく
確定版であり、`docs/research/ps-small-store-grid-and-source-audit-2026-09-05.md`
第7節が記録していた表記衝突(福本考仁 vs 福本孝仁 等)は、後続のこの
一次資料により解決済みであることを確認した。

## 決定

### `staff_candidates`カタログの新設

`vertical_slice.json`に新しい`staff_candidates`配列(35エントリ)を追加し、
`reference_sim`の`STAFF_CANDIDATES`をPythonスクリプトで直接読み取って
機械的に生成した(手動転記による誤りを避けるため)。各エントリは
`candidate_id`/`display_name`/`age_years`/`salary_yen_per_day_24h`
(`hourly_wage_yen * 24`として導出済み)/`stamina`/`academic_background`/
`agility`/`sociability`/`education`/`service_skill`/`register_skill`/
`cleaning_skill`/`replenishment_skill`/`security_skill`(1名のみnull)/
5種の`*_skill_growth_ceiling`を持つ。`staff_candidates_evidence_note`で
出典とCONFIRMED_OFFICIALタグ、およびこのカタログ自体は「採用UIから
実際に選べる」機能を伴わない参照データに過ぎないことを明記した。

### アクティブな2名を実在候補にバインド

`staff.members`のstaff-1(レジ担当)を`manda_machiko`(万田町子、
register_skill=20で全candidate中最高)、staff-2(補充担当)を
`sugawara_fumio`(菅原文夫、replenishment_skill=20で全candidate中最高)に
差し替えた。両エントリの`service_skill`/`security_skill`/`cleaning_skill`
/`register_skill`/`replenishment_skill`を、この実在candidateの値へ
置き換えた(`candidate_id`/`display_name`も追加し、どのcandidateに
対応するかを追跡可能にした)。`register_skill`/`replenishment_skill`は
このタスクの時点ではまだいかなるGDScriptロジックにも消費されない
(前者はタスク#33の対象)。

`staff.skill_evidence_note`を更新し、これらの値がもはや
REMAKE_BALANCED_DEFAULTな仮置きではなく、実在candidateからの
CONFIRMED_OFFICIALな初期値であること、ただし成長システム自体
(`reference_sim/conveni_sim/staff.py`)は依然未移植であることを明記した。

### `staff_state.gd`のコメント更新

`StaffState._init()`のコメントを、「クラス自体は成長システムを実装して
いない(値は静的)」という事実と、「vertical_sliceの実データは今や実在の
CONFIRMED_OFFICIAL candidateに由来する」という事実を分離して記述するよう
書き直した。このクラス自体は渡された値が実在candidate由来か仮置きかを
判別できない汎用コンポーネントであるため、フィールド欠落時のフォール
バック(`.get(..., 0)`)は引き続きREMAKE_BALANCED_DEFAULT的挙動のままで
あることも明記した。

### テストの更新

- `headless_smoke.gd`: `compute_service_value`/`compute_security_value`/
  `compute_cleaning_value`の単体テスト(`store_value.gd`を直接呼ぶ既存の
  固定入力によるテスト)はそのまま(スタッフconfigとは独立)。一方
  月次評価テスト(`rating_event_details`)は、フレッシュな
  `VerticalSliceSimulation`が実際の`vertical_slice.json`の`staff.members`
  を使うため、旧placeholder値(20/15/15と20/15/15)に基づく期待値
  (service=20.0, security=45.0, cleaning=45.0)を、新しい実在candidate値
  (staff-1: service=17,security=18,cleaning=17 / staff-2:
  service=17,security=20,cleaning=17)に基づく期待値
  (service=17.0, security=57.0, cleaning=51.0)へ更新した。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_named_staff_candidate_roster_ports_all_35_confirmed_official_entries`
  を追加。`reference_sim`の`STAFF_CANDIDATES`と`staff_candidates`が
  フィールド単位で完全に一致すること(35件、id一意性、security_skillが
  null許容な1件を除き全て一致)、`staff.members`の2名が実在candidateの
  値と一致していること、`staff_state.gd`にこのタスクへの言及があることを
  検証する。

## 検証

- Godot 4.3公式バイナリで`headless_smoke.gd`を実行し、全テストPASSを確認
  (`Vertical-slice headless smoke passed in 515 steps.`)。
- `reference_sim/tests`フルスイート(650件、新規テスト含む)が全てPASS。
- Xvfbでの実レンダリングによりクラッシュ/表示崩れがないことを確認。

## 実装ファイル

- `game/data/vertical_slice.json`: `staff_candidates`/
  `staff_candidates_evidence_note`を新設、`staff.members`の2エントリを
  実在candidateへ差し替え、`staff.skill_evidence_note`を更新。
- `game/scripts/domain/staff_state.gd`: コンストラクタのコメントを更新。
- `game/scripts/headless_smoke.gd`: 月次評価テストの期待値を新しい
  candidate値に合わせて更新。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## タスク#32の完了

35名の実名候補データをCONFIRMED_OFFICIALな参照カタログとして移植し、
アクティブな2名のスタッフを実在candidateへバインドすることで、これまで
両者とも同一の仮置き数値だった問題を解消した。採用UI自体(候補から選んで
実際に雇用する機能)は本タスクの範囲外として明示的に対象外とした。
