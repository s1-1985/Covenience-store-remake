# 総合評価タイミングと序盤経済の追加調査 2026-09-05

対象: 1997年PS版を中心とした『ザ・コンビニ ～あの町を独占せよ～』。

目的:
- `月初に総合評価が上がる` と `オーナー評価は年1回/1月` の両証拠を矛盾として明示し、別レイヤー仮説を管理する。
- 初期の土地代、ライバル買収価格、改築費、店舗確保戦略をPS/初代専用資料だけで整理する。

---

## 1. 初代専用Wiki: 月初に総合評価が上がる

初代専用ゲームモード攻略では、上級について:

- 支店を増やす
- 人気/清掃/警備/サービスを高い状態にする
- 一定の利益を出す
- その状態で `月初` を迎えると総合評価が上がっていく
- 星4の状態で各パラメータを100にすれば星5になる
- 小型店舗でも星5にできる

と記録される。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

証拠レベル: CONFIRMED-COMMUNITY

### 重要

この記録は `総合評価` の更新タイミングを `月初` としている。

---

## 2. PS詳細実プレイ: オーナー評価が出るのは1年ごと、1月

PS版上級の詳細プレイ記録では:

- `オーナー評価が出るのは1年ごと`
- `1月が来るときに常にチェック` していればクリアを見逃さなかった
- 実際のクリアは19年目1月

と明記される。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC / DETAILED-PLAYLOG

---

## 3. 現時点では「月次内部更新」と「年次判定/表示」を分離する仮説が最も安全

両資料を同時に尊重すると、次のような構造が考えられる。

```text
MonthlyStoreEvaluation
  onMonthBoundary:
    updateStoreMetrics()
    updateAggregateScoreProgress()

AnnualOwnerEvaluation
  onYearBoundary / January:
    deriveOwnerStarsFromAggregateState()
    checkAdvancedScenarioClear()
```

これは**HYPOTHESIS**。

### なぜ分離が合理的か

- 初代Wikiは攻略観測として「月初を迎えると総合評価が上がる」としている。
- PS実プレイは「オーナー評価が出るのは1年ごと」としている。
- `調査 -> 全店収支グラフ` の星表示が随時変化するのか、年1回だけ更新されるのかはまだ直接画面で未確認。

### baseline実装方針

現時点では:

- 月次のstore/aggregate評価計算が入れられる構造
- 年次のowner rating判定を別イベントとして持てる構造

にしておき、**同じ関数へまとめない**。

PS実機で星表示の変化タイミングが確認できた段階で統合/修正する。

---

## 4. 上級の★5には全店パラメータが重要

初代専用Wikiでは上級について:

- 最終的に10店舗全てのパラメータを100にする必要がある
- 人気/清掃/警備/サービスを高く維持
- 一定利益を確保
- 星4→星5時は全パラメータ100が重要

とされる。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

ただし別PSプレイ記録では、10店舗保有前提と思い込んでいた筆者が店舗数未達と思っている最中にクリアしている。

### ここで分けるべきもの

- `10店舗保有がクリア必須` → **否定方向の証拠が強い**
- `全ての既存自社店舗について高評価が必要` → 可能性高い
- Wikiの `10店舗全て` という表現 → 攻略上10店持つ前提の記述である可能性あり

したがって実装条件を:

```text
required_store_count = 10
```

とはしない。

★5の正確な集計式は未確定。

---

## 5. ライバル支店は開始直後なら約4,500万円で買収できるという初代Wiki観測

初代専用攻略Wiki:

- ゲーム開始直後ならライバル支店を約4,500万円で買収可能
- 買収した店は初期から顧客独占率が高く、価格2倍でも客が来るケース
- 1ヶ月目から売上800万円超という例

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

証拠レベル: CONFIRMED-COMMUNITY / OBSERVATION

### 長期プレイとの比較

PS中級詳細記録では数年後に:

- 買収価格2億円
- 具体例2億1,200万円

PS上級では10年超で:

- ライバル4号店買収額2億円超
- 3億円を貯めて買収

が確認される。

Sources:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-jokyu2.html

### 結論

買収額は固定ではなく、少なくとも:

- 年数/地価
- 店舗価値
- 売上/利益
- 店舗規模

のいずれか/複数に依存して大きく変動する。

