# 初代PS/SS メニュー階層・経営コマンド証拠 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 原作の経営コマンドを、続編のメニュー構造から逆輸入せず復元する。
- `正式な階層名まで確認済み` と `機能の存在のみ確認` を分離する。
- 公式スクリーンショットで確認済みのUiStateへ、未表示の経営機能を安全に接続する。

主要ソース:
- https://wikiwiki.jp/theconveni1/%E5%AE%A3%E4%BC%9D
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://codevis.nobody.jp/review-ps/the_convini.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

---

## 1. `販促 → 宣伝` は初代専用資料で明示

初代専用宣伝Wikiは明確に:

```text
「販促」→「宣伝」
```

と記載する。

したがって:

```text
販促
  └─ 宣伝
```

はCONFIRMED-COMMUNITYとしてbaselineへ採用可能。

宣伝画面自体は現行Console Archives公式スクリーンショットでも視覚確認済み。

---

## 2. `販促` 配下に `誘致` がある可能性は非常に高いが、矢印表記までは未取得

Saturn実プレイ記事は:

- メニューに `販促` コマンドがある。
- 同じ節で `宣伝` と `誘致` を、資金を使って店/町に恩恵を与える販促系機能として説明する。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル:
- `販促` root: CONFIRMED-COMMUNITY
- `誘致` 機能の存在: CONFIRMED-COMMUNITY
- `販促 → 誘致` という厳密な親子階層: STRONG-CANDIDATE

### baseline

```text
販促
  ├─ 宣伝      # confirmed hierarchy
  └─ 誘致      # strong candidate hierarchy
```

説明書/実画面で矢印関係を確認するまで `誘致` の親を絶対確定にはしない。

---

## 3. `調査 → 全店収支グラフ` は初代専用Wikiで明示

初代ゲームモード攻略では、上級のオーナー評価について:

```text
「調査」→「全店収支グラフ」にある総合評価
```

と明記する。

したがって:

```text
調査
  └─ 全店収支グラフ
```

はCONFIRMED-COMMUNITY。

### 重要

`全店収支グラフ` は単なるグラフ表示ではなく、上級クリアに関係する `総合評価` を確認する主要画面でもある。

---

## 4. `調査` から顧客独占率を確認できる

初代専用顧客独占率Wiki:

- `メニューの「調査」から確認できるパラメーター` と明記。

Source:
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87

証拠レベル: CONFIRMED-COMMUNITY

### 未確定

- `顧客独占率` が独立したサブメニュー名か。
- 店舗成績画面の一項目として表示されるのか。
- 何段目の画面にあるか。

よって:

```text
調査
  └─ [some research screen]
       └─ 顧客独占率 parameter
```

までを確定する。

---

## 5. `調査` で各店舗の売上成績・アンケート・収支グラフを見られる

Saturn版詳細実プレイ記事では `調査` コマンドで:

- 各店舗の売上成績
- 売れ筋のアンケート
- 収支グラフ

を確認できると記録される。

アンケートは:
- 欲しかった商品
- 商品の置き忘れ
- 品切れ対策

に役立つとされる。

Source:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php

証拠レベル: CONFIRMED-COMMUNITY / SS-DIRECT-PLAY

### 注意

記事の説明文がそのままゲーム内サブメニュー名とは限らない。

そのため現時点では:

```text
調査
  ├─ 全店収支グラフ        # exact name confirmed elsewhere
  ├─ [店舗売上成績系]
  └─ [アンケート系]
```

とする。

`店舗成績`、`売れ筋`、`アンケート` 等を正式ラベルとして勝手に固定しない。

---

## 6. ライバル店調査は50万円で実行できる

複数の初代PS/SS実プレイ記録:

- ライバル店を調査するには50万円必要。
- 営業時間や売上/収益等の基本情報を確認できる。
- ライバル店の内部/店内までは確認できない。

Sources:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

証拠レベル: CONFIRMED-COMMUNITY / PS+SS

### 確定できること

```text
Rival Investigation
- cost: 500,000 yen
- reveals: business hours, sales/profit-like financial info
- does_not_reveal: interior layout
```

### 未確定

- 正式なサブメニュー名。
- `調査` rootの直下か、ライバルを選んだ後に出るのか。
- 調査結果画面の正確な項目。

機能は `調査` 系として保持するが、階層はUNKNOWN。

---

## 7. 店員関連のゲーム内アクション名

初代専用店員Wikiは次の名称を明示:

- `店員の雇用`
- `店員の異動`

それぞれで表示されるパラメーターが異なることまで詳述される。

