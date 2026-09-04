# 初代PS/SS 情報取得・アンケート・顧客直接介入のフィードバックループ 2026-09-05

対象: 1997年PS/SS版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 原作でプレイヤーが「何を見て、どう改善するか」をUI/ゲームループとして整理する。
- 調査画面、客個体選択、ライバル情報を別系統として扱う。
- 実装で経営結果をブラックボックス化しない。

主要ソース:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://daiyamonndohuyukai.seesaa.net/article/416425070.html
- https://wazap.com/cheat/%E5%AE%A2%E3%81%AB%E6%80%92%E3%82%89%E3%82%8C%E3%81%AA%E3%81%84%E3%82%88%E3%81%86%E3%81%AB%E3%81%99%E3%82%8B/51715/
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87

---

## 1. `調査` は経営改善の中心フィードバック

Saturn版実プレイ記録では `調査` コマンドから:

- 各店舗の売上成績
- アンケート
- 収支グラフ

を確認できる。

特にアンケートについて:
- 客が欲しかった商品を知る。
- 置いていない商品を発見する。
- 品切れ対策に使う。

という用途が明記される。

証拠レベル: CONFIRMED-COMMUNITY / SS-DIRECT-PLAY

### 原作の改善ループ

```text
営業する
 -> 客が来る
 -> 売れない / 欲しい物が無い / 品切れ
 -> 調査・アンケートを見る
 -> 商品を追加 / 棚を増やす / 配置を変える
 -> 再び営業結果を見る
```

これはbaselineで必ず残す。

---

## 2. アンケートは「売れた商品」だけではなく「欲しかった商品」を示す

同実プレイ記事のスクリーンショット説明では:

- `アンケートを見れば客の欲しかった商品が一目瞭然`
- 本を欲しがる例

が紹介される。

### 実装上の重要性

売上ログだけでは:

```text
book sales = 0
```

が
- 誰も本を欲しくなかった
- 本棚を置いていなかった
- 品切れしていた

のどれか判別できない。

原作はアンケートによって**失われた需要**をプレイヤーへ可視化している。

データモデル候補:

```text
LostDemandRecord
- store_id
- customer_archetype?
- desired_product_or_category
- failure_reason?
- timestamp
```

`failure_reason` を原作が明示していたかは未確認なので、内部ログ候補に留める。

---

## 3. 個々の客を直接選択すると購入内容を確認できる

初代プレイ回顧では:

- 実際に来店している客を選択できる。
- その客が購入する内容を見られる。

Source:
- https://daiyamonndohuyukai.seesaa.net/article/416425070.html

証拠レベル: CONFIRMED-COMMUNITY / FIRST-TITLE-PLAY-RECOLLECTION

別のSS実プレイ記事にも `お客さんの情報も見られる` というスクリーンショット説明がある。

### baseline要求

客は単なる描画spriteではなく、選択可能なsimulation entity。

```text
CustomerEntity
- id
- archetype
- current_state
- held_items[]
- intended_items[]?  # exact visibility unknown
- position
- queue_state
```

表示項目は実画面取得まで全部確定しない。

---

## 4. `つまみだす` は選択客への直接コマンド

複数の初代PS/SS資料で:

- 客を選択して `つまみだす` ことが可能。
- 万引き犯を追い出せる。
- 普通の客も追い出せる。
- 怒りそうなレジ待ち客を怒る前に追い出す攻略も存在。

Sources:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://wazap.com/cheat/%E5%AE%A2%E3%81%AB%E6%80%92%E3%82%89%E3%82%8C%E3%81%AA%E3%81%84%E3%82%88%E3%81%86%E3%81%AB%E3%81%99%E3%82%8B/51715/

証拠レベル: CONFIRMED-COMMUNITY / PS+SS

### 重要

これは万引き専用自動処理ではなく、**プレイヤーが個体客へ直接介入できる操作**。

```text
CUSTOMER_INSPECT_MODAL
  -> show customer info
  -> EJECT_CUSTOMER (`つまみだす`)
```

という状態をUiState候補へ追加する価値が高い。

---

## 5. 客タイプごとの購買傾向も観察対象

初代回顧では:

- 学生
- おじいさん
- OL
- 主婦
- サラリーマン

など客層が異なり、購入傾向も違うことを観察する楽しさが記録される。

Source:
- https://daiyamonndohuyukai.seesaa.net/article/416425070.html

既存資料では学校付近で学生客が増えることも確認済み。

### ループ

```text
町の立地
 -> 来る客層
 -> 欲しい商品
 -> 客を直接観察 / アンケート
 -> 品揃えを調整
```

ここまでが一つの原作経営体験として繋がる。

---

## 6. ライバル情報は無料ではなく50万円の有料調査

PS/SS複数資料:

- 1回50万円。
- ライバル店の営業時間や売上/利益系の基本情報を確認できる。
- ライバルの店内レイアウトまでは見られない。

Sources:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

証拠レベル: CONFIRMED-COMMUNITY / PS+SS

### 意味

ライバル情報にはinformation costがある。

```text
pay 500,000
 -> inspect rival financial state
 -> choose price war / acquisition / expansion response
```

原作ではセーブして調査→ロードで費用を回避するプレイヤー例もあるが、これは攻略上の抜け道でありbaseline仕様にする必要はない。

---

## 7. 顧客独占率は `調査` で確認できる

初代専用Wikiは:

- `顧客独占率` をメニューの `調査` から確認できるパラメータと明記。

Source:
- https://wikiwiki.jp/theconveni1/%E9%A1%A7%E5%AE%A2%E7%8B%AC%E5%8D%A0%E7%8E%87

この数値を見て:
- 価格
- 品揃え
- 営業時間
- 周辺競合
- 天候

の効果をプレイヤーが判断できる。

### baseline要求

顧客独占率を内部値だけにせず、プレイヤーから確認可能にする。

---

## 8. 情報は3つの粒度に分かれる

現在の証拠から原作の情報取得は少なくとも3層:

```text
MICRO: individual customer
- selected customer's shopping state
- eject command

STORE: own-store research
- sales results
- survey / lost demand
- customer share
- income/expense graphs

COMPETITOR: paid rival investigation
- rival hours
- sales/profit-like metrics
- no interior visibility
```

この3階層をRemakeのUXでも維持する。

---

## 9. Vertical Sliceへの要求

最初の店内プロトタイプでも、単に客を歩かせるだけではなく:

1. 客をタップして個体情報を見る。
2. 客が欲しい物を買えなかった事実をログする。
3. 期間後に簡易アンケート結果を見る。
4. 棚/商品を変更する。
5. 売上/失敗需要が変化する。

まで繋げると、原作らしい「観察して改善」が成立する。

### まだ未確定

- アンケートの正式サブメニュー名。
- アンケートの集計期間。
- 何件/何商品まで表示するか。
- 客個体情報画面の全項目。
- `つまみだす` の確認ダイアログ有無。
- 強制退店で人気/評価が下がるか。
- ライバル調査結果の全項目。

説明書/原作画面で継続確認する。
