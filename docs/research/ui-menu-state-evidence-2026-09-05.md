# 初代PS/SS版 UI・メニュー・状態遷移 追加調査 2026-09-05

対象: 1997年PlayStation / Sega Saturn版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- Android Remakeで必要になる画面状態とメニュー階層を、初代専用資料・初代実画面・当時パッケージから復元する。
- 『ザ・コンビニ2』のメニュー体系・高速モード・UIを混同しない。
- 正式なトップレベル全メニュー名が未回収の箇所は、無理に補完しない。

## 証拠レベル

- CONFIRMED-VISUAL: 初代PS/SS実画面で直接確認
- CONFIRMED-PACKAGE: 初代PSパッケージ裏の当時資料で確認
- CONFIRMED-COMMUNITY: 初代PS/SS専用の詳細プレイ記録・専用Wikiで一致
- PROVISIONAL: 単一資料・正式メニュー名が不明
- UNKNOWN: 未回収

---

## 1. 常時HUD: 年・月日・天候・時刻・所持金

初代PSの店舗選択画面、町画面、初代SS店内画面で、画面最上段に以下が常時並ぶ。

```text
[年] [月日] [天候] [時刻] [所持金]
```

PS実画面例:
- `01年目01月01日 [快晴] 00:00 ¥180,000,000`

SS実画面例:
- `1年目 3月2日 [晴れ] 12:46 ¥57,903,060`

Sources:
- https://www.gavas.jp/products/detail.php?product_id=9180
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-VISUAL

### baseline要求

スマホ版でもゲーム状態として最低限:

```text
GameHUDState
- year
- month
- day
- weather
- clock
- cash
```

を常時参照可能にする。

ただしAndroidの画面占有を考え、見た目までPSの1行バーに固定する必要はない。

---

## 2. 店内表示: 店舗名・本店/支店・売上カード

初代SS実画面では、店内トップビューの右側に店舗カードが表示される。

読める内容:
- 店舗名/チェーン名表示
- `本店`
- `売上 ¥11,025`
- 小さな状態アイコンが3つ

Source:
- https://mimora.mimoza.jp/yao_game/retro/images/ctg_main/memorandum/detail/SS/pict/SS-0001/img_gmrSS_0001-05.webp

証拠レベル: CONFIRMED-VISUAL / SS

### 注意

小型アイコン3つの意味は、この解像度だけでは断定しない。

PSの電撃掲載店内画面でも、画面下部に店舗名/号店と小型アイコン群が確認でき、PS/SSで「現在見ている店舗の状態を常時表示する」UI思想は共通と考えてよい。

Source:
- https://dengekionline.com/elem/000/000/722/722919/

---

## 3. 新規出店時の状態遷移

初代PS/SS専用の実プレイ記録では、新店舗を開店するまでに以下を行う。

```text
町マップ
 -> 出店場所選択
 -> 店舗外観/規模選択
 -> 酒・タバコ・薬品の販売許可申請
 -> 内装設定
 -> 店員雇用
 -> 営業方針設定
 -> 開店
```

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- 既存PS実プレイ研究メモ

証拠レベル: CONFIRMED-COMMUNITY

### UI実装上の要求

新規出店を一画面の巨大フォームにまとめず、原作同様に段階的なセットアップへ分割できる構造にする。

```text
NewStoreWizardState
- SELECT_LOCATION
- SELECT_STORE_TYPE
- APPLY_PERMITS
- EDIT_LAYOUT
- HIRE_STAFF
- SET_POLICY
- OPEN_CONFIRMATION
```

正式な遷移順の細部はPS説明書本文で最終確認する。

---

## 4. 店舗選択画面

初代PS実画面では新規店舗の選択時に6個の店舗アイコンが並ぶ。

画面文言:
- `店舗を選んで下さい`
- 選択中価格 `¥6,000,000`

背景は町マップのままで、モーダル形式の選択ウィンドウが中央に出る。

Source:
- https://www.gavas.jp/upload/save_image/9180_2.jpg

証拠レベル: CONFIRMED-VISUAL / PS

既存の公式画像調査では、L1で店舗サイズ変更のガイドも確認済み。

### baseline要求

```text
WorldMap
 + modal StoreTypePicker
```

という「町を見失わず上に小窓を重ねる」UIは原作らしさの重要要素。

---

