# 初代PS 店舗選択UI・店舗価格・商品選択画面の実画面証拠 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 原作実画面から店舗選択UI、店舗価格、店舗個別メニュー、商品選択画面の構造を復元する。
- 後続作の値やメニューを混入させない。
- 画像そのものは保存せず、読取結果と出典URLだけを記録する。

## 証拠レベル表記

- CONFIRMED-VISUAL: 初代PS実画面で直接確認
- STRONG-INFERENCE: 実画面配置からかなり強く推測できるが、文字ラベル等で完全確定していない
- UNKNOWN: 未確定

---

## 1. 店舗選択画面に6つの店舗アイコンが存在

初代PS実画面に以下を確認した。

画面文言:
- `店舗を選んで下さい`
- 選択中価格 `¥6,000,000`

店舗アイコン:
- 2行×3列、合計6個
- 左列は小型外観、中央列は中型外観、右列は大型外観に見える
- 上段/下段は同規模の向き違いに見える

Source:
- https://www.gavas.jp/products/detail.php?product_id=9180
- 同ページ掲載の1997年PSプレイ画面

証拠レベル:
- 6アイコン: CONFIRMED-VISUAL
- 選択中価格600万円: CONFIRMED-VISUAL
- 3規模×2方向という意味: STRONG-INFERENCE

### 実装上の意味

店舗定義は少なくとも:

```text
StoreBuildingVariant
- size_class: SMALL / MEDIUM / LARGE
- orientation_variant: A / B
- construction_price
- interior_mask
- exterior_footprint
```

を分離できる構造が安全。

大型店については初代専用Wikiで「縦13×横14」「縦型（建設時リストで上）の方が店内スペースが広い」と既に確認済みであり、今回の2行構造はその記述と整合する。

Source:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

### 600万円の扱い

画面上ではカーソルが左上の小型店舗アイコン上にあり、価格欄が600万円になっている。

したがって:

```text
small_store_variant_A_price = 6,000,000 yen
```

はCONFIRMED-VISUALとして扱える。

一方、左下の向き違い小型店も同額かどうかは、画面上で直接カーソル選択した状態を確認できていないため未確定。

中型/大型の新規建設価格も未確定。

---

## 2. 店舗個別メニューの4項目を原作実画面で直接確認

別の初代PS実画面で、店舗を選択した際の右側メニューに以下4項目が表示される。

- `内装`
- `方針`
- `店員`
- `改築`

また同画面には:
- 店舗名
- 営業時間 (`AM7:00 ～ PM11:00` の例)
- `評価` の星表示

がある。

Source:
- https://refuge.tokyo/playstation/ps/00321.html
- 検索結果で確認した同ページの初代PSスクリーンショット

証拠レベル: CONFIRMED-VISUAL

### 状態遷移として固定できる範囲

```text
Town/Store View
  -> select own store
      -> Store Menu
          - Interior (内装)
          - Policy (方針)
          - Staff (店員)
          - Rebuild/Expansion (改築)
```

ここで `方針` の下位項目はまだ全数未確定。

`改築` が店舗個別メニューに直接存在するため、新規出店と既存店舗拡張はUI上も別経路である。

---

## 3. 宣伝選択画面は複数選択式

同じ初代PSスクリーンショット群には:

- `宣伝方法を選択して下さい（複数選択可）`
- `ダイレクトメール ¥100,000/月`
- `費用合計 ¥100,000/月`
- 宣伝手段5個のアイコン
- `終了・・START`

が写っている。

Source:
- https://refuge.tokyo/playstation/ps/00321.html

証拠レベル: CONFIRMED-VISUAL

既存研究の宣伝5種（DM/新聞/飛行船/ラジオ/TV）と整合する。

UI実装では単一ラジオボタンではなく複数同時選択を前提とする。

---

## 4. 商品選択画面で「調味料類 ¥9,600/日」を直接確認

