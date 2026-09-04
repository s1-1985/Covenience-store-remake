# 初代PS/SS 在庫・補充・仕入れ境界調査 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 商品補充がどの単位で行われ、いつ費用が発生するかを初代専用証拠から整理する。
- 後続作や現代的な在庫管理を勝手に初代baselineへ追加しない。
- 棚在庫 / バックヤード在庫 / 発注 / 補充タスクを分離し、未確認部分をUNKNOWNのまま残す。

主要ソース:
- https://wikiwiki.jp/theconveni1/FAQ
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- https://minkara.carview.co.jp/userid/2518797/blog/40357970/
- https://minkara.carview.co.jp/userid/2518797/blog/40369273/

---

## 1. 補充は店員の自律作業

初代専用店員Wikiでは、店員の実務能力として `補充` が存在し:

- 高いほど補充速度が速い。
- 補充作業をするたび能力が1上昇。
- 敏捷性が補充能力の上限に対応。

と明記される。

証拠レベル: CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC

### baseline要求

```text
StaffTask
- REGISTER
- RESTOCK
- CLEAN
- REST
- ...
```

の一つとして `RESTOCK` を持つ。

補充をプレイヤーが毎回手動指示しなければ商品が戻らない構造にはしない。

---

## 2. PS版実機比較では「陳列物の補充はすべて店員任せ」で1年間営業可能

PS版を実際に使ったレイアウト比較記事では:

- 同一セーブ
- 同一年月
- 同じ店員
- 1年間比較
- `陳列物の補充はすべて店員任せ`

という条件を明記している。

Source:
- https://minkara.carview.co.jp/userid/2518797/blog/40357970/

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC / DIRECT-PLAY

### 意味

原作の通常プレイでは、棚の減少を店員AIが自動検知して補充タスクへ移る仕組みがある。

正確な補充開始閾値は未確定。

---

## 3. 閉店中でも補充は継続する

初代専用FAQ:

- 臨時休業/営業時間外でも店員は掃除や補充を行う。
- 営業時間外は人件費を含む多くの維持費が停止する。

Source:
- https://wikiwiki.jp/theconveni1/FAQ

証拠レベル: CONFIRMED-COMMUNITY

### baseline状態

```text
STORE_CLOSED
- customer_spawn = false
- many operating costs paused
- staff simulation = active
- RESTOCK task = active
- CLEAN task = active
```

閉店を `simulation paused` としてはいけない。

---

## 4. 閉店中に資金が減る主因は「補充した商品分の代金」

初代専用FAQは明確に:

- 閉店中でもお金が減るように見える。
- 実際には `補充した商品分の代金のみ`。

と説明する。

Source:
- https://wikiwiki.jp/theconveni1/FAQ

証拠レベル: CONFIRMED-COMMUNITY

### 非常に重要な実装上の意味

少なくとも原作では、補充行為と仕入コストの発生が近接している。

安全な候補モデル:

```text
onRestockUnits(product, quantity):
    shelf_stock += quantity
    cash -= purchase_cost(product, quantity)
```

ただしこれは**実装候補**であり、原作内部コードがこの瞬間に直接仕入計上していると断定するものではない。

---

## 5. レジ待ち客がいても補充を優先する場合がある

初代専用FAQ:

- レジに客が並んでいても補充等のタスクがあると、店員がギリギリまでレジへ向かわない場合がある。

Source:
- https://wikiwiki.jp/theconveni1/FAQ

証拠レベル: CONFIRMED-COMMUNITY

### 意味

`REGISTER` が絶対最優先ではない。

```text
Staff AI
- evaluate restock
- evaluate register
- evaluate cleaning
- evaluate rest
```

という複数タスク間の優先判断が必要。

完全に最適化された現代AIへ置換すると、原作の人材差・レイアウト差・レジ渋滞が消える可能性がある。

---

## 6. レイアウトが補充効率へ影響している可能性が高い

PS版レイアウト比較では:

- 旧レイアウトでレジ無人/渋滞が多い時期があった。
- 休憩スペースからレジまでの距離は新旧同じ。
- 筆者は `商品の補充で手間取ったのでしょうか？` と原因候補を挙げる。