## 5. 販促 -> 宣伝 / 誘致

初代SS専用プレイ記録で、トップレベルに `販促` コマンドが存在すると明記される。

その下で少なくとも:
- `宣伝`
- `誘致`

を使用する。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

初代専用Wikiも:
- `販促` → `宣伝`

という階層を明記。

Source:
- https://wikiwiki.jp/theconveni1/%E5%AE%A3%E4%BC%9D

証拠レベル: CONFIRMED-COMMUNITY

### baseline候補

```text
PROMOTION
  - ADVERTISING
  - FACILITY_INVITATION
```

銀行等の他サブ項目を『2』から逆輸入しない。

---

## 6. 宣伝画面は複数選択式

初代PS実画面で:

`宣伝方法を選択して下さい(複数選択可)`

と表示される。

宣伝方法アイコンが5種類横並びで表示され、選択内容に応じて:
- 各項目の月額費用
- `費用合計`

が画面に出る。

Source:
- https://refuge.tokyo/playstation/ps/00321.html

初代専用Wikiから5方式の名称:
- ダイレクトメール
- 新聞広告
- 飛行船
- ラジオ
- TV

Source:
- https://wikiwiki.jp/theconveni1/%E5%AE%A3%E4%BC%9D

証拠レベル: CONFIRMED-VISUAL + CONFIRMED-COMMUNITY

### baseline要求

宣伝を1個だけ選ぶラジオボタンにしない。

```text
AdvertisingSelection
- direct_mail: bool
- newspaper: bool
- blimp: bool
- radio: bool
- tv: bool
- monthly_total_cost
```

---

## 7. 調査コマンド

初代SS専用詳細プレイ記録では `調査` コマンドから以下を確認できる。

確認済み機能:
- 各店舗の売上成績
- 売れ筋/欲しかった商品のアンケート
- 収支グラフ
- ライバル店調査

ライバル調査:
- 50万円
- 営業時間や収益など基本情報
- 店内は見られない

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

また初代専用Wikiでは `顧客独占率` もメニューの `調査` から確認するパラメータと明記。

Source:
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87

証拠レベル: CONFIRMED-COMMUNITY

### 注意

正式なサブメニュー表示名・並び順は未回収。

安全な実装用モデル:

```text
RESEARCH
  - STORE_PERFORMANCE       # exact label unknown
  - FINANCIAL_GRAPH         # exact label unknown
  - CUSTOMER_SURVEY         # exact label unknown
  - CUSTOMER_SHARE          # placement inside UI to verify
  - RIVAL_INVESTIGATION     # exact label unknown
```

正式日本語ラベルは説明書/実画面が取れるまで仮称扱い。

---

## 8. アンケートは「欲しかった商品」の欠落/品切れ検出に使う

初代SSプレイ記録では、アンケートを見ることで客が欲しかった商品を確認し:
- 置き忘れ
- 品切れ

への対策に使えると明記される。

同ページのゲーム画像キャプションでは「本が熱望される」例がある。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-COMMUNITY / VISUAL-CAPTION

### baseline要求

アンケートを雰囲気テキストだけにせず、実際のcustomer demand失敗ログを集計して表示できる設計にする。

```text
CustomerMissedDemandEvent
- customer_type
- desired_product
- reason: NOT_STOCKED | OUT_OF_STOCK | UNKNOWN
```

原作が理由まで区別して表示するかは未確認なので、UIにはdesired_product集計のみから始めるのが安全。

---

## 9. 内装編集: サンプルレイアウト読込が存在

初代SS詳細プレイ記録で:
- 内装は自由配置
- サンプルレイアウトが用意されている
- サンプルを開くと元に戻せない
- 一度に全売却する機能はない

と記録される。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-COMMUNITY

既存公式画像研究では内装編集トップコマンドとして:
- 配置
- 移動
- 入れ替え
- 売却
- 終了

を確認済み。

### baseline要求

```text
LayoutEditor
- PLACE
- MOVE
- SWAP
- SELL
- LOAD_SAMPLE/LAYOUT
- FINISH
```

`LOAD_SAMPLE/LAYOUT` の正式な位置/名称は未確定。

---

## 10. レジ・什器は向きを持つ

初代SS詳細プレイ記録で、レジを逆向きに置くと想定と逆方向に客が並ぶことが明記される。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

