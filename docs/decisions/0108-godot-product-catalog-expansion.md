# 0108: `game/`(Godot)の商品カタログを27カテゴリ中25カテゴリへ拡充(タスク#39)

## 背景

PR #209(タスク#38是正)のマージ後、ユーザーから「初代ザ・コンビニの再現を
忘れるな」という指摘を踏まえ、次の作業として「新規発明よりも、既に確認済み
のロジック・データの配線を優先する」候補を調査した。

`reference_sim/conveni_sim/baseline_data.py`の`PRODUCT_CATEGORY_PRICING`には
攻略本のDATA LIST商品表(book page 85、
`docs/research/strategy-guide-full-decode-2026-09-16.md`第3節)から
transcribeされたCONFIRMED_OFFICIALな商品カテゴリが27種類存在するが、
`vertical_slice.json`の`product_catalog`にはタスク#32で追加された「たばこ」
1種類しか移植されていなかった。`try_procure_product`/`apply_explicit_restock`
(タスク#38で既にUIに接続済み)や`main.gd`の`product_catalog_option`は、
どちらも既に`product_catalog`配列を汎用的に走査する実装になっており、
カタログへのデータ追加以外にコード変更を必要としない。したがって本タスクは
新しいメカニクスの発明を一切伴わない、純粋なデータ移植である。

## 決定

### 27カテゴリ中25カテゴリを`product_catalog`へ追加

`PRODUCT_CATEGORY_PRICING`の各エントリについて、`standard_retail_price_yen`
を`sale_price_yen`に、`standard_retail_price_yen - profit_per_unit_yen`を
`restock_unit_cost_yen`に、それぞれそのまま転記した(既存のたばこエントリと
同じ導出式)。`cold_drink`/`hot_drink`/`alcohol`/`bento`/`bread`/
`instant_food`/`snacks`/`books`/`ice_cream`/`stationery`/`retort_food`/
`electronics`/`seasoning`/`vegetables`/`frozen_food`/`fish`/`oden`/
`daily_goods`/`copy_paper`/`parcel_delivery_form`/`medicine`/`underwear`/
`event_goods`/`chinese_steamed_bun`/`meat`の25種を新規追加した。

`alcohol`/`medicine`は`vertical_slice.json`の`permits`に既存のエントリが
あるため、`required_permit_id`をそれぞれ`"alcohol"`/`"medicine"`とした
(`try_procure_product`は既にこのフィールドを許可証チェックに使用している、
タスク#32で確立済みの挙動)。他のカテゴリには許可証エントリが存在しない
ため、`required_permit_id`を付けず、無許可証で購入可能とした(攻略本が
言及していない許可証要件を新規発明しないため)。

`initial_stock_units`は既存のたばこエントリの前例(=10)に合わせ、
全カテゴリで10とした。これは攻略本が主張する実際の発注ロット数ではない
ため、各エントリの`evidence_note`に`REMAKE_BALANCED_DEFAULT`と明示した
(PR #209で是正した規律に従い、決定書だけでなくコード側=JSON
`evidence_note`本文にタグを含めている)。`seasonal_demand`/
`max_maintenance_yen_per_day`/`max_capacity`/`demand_example_count`/
`compatible_fixtures_text`は`reference_sim`側に確認済みデータとして存在
するが、`fixture_catalog`の`maintenance_yen_per_day`と同様、このクライアント
のどのロジックにも消費されない未消費フィールドとして残した(新しい
消費先=新メカニクスを今回は追加しない)。

### `cash`(現金)カテゴリは対象外

`PRODUCT_CATEGORY_PRICING`の27番目のエントリ`cash`は、攻略本上
`profit_per_unit_yen=0`/`cost_rate_pct=100`のゼロマージン特殊枠で、対応する
什器は`キャッシュディスペンサー`(現金自動支払機、ATM類似の設備)である。
これは棚に商品を並べて売る通常の商品カテゴリとは異なる、現金引き出し
サービスという別種のメカニクスであり、対応する什器・機能がこのクライアント
に存在しない。したがって商品カタログへの移植対象から明示的に除外した
(什器attention差別化を保留したのと同じ理由: 存在しないメカニクスを
新規発明してまで埋めるべき項目ではないと判断)。

### `main.gd`/`store_view.gd`は変更なし

`_populate_product_catalog_option()`(`main.gd`)は`config["product_catalog"]`
を無条件に走査してOptionButtonの選択肢を構築しており、`try_procure_product`
も`catalog_id`に対して完全に汎用的な実装のため、カタログへのエントリ追加
だけでUIから25種類すべてが選択・購入可能になる。什器の`kind`による
仕入れ先制限(`compatible_fixtures_text`)は現状のエンジンに存在せず、本
タスクでも追加していない(どの棚にどの商品でも置ける、という既存の緩い
挙動を維持)。

## テスト

- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規
  `test_product_category_catalog_expansion_ports_confirmed_reference_sim_pricing`
  を追加。25エントリ全てが`PRODUCT_CATEGORY_PRICING`の該当カテゴリと
  `sale_price_yen`/`restock_unit_cost_yen`単位で一致すること、`cash`が
  含まれないこと、`CONFIRMED_OFFICIAL`/`REMAKE_BALANCED_DEFAULT`両タグが
  各`evidence_note`に含まれること、`alcohol`/`medicine`以外に
  `required_permit_id`が付与されていないことを検証する。フルスイート
  655件(xfail 1件)全てPASS(既存の`test_remake_purchase_policy.py`の
  1件は本変更と無関係なシード無しRNGによる既知のflakeで、単体実行/再実行
  ではPASSすることを確認済み)。
- `headless_smoke.gd`: Godot 4.3公式バイナリで実行し、既存の734ステップが
  変化なくPASSすることを確認(既存テストは`_product_catalog_ids.find(
  "tobacco")`で動的に検索しているため、カタログ拡充による影響を受けない)。

## 実装ファイル

- `game/data/vertical_slice.json`: `product_catalog`に25エントリを追加。
- `reference_sim/tests/test_game_vertical_slice_contract.py`: 新規テストを
  追加。

## 明示的に対象外とした限界

- `cash`カテゴリ(現金/ATM類似メカニクス)は上記の通り対象外。
- `compatible_fixtures_text`(什器種別ごとの仕入れ可否)は確認済みデータの
  まま未消費。任意の棚にどの商品でも仕入れられる現状の緩い挙動は変更して
  いない。
- `seasonal_demand`(季節需要)も確認済みデータのまま未消費で、価格や
  需要への影響は依然としてシミュレートされない。
