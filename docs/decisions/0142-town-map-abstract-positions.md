# 0142: 町マップ配線を「自店・ライバル店の抽象位置のみ表示」に縮小(タスク#72)

## 背景

タスク#67〜#71(什器・商品・店員・客スプライト、メニューUIアイコン)を
配線し終えた後、ユーザーから次の方向として「町マップ・建物タイルの
配線」の選択があった。`assets/raw/conveni_map_assets_v2/`を調査した
結果、以下の重大なギャップが判明した:

1. パッケージの52種のスプライトは全て「町の施設」(幼稚園・学校・公園・
   飲食店・住宅・会社・交番・消防署・駅など)であり、**自店舗・敵店舗を
   表す建物は一切含まれていない**(`README_JA.md`自身が「原作画像の抽出
   や模写ではなく...新規生成した絵」「視点は未達事項がある」と明記する
   本プロジェクト独自の新規デザイン、REMAKE_BALANCED_DEFAULT評価)。
2. 現在のゲームデータには、これら52種の施設をどこに配置するかという
   座標データが一切存在しない。`TownState`(`game/scripts/domain/
   town_state.gd`)は人口・店舗数の2つのカウンタのみを保持し、
   `_player_store_position`/`_rival_stores`(タスク#59、`vertical_slice_
   simulation.gd`)は許可距離判定(`TownSpatial.can_acquire_permit_at()`)
   の計算専用に追加された抽象的な座標にすぎず、実際の町マップ上の配置を
   表すものではない(`vertical_slice.json`の`town_spatial_evidence_note`
   が明記: 「町マップ上の配置ではなく、距離計算のためだけの参照点」)。

52種の施設をこのVertical Sliceに意味のある形で配置するには、配置座標
データを本プロジェクト独自に発明する必要がある。これは`PROJECT_MEMORY.md`
第17節が明示的な研究課題(「町発展の一般式」)として扱っている領域に
踏み込むことになり、`CLAUDE.md`の証拠規律(未確認の町シミュレーションを
推測しない)に抵触するリスクが高いと判断した。この判断をユーザーに
提示したところ、「自店・ライバル店の抽象位置のみ表示」(52種の施設
スプライトは一切使わず、既存の`_player_store_position`/`_rival_stores`
だけを可視化する最小限のビュー)を選択する回答があった。

## 決定

### 新規`TownView`は52種の施設スプライトを一切使わない

`game/scripts/town_view.gd`は、`vertical_slice_simulation.gd`が既に
追跡している2つのフィールド(`_player_store_position`/`_rival_stores`)
だけを、単色の四角形マーカーとして抽象座標グリッド上に描画する。
`conveni_map_assets_v2/`のアセットファイルは一切コピー・参照していない
——「データモデルに実際に存在するものだけを誠実に見せる」ビューであり、
見栄えのための偽の町を作らない。

`_rival_stores`はデフォルトで空配列(`vertical_slice.json`自身の
`town_spatial_evidence_note`)のため、既定シナリオではプレイヤー自店を
表す1つのマーカーのみが表示される——これは実装の不備ではなく、現在の
データモデルの実態をそのまま反映した結果である。

### 既存StoreViewの上に重ねるトグル方式(新規シーン・新規ナビゲーションは追加しない)

`main.tscn`に`StoreView`の兄弟として`TownView`(既定で非表示)を追加し、
既存の状態パネルに「Show town map」トグルボタンを1つ追加した
(`main.gd`の`_on_show_town_map_pressed()`が`store_view.visible`/
`town_view.visible`を反転させる)。新しいシーンファイルやシーン切り替え
インフラ(`GameLaunchState`のような)は導入していない——既存の1画面構成
に収まる最小限の変更。

トグルで`StoreView`が非表示になっている間もタップ入力自体は
`_unhandled_input()`に届き続けるため、`store_view.gd`の
`_unhandled_input()`冒頭に`if not visible: return`を追加した
(タスク#72で見つけた実際のバグ——非表示中に什器移動が誤発火しうる)。

### 境界ボックス計算の設計

`_bounding_box()`は、プレイヤー店舗+全ライバル店舗の座標を過不足なく
含む最小のタイル整列矩形を、各辺1タイルの余白付きで計算する
(`_town_points()`と分離した純粋関数——タスク#69/#70で確立した
「`_draw()`本体からロジックを分離してテスト可能にする」方針を踏襲)。
座標が非常に離れている場合にグリッドが巨大になる可能性は既知の制約として
未対応のまま(既定シナリオでは`_rival_stores`が空なので問題にならない)。

## テスト

- `reference_sim`フルスイート737件パス/1件xfail(新規コントラクトテスト
  1件)。`town_view.gd`が52種施設スプライト(`.png`・`ResourceLoader`)を
  一切参照しないこと、既存の証拠規律コメントが実際にコード内に存在する
  ことをファイル内容レベルで検証する。
- `game/scripts/headless_smoke.gd`: ローカルにGodot実行環境がないためCIで
  検証。追加した検証内容:
  - トグルボタンの押下でTownView/StoreViewの表示・非表示とボタン文言が
    正しく切り替わること(既存の`main.tscn`シーン経由、エンドツー
    エンド)。
  - 既定シナリオ(プレイヤーが原点、ライバル店ゼロ)で`_town_points()`が
    ちょうど1件のマーカーを返すこと。
  - `_bounding_box()`を、複数ライバルを持つ合成データ(ダックタイピングの
    フェイクシミュレーション`_FakeTownSimulation`、実データを一切汚さない)
    に対して直接演習し、期待通りの境界ボックスを計算すること。

## 対象ファイル

- `game/scripts/town_view.gd`(新規)
- `game/scripts/main.gd`
- `game/scripts/store_view.gd`(非表示中の入力ガードのみ)
- `game/scenes/main.tscn`
- `game/scripts/headless_smoke.gd`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- `conveni_map_assets_v2/`の52種施設スプライトの配線そのもの——配置データが
  存在しないため今回は一切使用しない。将来、確認済みまたは分析的類推が
  可能な配置データが見つかれば、改めて着手する。
- 町の人口成長・施設誘致・ライバル店AIなど、`TownState`/`_rival_stores`
  自体の新規メカニクスは今回の対象外(表示層のみ)。
- ライバル店舗の座標が極端に離れている場合のグリッド肥大化への対策は
  未実装(既定シナリオでは発生しない既知の制約)。
- 新規シーンファイル・シーン切り替えインフラは導入していない——既存の
  `main.tscn`内でのトグル表示のみ。