初代専用内装Wikiでも什器の利用面・通路確保が重要とされる。

Source:
- https://wikiwiki.jp/theconveni1/%E5%86%85%E8%A3%85

証拠レベル: CONFIRMED-COMMUNITY

### baseline必須

```text
FixtureInstance
- rotation/orientation
- interaction_sides[]
- queue_anchor?   # register only, exact algorithm unknown
```

見た目だけ回転して当たり判定/利用面が同じ、という実装は不可。

---

## 11. 町建物にカーソルを置くと情報ポップアップ

PS実画面で役所を選択すると:

```text
役所
買い物人口 250人
```

というポップアップが町画面上に表示される。

Source:
- https://dengekionline.com/elem/000/000/722/722931/

証拠レベル: CONFIRMED-VISUAL / PS

### baseline要求

町建物は背景絵ではなく選択可能オブジェクト。

```text
TownBuilding
- id
- type
- shopping_population
- selectable
- info_panel_data
```

---

## 12. 原作の時間進行は「速度操作不可」が重要

電撃PlayStationの初代PS紹介では、初代の特徴として:
- `ゲーム中での経過時間を操作できない`
- 店の基盤を整えると、あとは眺めながら進む

と明記される。

Source:
- https://dengekionline.com/elem/000/000/722/722919/

証拠レベル: CONFIRMED-PRESS / PS

### 重要なversion boundary

『ザ・コンビニ2』では高速モードが追加されたことを現行公式が説明しているため、初代Remake baselineに最初から高速モードを「原作仕様」として入れてはいけない。

ただしAndroid版の快適性改善として後から deliberate deviation で追加するのは可能。

### 未確定

- START等で一時停止できるか
- メニューを開いている間に時間が止まるか
- 特定編集画面で時間停止するか

`時間速度を変更できない` と `ゲームを一時停止できない` は同義ではないため、分離して調査する。

---

## 13. PSパッケージ裏が示すゲームの主要UI柱

初代PSパッケージ裏では、小さな実画面付きで主要プレイ要素を紹介している。

確認できる柱:
- 店舗立地/出店
- 店内レイアウト
- 個性的な従業員の雇用/育成
- マーケティング/販促
- 商品/営業管理
- 町に店舗網を広げる

Source:
- https://www.yugiyahiranonetshop.com/product/40436

証拠レベル: CONFIRMED-PACKAGE

### 研究上の意味

Remakeのメインナビゲーションも、この6本柱から大きく外れないようにする。

---

## 14. 現時点のUI状態機械案

原作証拠を壊さない最低構造:

```text
AppState
  TITLE
  SCENARIO_SELECT
  WORLD_MAP
    WORLD_OBJECT_INFO
    STORE_BUILD_WIZARD
    PROMOTION
      ADVERTISING
      FACILITY_INVITATION
    RESEARCH
      STORE_PERFORMANCE
      CUSTOMER_SURVEY
      FINANCE_GRAPH
      CUSTOMER_SHARE
      RIVAL_INVESTIGATION
  STORE_VIEW
    STORE_INFO_OVERLAY
    CUSTOMER_INFO
    STAFF_INFO
    STORE_POLICY
    LAYOUT_EDITOR
      PLACE
      MOVE
      SWAP
      SELL
      LOAD_LAYOUT
      FINISH
  ENDING
```

### 注意

これは**実装用の状態整理**であり、初代の正式メニュー名・階層を完全に確定したものではない。

正式ラベルと並び順は:
1. PS説明書本文
2. PS/SS攻略本の操作章
3. 実機動画/スクリーンショット

で継続回収する。

---

## 15. 今回の確定度更新

UI/メニュー領域の復元度を暫定で:

```text
常時HUD                    90%
新規出店セットアップ        80%
販促                        80%
宣伝                        95%
調査の機能集合              75%
調査の正式ラベル/並び順      40%
内装編集トップコマンド      85%
店舗/客/店員情報パネル      55%
コントローラ完全割当        20%
時間操作/停止条件            35%
```

と評価する。

次の優先調査:
- 初代PSのトップレベルメニュー実画面
- 調査サブメニューの正式ラベルと並び
- 営業方針画面の全項目
- 店員雇用画面の完全列
- 顧客個体情報画面
- 町/店内切替ボタン
- START/SELECT/R1/L1等の初代完全割当
