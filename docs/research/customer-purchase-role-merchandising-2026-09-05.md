# 初代PS/SS 商品の目的買い・ついで買い・客層依存 追加調査 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 客が単にランダムな商品を買うのではなく、商品ごとに「目的買い」「追加購入（ついで買い）」で役割が異なる可能性を初代専用資料だけで整理する。
- 商品価格と客層の相互作用を実装データへ残す。
- 後続作の完全な顧客データは使わず、初代で観測された範囲のみを採用する。

## 主要ソース

初代専用内装Wiki:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

証拠レベル: CONFIRMED-COMMUNITY（記載された攻略観測）

---

## 1. 大型ワゴンには「注目度」があり、ついで買いへ関係する可能性

初代専用資料では:

- 2×2大型ワゴンは1マス幅のワゴンより「注目度」が少し高い。
- `注目度はおそらくついで買いの確率に影響` とされる。

ここで重要なのは、`注目度` という設備側パラメータの存在自体は強い一方、**ついで買い確率へどう作用するかはWiki自身が推測形**であること。

扱い:
- 大型ワゴンの注目度が高い: CONFIRMED-COMMUNITY
- 注目度 → 追加購入確率の式: HYPOTHESIS

### 実装要求

FixtureDefinitionへ `attention` を保持できる余地を残す。

```text
FixtureDefinition
- attention: nullable / unknown
```

ただし数値も計算式も未確定なので仮の値を置かない。

---

## 2. 商品には「目的商品になりにくい/ならない」候補がある

初代専用Wikiの観測:

- おでん
- 中華まん
- 温かい飲料
- 冷凍食品
- 調味料

について、`目的として来店する客はいない？` とされている。

証拠レベル: PROVISIONAL / FIRST-TITLE-COMMUNITY-HYPOTHESIS

### 重要

疑問符付きなので「絶対に目的商品にならない」と確定してはいけない。

ただし商品ごとに:

```text
ProductDemandRole
- can_be_primary_destination
- can_be_add_on
- primary_weight
- add_on_weight
```

のような役割差を表現できる構造が必要な可能性が高い。

全商品を同一確率で目的商品にする設計は避ける。

---

## 3. 逆に「ついで買いされない」候補もある

同じ初代専用Wikiでは:

- 弁当
- 宅急便申込書

について `ついでに買う客はいない？` と記録される。

証拠レベル: PROVISIONAL / FIRST-TITLE-COMMUNITY-HYPOTHESIS

### 意味

商品ごとに「目的買い」と「追加購入」の重みが非対称である可能性がある。

例として将来:

```text
bento:
  primary_destination_weight: HIGH?
  add_on_weight: ZERO_OR_LOW?

takkyubin_form:
  primary_destination_weight: UNKNOWN
  add_on_weight: ZERO_OR_LOW?
```

のようなデータを持てるようにする。

`?` は未確定を示し、実装値ではない。

---

## 4. イベント商品は主要購買層が低年齢層で、値上げ耐性が低いという観測

初代専用Wiki:

- イベント商品は単価が高い。
- 主な購買層が所持金の少ない低年齢層。
- 値上げすると売れにくい。
- `20%UPが限度か` という攻略観測。

証拠レベル:
- 低年齢層が主要購買層: CONFIRMED-COMMUNITY / QUALITATIVE
- 20%UPが限度: PROVISIONAL / PLAYER-OBSERVATION

### 実装上の意味

顧客に所持金/予算概念がある可能性を重視する。

```text
CustomerArchetype
- spending_power / budget_profile
- preferred_products[]

Product
- base_price
- price_multiplier
```

低年齢客が高価格商品を無条件に買えるモデルは原作体験から離れる可能性がある。

ただし正確な所持金分布は未復元。

---

## 5. 2人打ちレジの存在を初代専用店員資料で直接補強

初代専用店員Wikiでは、レジ能力が最低クラスの店員について:

- 客1人の会計に丸一日かかる場合がある。
- 他の店員がかなり育ち、`2人打ちのレジ` を導入してようやく雇用を検討できる。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC

### 重要

続編に大型/2人用レジがあることは以前から検索で出ていたが、今回の根拠は**初代専用ページ**なので、初代baselineにも複数店員対応レジを持たせてよい。

未確定:
- 正式な設備名
- footprint
- 価格
- 同時処理アルゴリズム
- 2人揃わない時の挙動

したがって今は:

```text
RegisterDefinition
- max_simultaneous_staff: at least one first-title variant supports 2
```

までを確定候補とする。

---

## 6. 店員能力が低いと「1人の会計に丸一日」という極端な差がある

初代専用店員Wikiでは、最低クラスのレジ能力だと客1人の会計を済ませるのに丸一日かかる例が記録される。

これは厳密な固定時間ではなく極端さを示す攻略表現の可能性があるが、レジ能力差がごく小さな速度補正ではないことを示す。

証拠レベル: CONFIRMED-COMMUNITY / QUALITATIVE

### baseline要求

```text
checkout_duration = strongly dependent on staff.register_skill
```

とする。

`register_skill=10なら何秒` のような式はまだ作らない。

---

## 7. 初代商品AIとして安全な暫定モデル

現時点の証拠を破壊しないデータ構造:

```text
CustomerArchetype
- origin/building affinities
- spending_power_profile
- preferred_primary_products[]
- preferred_add_on_products[]
- patience_profile

ProductDefinition
- category
- base_price: UNKNOWN
- primary_purchase_eligibility: UNKNOWN/YES/NO
- add_on_purchase_eligibility: UNKNOWN/YES/NO
- audience_affinities[]

FixtureDefinition
- attention: UNKNOWN
- interaction_sides[]
```

### まだハードコードしないこと

- おでん等が100% primary不可
- 弁当が100% add-on不可
- イベント商品の値上げ上限20%
- 大型ワゴン注目度の正確な差
- 注目度→ついで買いの数式

これらは攻略本データ表・実機反復テストで継続検証する。