Source:
- https://minkara.carview.co.jp/userid/2518797/blog/40369273/

この原因自体は筆者の推測なのでHYPOTHESIS。

一方、店員が実際に棚へ歩いて補充すること、内装で客/店員が詰まることは別の初代資料で強く確認されている。

### baseline要求

補充時間を単なる店舗全体のタイマーにせず:

```text
staff position
 -> navigate to target fixture
 -> perform restock work
```

を表現できる構造にする。

---

## 7. 「棚容量」は存在するはずだが、初代PSの正確な値は未回収

商品棚/ワゴン/冷蔵/冷凍等には大小の設備があり、商品が減って補充が必要になるため、設備ごとの在庫量上限が存在すると考えるのが自然。

しかし現時点で:

- 初代PS/SSの各棚収容量
- 補充1回あたりの個数
- 補充開始閾値

を直接示す高品質な初代表は未回収。

**『ザ・コンビニ2』の設備表にある収容数を流用しない。**

### baselineデータ

```text
FixtureInventory
- capacity: UNKNOWN
- current_stock
- restock_threshold: UNKNOWN
```

で保持する。

---

## 8. バックヤード在庫/倉庫在庫の存在は現在未確認

現在までの初代PS/SS資料で確認できているのは:

- 店員が棚を補充する。
- 補充に商品代金が発生する。
- 休憩室へ店員が戻る。

である。

現在までに**初代PS/SSの別管理されたバックヤード商品在庫、倉庫数量、発注ロット、発注残**を示す直接証拠は見つかっていない。

### 重要

これは「存在しないことを証明した」ものではない。

現段階では:

```text
BackroomInventory = UNKNOWN
PurchaseOrderSystem = UNKNOWN / no evidence found yet
```

とする。

現代コンビニらしさのために勝手に発注システムを追加しない。

---

## 9. プレイヤーの手動補充が初代PSに存在するかは未確定

後続作『2』については手動補充の話題がネット上に多いが、これは初代baselineへ流用できない。

PS初代の実機比較では完全に店員任せで運用されているが、これは `手動補充機能が存在しない` ことの証明ではない。

現時点:

```text
manual_restock_action: UNKNOWN
```

説明書/実機UI取得待ち。

---

## 10. 品切れとアンケートの接続

SS実プレイ記録ではアンケートが:

- 商品の置き忘れ
- 品切れ対策

に役立つとされる。

したがって品切れは単なる売上0ではなく、`欲しかったが買えなかった需要` としてプレイヤーへフィードバックされる。

既存 `information-feedback-loop` と接続:

```text
shelf out of stock
 -> customer cannot obtain desired product
 -> lost demand / survey data
 -> player notices shortage
 -> improve fixture/capacity/layout/staff
```

---

## 11. baseline用最小モデル

現在の証拠だけで安全に作れる最小形:

```text
ShelfInventory
- product/category
- current_stock
- capacity: data-driven UNKNOWN initially

RestockTask
- fixture_id
- required_units
- assigned_staff
- progress

Restock completion
- increase shelf stock
- charge purchase cost
- staff restock skill grows
- stamina decreases
```

### まだ追加しない

- 発注点方式
- ケース/ロット発注
- 発注リードタイム
- 配送便
- 倉庫在庫
- 賞味期限
- 廃棄
- POS自動発注

これらは後続作や現代コンビニには自然でも、初代PS baselineの証拠がない。

将来オリジナル拡張として入れる場合はbaseline完成後に別仕様化する。

---

## 12. 次の調査対象

Priority A:

1. 初代各棚/ワゴンの収容量。
2. 補充開始条件。
3. 1回の補充量。
4. 休憩室が補充開始地点なのか。
5. 店員が補充時にどこから商品を持ってくる描画/経路。
6. 手動補充の有無。
7. 商品仕入原価/利益率との計算関係。
8. 品切れアンケート画面の正式表示。

1997年PS/SS攻略本の設備データリストが最有力。
