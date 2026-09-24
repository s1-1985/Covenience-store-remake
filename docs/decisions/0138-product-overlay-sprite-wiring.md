# 0138: 商品オーバーレイの配線(タスク#68、アセット統合 第2弾)

## 背景

タスク#67(什器スプライト)のマージ後、ユーザーから次の配線対象として
「商品オーバーレイ(推奨)」の選択があった。`assets/raw/README.md`によれば
`conveni_products_remake_v3/`は`fixture_catalog`と同じブリーフ
(`docs/assets/chatgpt-fixtures-products-brief-2026-09-23.md`)に基づく
作り直し版(v3)で、25カテゴリ×high/medium/lowの75枚(すべて64×64px、
`<catalog_id>_<state>.png`)で構成される。`product_catalog`の26カタログID
のうち`copy_paper`のみ、パッケージ側のREADME
(`assets/raw/conveni_products_remake_v3/README_CLAUDE.md`)が
「copy_paper、cash、汎用vending_machineは独立商品・什器として追加していない」
と明記しており、対応スプライトが存在しない。

`game/`側を調査したところ、商品の在庫状態(`InventoryState`)は元々
`product_catalog`の`catalog_id`と一切紐付いていなかった——
`try_procure_product()`は`catalog_id`引数を使って`product_catalog`から
価格等を引くだけで、その`catalog_id`自体は`InventoryState`に一切保存されず
破棄されていた。カタログ経由で仕入れた商品ですら、どの商品カテゴリの
見た目を表示すべきか判定する手段が存在しなかった。

## 決定

### `InventoryState.catalog_id`の追加(タスク#38以前の2什器と同型の判断)

`InventoryState`に`catalog_id: String`フィールドを追加し、
`try_procure_product()`が既に持っている`catalog_id`引数をそのまま
`product_config`に渡すようにした(`vertical_slice_simulation.gd`)。
これは新しい推測ではなく、既に確定していたが破棄されていた値を
配線し直しただけである。

`vertical_slice.json`の`products`配列にあるタスク#38由来の
プロトタイプ商品2件(`prototype-bread`/`prototype-drink`)は
カタログシステム以前のデータで、価格も`product_catalog`の
確定値(bread: 300円/150円、cold_drink: 110円/55円)と一致しない
(prototype-bread: 120円/60円、prototype-drink: 160円/80円)。
このため`catalog_id`フィールド自体はデータに追加せず——追加すれば
「この2商品はまさにそのカタログ品目である」という主張になってしまう
——タスク#67のcheckout-1/shelf-1/shelf-2と同じ判断で、`store_view.gd`側の
表示専用フォールバック辞書(`FALLBACK_PRODUCT_CATALOG_ID_BY_PRODUCT_ID`、
`{"prototype-bread": "bread", "prototype-drink": "cold_drink"}`)で
対応した。

### 在庫段階(high/medium/low)の切り替え

パッケージのスプライト自体が「9個/5個/2個」等の個数を絵として
既に含んでいるため(`README_CLAUDE.md`「商品の重ね方」)、実装側で
個数を動的に描画する処理は不要で、3枚のうちどれを表示するかだけを
選べばよい。`stock_units / initial_stock_units`の比率がどこで
high→medium→low に切り替わるかは原資料のどこにも書かれていないため、
0.66/0.33を本プロジェクト独自のREMAKE_BALANCED_DEFAULT閾値として
`store_view.gd`に定義した(在庫0の場合はオーバーレイを描画せず、
棚が空に見える——これは閾値の発明ではなく、個数が減るほど表示個数が
減るという確認済み事実の単純な延長)。

### 什器footprintへのタイル単位での繰り返し

`README_CLAUDE.md`「2×1や3×1はタイルごとに繰り返す」の指示通り、
`_draw_product_overlay()`は什器の`footprint_tiles`の各1マスに同じ
スプライトを1枚ずつ描画する(什器全体に引き伸ばさない)。回転時に
向きを変える処理はタスク#67の什器スプライトと同様、今回も未対応
(ソースのmanifestに向き違いのバリアントが存在しないため)。

### タグ付け規律の遵守漏れの是正(タスク#67分も含む)

`CLAUDE.md`の証拠タグ付け規律は、REMAKE_BALANCED_DEFAULTの文字列が
(1)コードコメント、(2)`vertical_slice.json`の`evidence_note`、
(3)そのタグの文字列自体を検証するテストアサーション、の3箇所すべてに
存在することを要求している。タスク#67(什器スプライト)はコードコメントのみで
(2)(3)を欠いており、これは`CLAUDE.md`自身が「以前に是正された同種の
問題」として明記している抜け漏れパターン(タスク#38→#38の補正、PR #209)
と同種だったため、本タスクで併せて是正した:
`reference_sim/tests/test_game_vertical_slice_contract.py`に
`test_fixture_sprite_visual_fallback_is_a_tagged_remake_default`
(タスク#67分)と
`test_product_overlay_sprites_are_wired_and_tagged_remake_default`
(タスク#68分)を追加し、`vertical_slice.json`の`products`配列2件に
`evidence_note`フィールドを新設した。

## テスト

- `reference_sim`フルスイート733件パス/1件xfail(新規2件のコントラクト
  テストを含む)。
- `game/scripts/headless_smoke.gd`: ローカルにGodot実行環境がないためCIで
  検証。追加した検証内容:
  - `product_catalog`の全26カタログIDについて、`copy_paper`を除く25件×
    high/medium/lowの計75通りすべてで`StoreView._product_texture()`が
    実際に非nullのテクスチャを返すこと(`copy_paper`側は逆に常にnullで
    あることも検証——既知の欠落が黙って拡大/縮小しないことの保証)。
  - `prototype-bread`が`catalog_id`を持たないこと、その表示用フォール
    バックが`bread`に解決されること、満タン在庫時に`high`状態を表示する
    こと、`_product_on_fixture("shelf-1")`が`prototype-bread`を正しく
    解決すること。
  - 什器カタログ経由で仕入れた`product-purchase-1`(catalog_id=
    `tobacco`)が実際に`InventoryState.catalog_id`へ`tobacco`として
    伝播していること。

## 対象ファイル

- `game/assets/products/*.png`(75ファイル、25カテゴリ×high/medium/low)
- `game/scripts/domain/inventory_state.gd`
- `game/scripts/domain/inventory_catalog.gd`
- `game/scripts/vertical_slice_simulation.gd`
- `game/scripts/store_view.gd`
- `game/scripts/headless_smoke.gd`
- `game/data/vertical_slice.json`
- `reference_sim/tests/test_game_vertical_slice_contract.py`
- `PROJECT_MEMORY.md`

## 明示的に対象外

- 店員・客スプライト、町マップ・建物タイル、メニューUI系5パッケージの配線は
  今回対象外。それぞれ別タスクとして扱う。
- `copy_paper`カテゴリの見た目(対応スプライトが存在しない)は今回も
  未対応のまま——新規画像生成は本タスクのスコープ外。
- 什器の回転時にオーバーレイの向きを変える処理は未対応(タスク#67と同じ
  理由: ソースパッケージに向き違いのバリアントが存在しない)。
- `reference_sim`側への商品カテゴリ別スプライト表示相当のロジック移植は
  行っていない——`reference_sim`にはそもそも描画層が存在しない。
- これらのスプライト自体は`CLAUDE.md`の証拠規律上、原作の確認された
  見た目(CONFIRMED_OFFICIAL)ではなく、あくまで本プロジェクト独自の
  新規デザインである(タスク#67と同じ評価)。