電撃PlayStation系の記事に掲載された初代PS実画面で、商品選択ダイアログを確認。

表示:
- `商品を選択して下さい`
- 選択中カテゴリ `調味料類`
- `¥9,600/日`
- 3行×4列、合計12個の商品カテゴリ/商品群アイコン

Source:
- https://dengekionline.com/elem/000/000/722/722934/

証拠レベル:
- 調味料類というカテゴリ名: CONFIRMED-VISUAL
- 9,600円/日という表示値: CONFIRMED-VISUAL
- 9,600円/日の正確な意味（仕入費/維持費/原価等）: UNKNOWN
- 画面に12個の選択肢が存在: CONFIRMED-VISUAL

### 重要な注意

この `¥9,600/日` を現時点で「維持費」や「仕入原価」と断定しない。

画面は商品選択中であり、値が日単位なのは確定だが、説明書や攻略本の用語定義がまだ必要。

安全なデータモデル:

```text
ProductCategory
- name
- daily_cost_display: nullable
- daily_cost_semantics: UNKNOWN / PROCUREMENT / MAINTENANCE / OTHER
```

---

## 5. 顧客詳細ポップアップの項目を原作画面で再確認

電撃PlayStation系の記事に掲載された別画面では顧客を選択すると:

- 客タイプ名（例: おじさん）
- `買いにきた品物`
- `すでに購入した`
- `所持金 ¥1,265`
- `OK`
- `つまみだす`

が表示される。

Source:
- https://dengekionline.com/elem/000/000/722/722938/

証拠レベル: CONFIRMED-VISUAL

これは既存研究の顧客状態モデル:

```text
Customer
- target_item / intended_purchase
- purchased_items
- cash_on_hand
```

を原作画面で直接補強する。

---

## 6. 町建物の買い物人口表示も実画面確認

電撃PlayStation系の記事掲載画面で町建物を選択すると:

- 建物名 `役所`
- `買い物人口 250人`

と表示される。

Source:
- https://dengekionline.com/elem/000/000/722/722931/

証拠レベル: CONFIRMED-VISUAL

これにより、町建物には単なる人口とは別に、ゲームUI上明示された `買い物人口` が存在することを直接確認できる。

したがって駅の攻略記録 `2240人` なども、単純に総人口と同一視してはいけない。

安全なモデル:

```text
TownFacility
- resident_population: UNKNOWN / nullable
- shopping_population: explicit game parameter
```

今回確定:

```text
役所.shopping_population = 250
```

---

## 7. 今回の確定事項

CONFIRMED-VISUAL:
- 店舗選択画面に6アイコン
- 左上小型店舗選択時の価格600万円
- 店舗個別メニュー `内装 / 方針 / 店員 / 改築`
- 店舗メニューに営業時間と評価星表示
- 宣伝画面が複数選択可
- DM 10万円/月の実画面表示
- 商品選択画面に12選択肢
- `調味料類 ¥9,600/日`
- 顧客詳細に買いに来た品物/購入済み/所持金/つまみだす
- 町建物 `役所` の `買い物人口 250人`

STRONG-INFERENCE:
- 店舗6種は小/中/大 × 2方向

UNKNOWN:
- 小型方向Bの建設費
- 中型/大型の新規建設費
- 小型/中型の正確な内部マス数
- 9,600円/日の会計上の意味
- 商品選択12枠の全カテゴリ名
- `方針` の完全な下位メニュー

---

## 8. 次の最優先調査

1. 6店舗アイコンを一つずつ選択した画面を探し、新規建設費を全6種回収
2. 小型/中型の店内画面を正面から取得し、グリッドセル数を数える
3. 商品選択12枠の各カーソル状態を取得し、カテゴリ名と日額を全回収
4. 役所以外の町建物を選択した画面から買い物人口表を作る
5. `方針` メニューを開いた原作画面を回収して完全階層化

原作画像そのものは著作権保護のためリポジトリへ保存しない。