正確な式は未確定。

---

## 6. 土地インフレは非常に強い

初代専用Wiki:

- 開始時2,000万円で買えた土地
- 2年ほどで1億円超になる場所がある

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

PS中級プレイ記録:

- 中盤は安い土地 + タバコのみ + 小型店で約8,000万円と見積もる状況
- さらに後半は小型店を開くにも1億円以上必要

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

証拠レベル: CONFIRMED-COMMUNITY

### baseline上の要求

`land.price` は固定初期データではなく時間/町発展で更新される必要がある。

```text
LandParcel
- base_price
- current_price
- development_factor
- occupied_building_value
```

等に分離できる設計が必要。

正確な上昇式は未確定。

---

## 7. 小型→中型改築費1,200万円はPS詳細記録で繰り返し確認

PS中級記録:

- `中型店舗に改築するには1200万`
- `中型には1200万あればできる`

と複数箇所で明記。

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC

### 注意

これは `小型->中型の改築費` として読むのが自然だが:

- 中型新規建設費
- 大型改築費
- 外観/向き差

は別途未確定。

---

## 8. 中級での新規店舗確保競争

PS中級記録では:

- 自分5店 + ライバル5店になると、それ以上新規出店できない
- 合計10店上限
- ライバル支店が閉店した瞬間、新しい土地を確保して自店を出す競争になる
- ライバルは閉店後かなり早く別地点へ再出店する

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

証拠レベル: CONFIRMED-COMMUNITY / PS-SPECIFIC

### 実装上の意味

ワールド側には:

```text
MAX_CONVENIENCE_STORES_ON_MAP = 10  # strong evidence
```

と、ライバルAIの:

```text
onBranchClosed():
    seekNewBranchLocationAfterDelay()
```

相当が必要。

ただし再出店までの正確な待ち時間は未確定。

---

## 9. 価格15%OFFでもライバルを圧迫できるPS実例

PS中級記録:

- ターゲットライバル支店近くの自店を15%OFFに設定
- 時間経過後、対象支店が閉店
- ただしライバルは別地点へ新規出店

Source:
- https://pinkblue.sakura.ne.jp/contents/kansou/game/psgame/ps-simulation/ps-ai/ai-the-conbini-tyukyu.html

初代Wikiでも:

- 0%利益率の赤字支店で圧迫
- -20%程度でも出店ペースを遅らせられる

と記録。

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

### 結論

価格競争は単なる自店売上調整ではなく、顧客シェアを通じてライバル損益/撤退へつながる原作主要システム。

---

## 10. 初代Wikiの「改築で売上最大1.5倍程度」は攻略観測値

初代専用Wikiでは:

- 大型化/改築で品揃えが増え顧客独占率が上がる
- 売上増加は「せいぜい1.5倍程度」という攻略観測
- 店が大きいほど要求パラメータが上がる
- 清掃/警備不足や火災リスクが増す

Source:
- https://wikiwiki.jp/theconveni1/%E3%82%B2%E3%83%BC%E3%83%A0%E3%83%A2%E3%83%BC%E3%83%89%E6%94%BB%E7%95%A5

証拠レベル:
- 大型化で要求管理能力が上がる: CONFIRMED-COMMUNITY
- 売上1.5倍程度: PROVISIONAL / STRATEGY OBSERVATION

`size_multiplier = 1.5` のように式へ直接入れない。

---

## 11. 今回の実装用暫定モデル

```text
Evaluation
- monthly_store_metrics_update
- aggregate_rating_state
- annual_owner_evaluation_event
- exact relation UNKNOWN

Economy
- dynamic_land_price
- dynamic_acquisition_price
- remodel_cost_small_to_medium = 12_000_000  # PS strong evidence

World
- max_total_convenience_stores = 10
- rival_reopens_branch_after_closure
- exact reopen delay UNKNOWN
```

---

## 12. 次に解決すべき矛盾

1. `全店収支グラフ` の星が毎月変化するのか
2. 年1回の `オーナー評価` が別画面/イベントなのか
3. 上級のクリア判定は月初か年次評価時か
4. `10店舗全てのパラメータ100` は実際の必須条件か攻略上の十分条件か
5. 買収価格式
6. 土地価格の発展係数
7. 小型/中型/大型の新規建設費完全表
