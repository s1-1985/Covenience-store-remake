# 0103: `game/`(Godot)に駐車場什器3種を追加(タスク#34)

## 背景

タスク#34は、ユーザー承認済み優先順位リストの最後の項目。
`reference_sim/conveni_sim/baseline_data.py`の`FIXTURES`には既に
`parking_ground`/`parking_two_story`/`parking_tower`の3種が
CONFIRMED_COMMUNITY(初代専用Wiki「内装」)/CONFIRMED_OFFICIAL(攻略本の
購入価格のみ)として定義済みだったが、Godotの`fixture_catalog`には一切
移植されていなかった。

`docs/research/store-dimensions-and-fixture-costs-2026-09-05.md`第3節は
「駐車場は配置位置によらず車が駐車する」「白線のみの駐車場でも人は上を
歩けない」ことを記録しており、`reference_sim`の`FixtureDefinition`は
これを`blocks_pedestrian=True`という専用フィールドで表現している
(shelf/checkout/amenityにはこのフィールドが存在しない、
`blocks_pedestrian=None`)。

## 決定

### `store_layout.gd`は変更不要と判断

`store_layout.gd`の`_build_blocked_cells()`を確認したところ、**このクライア
ントは既にどの`kind`の什器であっても、その footprint 全セルを無条件で
`blocked`に登録している**(什器の種類によらない、既存の統一的な挙動)。
つまり「駐車場セルは歩行不可」という確定事実は、什器を1つでも配置すれば
自動的に既に成立している。`reference_sim`側が`blocks_pedestrian`という
専用フィールドを持つのは、この事実をこの什器について明示的に確認した
証拠管理上の理由であり、エンジンの挙動を変える新しいメカニクスを要求する
ものではないと判断した。このため、`store_layout.gd`自体には新しいコードを
追加していない(「タスクが要求するように見えるからといって、不要な抽象化
を追加しない」という本プロジェクトの既存方針に従った判断)。

### `fixture_catalog`への追加

`vertical_slice.json`の`fixture_catalog`に3エントリを追加した:

| catalog_id | kind | footprint_tiles | purchase_price_yen | maintenance_yen_per_day | parking_capacity |
|---|---|---|---|---|---|
| parking_ground | parking | [1,2] | 500 | 0 | 2 |
| parking_two_story | parking | [1,2] | 1000 | 240 | 4 |
| parking_tower | parking | [2,3] | 9000 | 4800 | 20 |

各エントリは`reference_sim`の`FIXTURES`から直接読み取った値で、
`blocks_pedestrian: true`と`placement: "outdoor"`も情報用フィールドとして
含めた(前者は上記の通りエンジン挙動的には既に成立済みの事実の記録、
後者は次の限界の記録)。`parking_capacity`はこのクライアントに車両
シミュレーションが存在しないため、いかなるロジックにも消費されない
(`maintenance_yen_per_day`と同じ、既存の「未消費だが記録する」パターン)。

### 明示的に対象外とした限界

攻略本/Wikiは駐車場の設置場所を`outdoor`(店外)と記録しているが、この
クライアントの店舗グリッドは「編集可能な店内床」のみを表現しており、
屋外/敷地の空間モデルはタスク#26で意図的に対象外とした町・ライバル店の
空間モデルと同じ理由でまだ存在しない。したがって、`try_purchase_fixture`
を通じて駐車場什器を購入すると、現状では他の什器と同様に店内グリッドへ
配置される(=`placement: "outdoor"`という確定事実とは整合しない)。この
制約を`fixture_catalog`の`evidence_note`に明記し、将来の屋外/敷地モデルの
必要性として残した。特別な購入拒否ロジックを追加することは、
「店内に置けないなら結局どこにも置けない」という、この段階ではまだ無い
屋外モデルの代替にしかならず、範囲を不必要に広げるため見送った。

### `store_view.gd`への描画分岐追加

`_draw_fixtures()`に`kind == "parking"`の分岐を追加し、灰色の塗りと
什器idラベルで表示するようにした(追加しなければ既定の"SHELF"ラベル・
青色になり、実際の種類と食い違って誤解を招くため)。

## テスト

- `headless_smoke.gd`: 新しい`parking_simulation`インスタンスで
  `parking_ground`の購入が成功し、指定originに配置され、配置後その
  footprintが歩行不可になることを検証するテストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_parking_fixtures_port_confirmed_reference_sim_data`を追加。
  3エントリ全てが`reference_sim`の`FIXTURES`とフィールド単位で一致する
  こと、`store_layout.gd`に種類別の特別扱いが追加されていないこと(既存の
  統一的な`for fixture in fixtures:`ループのみで足りることの確認)、
  `store_view.gd`に`parking`分岐があることを検証する。
- Godot 4.3公式バイナリで`headless_smoke.gd`を実行し、全テストPASSを確認
  (`Vertical-slice headless smoke passed in 530 steps.`)。
- `reference_sim/tests`フルスイート(652件、新規テスト含む)が全てPASS。

## 実装ファイル

- `game/data/vertical_slice.json`: `fixture_catalog`に3エントリを追加。
- `game/scripts/store_view.gd`: `parking`kindの描画分岐を追加。
- `game/scripts/headless_smoke.gd`: 駐車場購入の単体テストを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## タスク#34、およびユーザー承認済み優先順位リストの完了

駐車場什器3種をCONFIRMEDなデータとしてカタログに追加し、既存の統一的な
footprint-blocking挙動がそのまま`blocks_pedestrian`の確定事実を満たす
ことを確認した上でタスク#34を完了とする。これにより、「そうだね、仮置きの
まま放置された箇所がないかを洗い出してからだね」に始まり「提案の通りで
進めて」で承認された優先順位付きタスクリスト(店舗グリッド→スタッフ実名
データ→レジ能力→駐車場什器)が全て完了した。
