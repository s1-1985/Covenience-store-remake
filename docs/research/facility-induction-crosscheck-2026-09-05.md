# 初代PS 施設誘致の独立クロスチェック 2026-09-05

対象: 1997年PlayStation版『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- 初代専用攻略Wikiで確認済みの「施設誘致」を、別系統の初代PS資料で独立確認する。
- 後続作の施設データを混ぜず、PS baselineとして安全に採用できる範囲を絞る。

---

## 1. 電撃PlayStationの2013年初代PS紹介記事

Source:
- https://dengekionline.com/elem/000/000/722/722919/

記事情報:
- 掲載日: 2013-10-07
- 対象を「1997年3月28日に初代PSで発売されたシリーズ1作目」と明記
- 紹介対象はゲームアーカイブス版だが、原典は初代PS版

証拠レベル:
- CONFIRMED-PS-SPECIFIC / SECONDARY-EDITORIAL

記事では、プレイヤーが町の発展へ関与できる要素として、大学や警察などの施設を誘致できると明記されている。

### 今回新たに独立確認できたこと

```text
FacilityInduction
- player_initiated = true
- confirmed_examples:
  - university
  - police
```

つまり「町は完全自動発展のみ」ではなく、プレイヤー側に施設誘致の明示的な介入手段があることが、初代専用Wiki以外のPS資料からも確認できた。

---

## 2. 初代専用Wikiとの照合

初代PS/SS専用Wikiのゲームモード攻略では、以下の記述がある。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

確認できる施設/町発展要素:
- 交番
- 消防署
- 大学
- 市役所
- 都庁
- 駅

ただし、すべてが同じ発生方式ではない。

### 誘致として明示・強く示唆されるもの
- 大学
- 交番/警察系
- 消防署

### 人口条件等で自動出現するとされるもの
- 駅: 町人口5000人超で線路上に出現する観測
- 都庁: 初級で町人口2万人超により自動出現する観測
- 市役所: 左下の役場用地に後から出現する観測があるが厳密条件未確定

証拠レベル:
- Wiki記述: CONFIRMED-COMMUNITY / FIRST-TITLE-SPECIFIC
- 人口閾値の厳密仕様: PROVISIONAL

---

## 3. 実装上の重要区分

町施設を一律に `induce()` で生成する設計は避ける。

少なくとも次の発生方式を分けられる構造が必要。

```text
FacilitySpawnMode
- PLAYER_INDUCED
- POPULATION_TRIGGERED
- SCRIPTED_SCENARIO
- UNKNOWN
```

現時点の安全な暫定割当:

```text
university: PLAYER_INDUCED confirmed
police: PLAYER_INDUCED confirmed
fire_station: PLAYER_INDUCED provisional-high
station: POPULATION_TRIGGERED provisional
metropolitan_government: POPULATION_TRIGGERED provisional / scenario-linked
city_hall: UNKNOWN or POPULATION_TRIGGERED provisional
```

ここで `confirmed` は「存在と誘致可能性」の確認であり、費用・成功率・設置可能条件まで確定した意味ではない。

---

## 4. 施設誘致と買い物人口は分離して扱う

現在確認できている駅の `2240人` は、初代専用Wikiの攻略観測による人口値である。

しかし以下は未確定:
- 2240が建物人口か「買い物人口」か
- 来店候補人数の母数か
- 客層内訳
- 時間帯別来店分布
- 店舗からの影響距離

したがって、実装データで:

```text
FacilityDefinition
- population
- shopping_population
```

を同一値として固定しない。

少なくとも:

```text
population_value_reported: 2240
population_semantics: UNKNOWN
```

のように意味を保留する。

---

## 5. プレイヤー誘致施設の効果も未確定

大学/警察/消防署について存在と誘致自体は強く確認できるが、効果の完全仕様はまだ足りない。

未確定:
- 誘致費用
- 誘致成功率
- 1マップの最大設置数
- 設置可能セル
- 建築完了までの時間
- 周辺店への影響距離
- 大学の正確な人口値
- 警察/消防署が警備へ与える定量効果
- 同施設を複数誘致した際の重複効果

初代Wikiには「交番、消防署が近くに無い場合は必ず誘致」「警備100維持」といった攻略記述があるが、警備への数式は不明。

### baseline方針

施設の存在だけ先に固定し、効果式は UNKNOWN とする。

---

## 6. 時間進行に関する独立再確認

同じ電撃PlayStation記事は、初代PS版の特徴としてゲーム中の経過時間を操作できないことも明記している。

これは既存研究 `ps-time-control-observation-loop-2026-09-05.md` と一致するため、新規仕様変更はない。

独立ソースが増えたという意味で証拠強度のみ上昇。

```text
TimeControl.speed_change = not available in original PS gameplay
confidence = high
```

後続作の倍速機能を初代へ混入させない。

---

## 7. 今回の確定度更新

### CONFIRMED-HIGH
- 初代PSではプレイヤーが施設誘致を行える
- 誘致対象の具体例として大学と警察が存在
- 施設誘致は町の発展へ介入するゲーム機能
- 初代PSは通常プレイ中の時間速度変更不可

### CONFIRMED-COMMUNITY
- 消防署も誘致対象
- 交番/消防署の存在が警備運用上重要

### PROVISIONAL
- 駅が町人口5000人超で出現
- 駅人口2240
- 都庁が町人口2万人超で自動出現
- 市役所/都庁用の特殊用地

### UNKNOWN
- 全誘致施設一覧
- 各誘致費用
- 成功率
- 正確な買い物人口
- 効果範囲
- 建設時間
- 発生式

---

## 8. 次の調査ターゲット

優先順位:
1. PS説明書/攻略本の「誘致」画面本文
2. 施設選択メニューの原作画面
3. 大学/警察/消防署の費用表示
4. 建物データ表の人口/買い物人口列
5. 誘致成功/失敗メッセージ
6. 駅・市役所・都庁の発生条件画面

後続作の施設データは数値補完に使用しない。