Source:
- https://wikiwiki.jp/theconveni1/%E5%BA%97%E5%93%A1

証拠レベル: CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC

### 現時点の状態

```text
[PERSONNEL_ROOT_UNKNOWN]
  ├─ 店員の雇用
  └─ 店員の異動
```

親メニューが `人事` 等なのかは初代PS/SSで未確認。

**後続作で親メニューが人事だからという理由で初代へ流用しない。**

解雇機能の存在も確認済みだが、画面名/操作位置は未確定。

---

## 8. 内装・改築・価格設定・営業時間は独立した管理操作として存在

初代PS/SSの複数資料から機能として強く確認済み:

- 内装
- 改築
- 価格設定 / 利益率調整
- 営業時間設定

Sources:
- https://codevis.nobody.jp/review-ps/the_convini.html
- https://wikiwiki.jp/theconveni1/FAQ
- PS詳細プレイ記録群

特にPSレビューでは:
- 営業時間6プリセット
- 商品ごとに利益率設定
- 全品目一括設定

が明記される。

### しかし親メニューは未確定

```text
[STORE_MANAGEMENT_ROOT_UNKNOWN]
  ├─ 内装
  ├─ 改築
  ├─ 営業時間設定
  └─ 価格/利益率設定
```

という機能グループとして保持するだけにする。

公式PS画像で `内装編集` 内部の `配置/移動/入れ替え/売却/終了` は直接確認済み。

---

## 9. 初代メニューの安全な暫定ツリー

現段階で原作名を捏造しないツリー:

```text
ROOT / WORLD UI
│
├─ 販促                         [CONFIRMED]
│   ├─ 宣伝                     [CONFIRMED]
│   └─ 誘致                     [STRONG-CANDIDATE]
│
├─ 調査                         [CONFIRMED]
│   ├─ 全店収支グラフ           [CONFIRMED]
│   ├─ 店舗売上成績系           [FUNCTION CONFIRMED / LABEL UNKNOWN]
│   ├─ アンケート系             [FUNCTION CONFIRMED / LABEL UNKNOWN]
│   ├─ 顧客独占率表示           [FUNCTION CONFIRMED / exact location UNKNOWN]
│   └─ ライバル店調査           [FUNCTION CONFIRMED / LABEL & level UNKNOWN]
│
├─ [PERSONNEL ROOT UNKNOWN]
│   ├─ 店員の雇用               [CONFIRMED ACTION NAME]
│   ├─ 店員の異動               [CONFIRMED ACTION NAME]
│   └─ 解雇                     [FUNCTION CONFIRMED]
│
└─ [STORE MANAGEMENT ROOT UNKNOWN]
    ├─ 内装                     [CONFIRMED FUNCTION]
    │   ├─ 配置                 [OFFICIAL VISUAL]
    │   ├─ 移動                 [OFFICIAL VISUAL]
    │   ├─ 入れ替え             [OFFICIAL VISUAL]
    │   ├─ 売却                 [OFFICIAL VISUAL]
    │   └─ 終了                 [OFFICIAL VISUAL]
    ├─ 改築                     [CONFIRMED FUNCTION]
    ├─ 営業時間                 [CONFIRMED FUNCTION]
    └─ 価格/利益率              [CONFIRMED FUNCTION]
```

---

## 10. UiStateへの接続候補

既存公式UI研究の状態へ接続すると:

```text
TOWN_VIEW
  -> STORE_LOCATION_SELECT
  -> PROMOTION_SELECT_MODAL
  -> [ATTRACTION_SELECT_MODAL]
  -> [RESEARCH_MENU_MODAL]
  -> [RIVAL_RESEARCH_MODAL]

STORE_LIVE_VIEW
  -> INTERIOR_EDIT
  -> [STAFF_HIRE_MODAL]
  -> [STAFF_TRANSFER_MODAL]
  -> [HOURS_SETTINGS_MODAL]
  -> [PRICE_SETTINGS_MODAL]
  -> [REMODEL_FLOW]
```

角括弧内は機能存在は強いが、正確な画面形状・遷移元は未確認。

---

## 11. 次に確定すべきこと

Priority A:

1. 原作のトップレベルコマンド一覧を1枚の画面/説明書から取得。
2. `販促` の全サブメニュー。
3. `調査` の全サブメニュー正式名称。
4. 店員関連の親メニュー正式名称。
5. `内装/改築/価格/営業時間` の親メニュー正式名称。
6. ライバル調査の正式ラベルと結果項目。
7. 各メニューを開くPSボタン。

説明書本文または当時攻略本の操作ページが取れれば一気に確定可能。
