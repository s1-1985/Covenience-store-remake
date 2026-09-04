# PS版 商品・什器カテゴリ直接検証 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 初代PS版で実際に配置できる商品・設備カテゴリを、続編の完全表から逆輸入せず復元する。
- 商品と什器/サービス設備を別データとして実装できる基礎を作る。

## 主要ソース

2017年にPlayStation版『ザ・コンビニ』を購入し、約3週間ゲームの流れを確認したうえでレイアウト比較を行った実機プレイ記録。

- https://minkara.carview.co.jp/userid/2518797/blog/40357970/
- https://minkara.carview.co.jp/userid/2518797/blog/m201709/

筆者は記事中でPS版を購入したこと、実際に大型店へ改装して検証したことを明記している。

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC / DIRECT-PLAY

---

## 1. 常温カテゴリ

実機記録に列挙されるカテゴリ:

1. 弁当
2. パン
3. レトルト
4. お菓子
5. インスタント
6. 日用品
7. 文具
8. 家電
9. 雑誌
10. 下着
11. 薬品
12. 調味料

### 注意

ここでの「弁当」は後述の冷蔵にも登場する。原作データ上、同じ商品カテゴリが複数の棚/温度帯設備から選択できる可能性があるため、`product_category == fixture_type` と一体化しない。

---

## 2. 冷蔵カテゴリ

1. ドリンク
2. 酒
3. 弁当
4. 薬品
5. 肉
6. 魚
7. 野菜

### 実装上の意味

商品カテゴリと陳列設備の対応は多対多にできる構造が安全。

```text
ProductCategory
FixtureType
FixtureProductCompatibility
```

を分ける。

---

## 3. 冷凍カテゴリ

1. アイス
2. 食品

表記は実機プレイ記事のまま保存する。

`食品` を勝手に「冷凍食品」へ正規化せず、原作画面/攻略本で正式表示を確認するまでは alias 候補として扱う。

---

## 4. 記事で「自販機」とまとめられている専用設備・サービス群

実機プレイ記事では次を一群として列挙している。

1. 冷たい
2. 温かい
3. 酒
4. タバコ
5. イベント
6. おでん
7. 肉まん
8. 保温飲料
9. ATM
10. コピー
11. レジ
12. 休憩
13. 噴水
14. 木
15. 駐車場
16. 椅子

### 重要

この見出しがゲーム内部の正式カテゴリ名として「自販機」なのか、記事筆者の便宜的なまとめなのかは未確認。

したがって実装で以下を全部 `VendingMachine` にしない。

最低でも概念上は:

```text
DedicatedMerchandiseFixture
- cold_drink
- hot_drink
- alcohol
- tobacco
- event_goods
- oden
- steamed_bun
- heated_drink_case

ServiceFixture
- ATM
- copy_machine

StoreOperationFixture
- register
- break_room

AmenityFixture
- fountain
- plant/tree
- bench/chair

ExteriorFixture
- parking
```

のように分けるのが安全。

上記英語名はRemake側の内部名称候補であり、原作正式英語名ではない。

---

## 5. 初代専用Wikiと照合できるカテゴリ

初代専用内装Wikiでは、以下の設備について独立したゲーム上の効果/寸法が確認される。

- 観葉植物: サービス+2, 1x1, 維持費120円/日
- ベンチ: サービス+3, 1x1, 維持費168円/日
- 噴水: サービス+25, 2x2, 維持費2400円/日
- 駐車場（白線）: 2台, 1x2, 維持費0円/日
- 2階建駐車場: 4台, 1x2, 維持費240円/日
- タワー駐車場: 20台, 2x3, 維持費4800円/日

Source:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

記事側の `木 / 椅子 / 駐車場` は、原作画面の正式名称を確認するまでは `観葉植物 / ベンチ / 駐車場系` との対応候補として扱う。

---

## 6. 『ザ・コンビニ2』との汚染防止

続編専用Wikiには非常に整った商品/設備完全表が存在するが、そこには初代にない続編要素が含まれる。

特に現行公式『2』説明でもゲーム商品等の追加が明記されるため、続編の一覧を初代の穴埋めに使用しない。

初代PS baselineへ採用できるのは、今回のように初代PS実機記録または初代PS/SS資料で裏の取れた項目のみ。

---

## 7. 現時点の実装用 provisional schema

```text
FixtureDefinition
- id
- family
- footprint
- orientation_count
- interaction_sides
- purchase_cost
- maintenance_cost_per_day
- capacity
- service_delta
- security_delta
- supported_product_categories[]
- license_requirement?
- indoor_or_outdoor

ProductCategoryDefinition
- id
- display_name_jp
- allowed_fixture_families[]
- license_requirement?
- customer_preferences: UNKNOWN
- base_margin/prices: UNKNOWN
```

### まだ埋めてはいけない値

- 商品個別価格
- 商品ごとの仕入値
- 棚容量
- 什器購入価格
- 全什器の正確なfootprint
- 什器ごとの維持費
- 各カテゴリの正式内部分類
- 商品の目的買い/ついで買い確率

これらは1997年PS/SS攻略本のデータリスト、説明書、実画面で継続復元する。
