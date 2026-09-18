# 0093: `game/`(Godot)に許可・商品仕入れを実装する(タスク#25の第2段)

## 背景

タスク#25の続き。今回は「許可」と「商品仕入れ」を1つの機能としてまとめて実装した。
`reference_sim/conveni_sim/baseline_data.py`の`PERMITS`(タバコ/酒/薬の申請料)と
`FIXTURES`(たばこ自販機等、カテゴリ限定什器)、`_sg_category`(たばこカテゴリの
標準小売価格・利益額)を突き合わせると、両者は本来一体の仕組みであることが分かる:
許可を取得しないと、その許可が必要な商品を扱う什器も、その商品自体も扱えない。

## 決定

### 実装した内容

- `game/scripts/domain/inventory_catalog.gd`に`add_product(product_config: Dictionary)
  -> bool`を追加。指定した`fixture_id`が既に別の商品に使われていないこと、
  `id`が重複していないことを確認したうえで、実行時に新しい商品SKUを追加する。
  `reset()`は既存の`_product_configs`(初期構成)のみから再構築するため、
  実行時に追加した商品は`try_purchase_fixture`で追加した什器と同様、リセットで
  消える(既存の「什器移動・回転もリセットで元に戻る」という仕様と一貫)。
- `vertical_slice_simulation.gd`に3つの公開メソッドを追加:
  - `try_purchase_permit(permit_id) -> bool`: 許可カタログの申請料を支払い、
    `_permits_held`に記録する。同じ許可の重複購入は拒否する。
  - `has_permit(permit_id) -> bool`
  - `try_procure_product(catalog_id, instance_id, fixture_id) -> bool`: 商品カタログ
    から新しい商品SKUを、指定した(空いている)什器に紐付けて仕入れる。カタログ
    エントリに`required_permit_id`があれば、その許可を持っていない限り拒否する。
  - `try_purchase_fixture()`にも同様の許可チェックを追加(既存メソッドの拡張)。
- `data/vertical_slice.json`(`schema_version`を8→9に更新):
  - `permits`: タバコ(¥7,000,000)・酒(¥3,000,000)・薬(¥10,000,000)の3許可。
    いずれも`reference_sim`の`PERMITS`からCONFIRMED_OFFICIALのまま移植。
  - `fixture_catalog`に2エントリ追加: `small_ambient_shelf`(許可不要、¥60、
    `FIXTURES['small_ambient_shelf']`)、`small_tobacco_vending`(タバコ許可必須、
    ¥600、`FIXTURES['small_tobacco_vending']`)。
  - `product_catalog`: `tobacco`商品(売価¥250・仕入原価¥175、
    `_sg_category('tobacco', ...)`の`standard_retail_price_yen`/
    `profit_per_unit_yen`から算出、いずれもCONFIRMED_OFFICIAL。
    `initial_stock_units: 10`のみPROVISIONAL)。

### 何を発明していないか、あるいは意図的に単純化したもの

- **距離制限(`exclusion_distance_tiles`)は実装していない**。攻略本は
  タバコ7マス/酒11マス/薬15マスという他店との最低距離を確定しているが、
  これは町・ライバル店の空間配置というタスク#26の領域に属する概念であり、
  空間シミュレーションが存在しない現状では検証しようがない。許可購入・什器購入・
  商品仕入れのいずれも、この距離制限を一切考慮しない。
- **`small_tobacco_vending`購入自体にタバコ許可を要求する判断は、本実装独自の
  ゲーティングである**。攻略本は「許可がないとその商品を売れない」ことは
  確定しているが、「許可がないとその什器を購入できない」とまでは明記していない。
  ただし`compatible_product_categories=("tobacco",)`という、この什器が
  タバコ専用であるという確定データから見て、許可なしに購入できても使い道が
  ないため、購入自体をブロックする方が一貫性があると判断した。
- **什器とカテゴリの互換性チェックは実装していない**。`try_procure_product`は
  指定された`fixture_id`が存在し空いていればどの什器にも仕入れられ、
  `compatible_product_categories`(例: 冷蔵ケースには冷蔵品しか置けない、等)は
  一切検証していない。
- 商品カタログは現時点で`tobacco`1件のみ。酒・薬も同じパターンで追加できるが、
  対応する商品カテゴリの確定小売価格・利益額をまだ個別に転記していないため、
  今回は許可システムの動作を証明する最小限の1件に留めた。

## 影響

- `game/scripts/domain/inventory_catalog.gd`: `add_product()`を追加。
- `game/scripts/vertical_slice_simulation.gd`: `_permit_catalog`/`_product_catalog`/
  `_permits_held`フィールド、`try_purchase_permit`/`has_permit`/
  `try_procure_product`メソッドを追加。`try_purchase_fixture`に許可チェックを追加。
  `_require_config()`が`permits`/`product_catalog`キーとその必須フィールドを
  検証するよう変更。`schema_version`要求を9に更新。
- `game/data/vertical_slice.json`: 前述のとおり更新。
- `game/scripts/headless_smoke.gd`: 許可なしでの什器購入/商品仕入れ拒否、
  許可購入の成功・重複拒否・コスト計上、許可取得後の什器購入・商品仕入れの成功、
  仕入れコストの計算、既に商品がある什器への二重仕入れ拒否を検証するテストを
  追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 本機能の存在と
  `reference_sim`由来の確定価格であることを検証する新規contractテストを追加。
- タスク#25の残り: 広告宣伝システムのみが未実装。
