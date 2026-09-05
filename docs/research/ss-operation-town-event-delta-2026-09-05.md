# 初代PS/SS 運営・町・イベント追加差分 2026-09-05

対象: 1997 PS/SS『ザ・コンビニ ～あの町を独占せよ～』のみ。

主資料:
- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

目的: 既存研究ファイルに未記録だった、実装に影響する運営境界・町施設・イベント結果だけを差分追加する。

## 1. 清掃100で床汚れが発生しなくなる

SS実プレイの豆知識として、店舗の `清掃` パラメータが100になると **床が汚れなくなる** と記録される。

これは単なる評価値ではなく、店内シミュレーションの状態遷移を変える閾値である可能性が高い。

実装候補:

```ts
if (store.cleanliness >= 100) {
  floorDirtGenerationRate = 0;
}
```

ただし、火災やイベント等による特殊な汚れまで完全停止するかは未確認。通常営業中の床汚れについてのルールとして扱う。

Confidence: `CONFIRMED-PLAY-SS`。

## 2. 店員控え室は店外にも設置可能

SS実プレイで `店員控え室` は **店舗建物の外側にも配置できる** と明記される。

したがって、控え室は「店内専用什器」としてハードコードしてはいけない。

実装候補:

```ts
FixtureDefinition {
  id: "staff_break_room";
  allowedZones: ["store_interior", "store_exterior"];
}
```

店外設置時に店員がどう出入りするか、経路上の扉/入口制約は実画面で要確認。

Confidence: `CONFIRMED-PLAY-SS`。

## 3. 誘致費用は施設価格と土地価格を分離する

SS実プレイの攻略メモでは、誘致に必要な金額は **施設の価格 + 土地の価格** と記録される。

これは新規店舗の総開業費と同様、固定施設費と時価土地費を分離すべき強い設計根拠になる。

```ts
inductionTotalCost = facilityBasePrice + landPrice
```

同じ記録では支払いは一括で、誘致は確実に成功するように見えたとされるが、成功確実性については筆者自身が「と思われる」と留保しているため固定しない。

Confidence:
- `facilityBasePrice + landPrice`: `CONFIRMED-PLAY-SS`
- one-time payment: `CONFIRMED-PLAY-SS`
- guaranteed success: `PROVISIONAL-PLAY-SS`

## 4. 大学1件の人口増加レンジ

PS上級長期プレイでは、大学を1件誘致すると **町人口が約500～800人増える** と記録される。

```text
TownBuildingDefinition[university].population_effect_observed_range = 500..800
platform = PS
```

これは初代PSの長期プレイ観測値であり、後続作の精密な施設表を輸入したものではない。

注意:
- 固定値ではなく観測レンジ。
- 「買い物人口」と「町全体人口増加」が同一概念かは未確定。
- 施設完成時に一括加算か、段階的増加かも未確定。

Confidence: `CONFIRMED-PLAY-PS / observed range`。

## 5. 誘致から完成まで時間差がある

同じPS上級長期プレイでは、大学を誘致後、完成まで **1～2か月待つ** 描写がある。

よって誘致操作と施設出現を同一tickで処理するのは原作らしくない。

```ts
TownConstructionState {
  requestedAt: GameDate;
  completionDelay: unknown;
}
```

`1～2か月` は単一プレイ記録の表現なので、固定工期ではなく存在証拠として保持する。

Confidence: `CONFIRMED-PLAY-PS` for delayed construction; exact duration `PROVISIONAL`。

## 6. コンビニコンテストの結果は賞金だけではない

PS長期プレイでは `コンビニコンテスト` による大きな資金増加・賞金受領が複数回記録される。

SS実プレイ側では、稀に発生するコンビニコンテスト等のイベントで:

- 賞金を得る
- 店長の能力が上がる

ことがあると記録される。

したがって、コンビニコンテスト/関連表彰イベントを単純な現金イベント1種に固定しない。

実装候補:

```ts
interface ContestOutcome {
  winnerStoreId: string;
  cashRewardYen?: number;
  managerStatBoost?: unknown;
}
```

未確定:
- コンテストが複数種類あるのか
- 同一コンテスト内で賞金/能力上昇が分岐するのか
- 賞金額
- 能力上昇量/対象能力
- 発生頻度/周期/応募条件
- 評価ロジック

Confidence:
- contest existence: `B+` (PS複数モード + SS)
- cash reward: `B+`
- manager ability increase in rare event context: `B`
- exact mechanics: `UNKNOWN`

## 7. ライバル店舗もコンテスト受賞対象

PS上級記録ではライバル店がコンテストで選ばれたケースがある。ロード後に結果が変わった/回避されたとの記録もある。

したがって候補集合はプレイヤー店舗限定ではない。

```ts
contestEligibleOwners = [PLAYER, RIVAL]
```

ロードによる結果変化は乱数タイミングの証拠候補だが、セーブデータに乱数状態を保存していない等の内部仕様までは断定しない。

Confidence: `CONFIRMED-PLAY-PS`。

## 8. ライバル調査で見える情報の上限

SS実プレイでは50万円のライバル店舗調査で確認できるのは、営業時間や収益など **基本情報** が中心で、ライバル店舗内部のレイアウトは見られないと明記される。

既存研究に調査費50万円はあるが、UI情報境界として以下を固定候補化する。

```text
RivalSurvey:
  visible: business_hours, earnings, other_basic_summary
  hidden: interior_layout
```

完全な表示項目は攻略本/実画面待ち。

Confidence: `CONFIRMED-PLAY-SS`。

## 9. 許可追加のUI境界を再確認

SS実プレイは `たばこ・酒・薬品` の販売許可について、**改装/改築時のみ変更でき、改装せず許可だけ取得することはできない** と記録する。

PS長期プレイの「今はタバコだけ申請し、酒・薬は中型改築時に申請する」という運用とも整合する。

したがって現時点の最有力モデルは:

```text
permitApplicationEntryPoint = store_build / remodel_flow
standalonePermitPurchaseMenu = false
```

PS/SSでUI差がないかは実画面で最終確認する。

## 10. 実装マスターへの反映優先度

今回の差分から、次のフィールドはデータモデル設計段階で先に確保してよい。

```ts
StoreState.cleanliness
FixtureDefinition.allowedZones
TownBuildingDefinition.basePrice
TownBuildingDefinition.populationEffect
TownBuildingConstruction.completionDelay
ContestDefinition.outcomeTypes
RivalSurveyDefinition.visibleFields
SalesPermitDefinition.applicationFlow
```

数値が未回収のものは `null + evidenceStatus` で保持し、続編値で埋めない。

## 11. 次の調査

攻略本/実画面で優先して回収する:

1. コンビニコンテストの正式画面・賞金額・能力上昇量・発生条件
2. 大学を含む全誘致施設の初代PS/SS価格・人口効果・サイズ
3. 誘致の工期/失敗確率
4. 清掃100の床汚れ停止をPSでもクロスチェック
5. 控え室の店外設置画面と店員経路
6. ライバル調査画面の全表示項目

## Sources

- https://mimora.mimoza.jp/yao_game/retro/contents/ctg_main/memorandum/SS/detail/gmr_SS-0001.php
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html
